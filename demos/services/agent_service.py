from time import sleep
from services.common import agent_cleanup
from services.settings_service import get_settings
from services.ckvstore_service import CategoryKeyValueStore
from services.logger_service import get_logger

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import Agent, ToolSet
from azure.ai.projects.models import (
    OpenAIPageableListOfThreadMessage,
    ThreadMessage,
    MessageContent,
    MessageTextContent,
)

logger = get_logger(__name__)


client_instance = None


def get_client_instance():
    global client_instance
    if not client_instance:
        client_instance = AIProjectClient.from_connection_string(
            conn_str=get_settings().connection_string,
            credential=DefaultAzureCredential(),
        )
    return client_instance


class AgentService:
    def __init__(
        self,
        name: str = "full-agent-class",
        description: str = "You are a general-purpose agent.",
        instructions: str = "You are a helpful assistant.",
        toolset: ToolSet | None = None,
        tools_delegate=None,
    ):
        self.client: AIProjectClient | None = None
        self.agent: Agent = None  # Placeholder for the agent object
        self.state: CategoryKeyValueStore = CategoryKeyValueStore()
        self.name: str = name
        self.description: str = description
        self.instructions: str = instructions
        self.toolset: ToolSet = toolset
        self.tools_delegate = tools_delegate

    def create_or_reload_agent(self, agent_id: str | None = None) -> None:
        """Create a new agent or recall an existing one."""
        self.client = get_client_instance()
        logger.info("Creating or retrieving recall agent...")
        agent_id = self.state.get(self.name, "agentid")
        if agent_id:
            self.agent = self.client.agents.get_agent(agent_id)
        else:
            self.agent = self.client.agents.create_agent(
                model="gpt-4o",
                name=self.name,
                description=self.description,
                instructions=self.instructions,
                temperature=0.1,
                toolset=self.toolset,
            )
            self.state.set(self.name, "agentid", self.agent.id)

    def reset_user_thread(self, userid: str) -> None:
        """
        Reset the thread for a specific user by removing the stored thread ID.
        """
        if self.state.exists(self.name, "thread-" + userid):
            self.state.delete(self.name, "thread-" + userid)
        else:
            logger.warning(f"No thread found for user {userid} to reset.")

        thread = self.client.agents.create_thread()
        self.state.set(self.name, "thread-" + userid, thread.id)
        logger.info(f"Thread for user {userid} has been reset.")

    def process_messages(self, messages: OpenAIPageableListOfThreadMessage) -> str:
        """
        Process a list of messages and return their responses.
        """
        text_messages: list[MessageTextContent] = messages.text_messages
        data: list[ThreadMessage] = messages.data
        message: ThreadMessage = data[0] if data else None
        content: list[MessageContent] = message.content if message else None
        response = ""
        for content_item in content:
            match content_item.type:
                case "text":
                    response += f"{content_item.text.value}\n"
                case "image_file":
                    id = content_item.image_file.file_id
                    response += f"Generated File ID: {id}.png\n"
                    self.client.agents.save_file(file_id=id, file_name=f"{id}.png")
                    response += f"File saved as {id}.png\n"
                case _:
                    return f"{str(content_item)}\n"
        return response

    def process(self, userid: str, prompt: str) -> str:
        logger.info(f"Processing prompt for user {userid}: {prompt}")

        thread = None
        if self.state.exists(self.name, "thread-" + userid):
            thread_id = self.state.get(self.name, "thread-" + userid)
            thread = self.client.agents.get_thread(thread_id)
        else:
            thread = self.client.agents.create_thread()
            self.state.set(self.name, "thread-" + userid, thread.id)

        message = self.client.agents.create_message(
            thread_id=thread.id, role="user", content=prompt
        )

        run = self.client.agents.create_run(thread_id=thread.id, agent_id=self.agent.id)
        while True:
            run = self.client.agents.get_run(thread_id=thread.id, run_id=run.id)
            logger.info(f"Agent running with status: {run.status}")
            if run.status == "completed":
                messages = self.client.agents.list_messages(thread_id=thread.id)
                return self.process_messages(messages)
            if (
                run.status == "expired"
                or run.status == "failed"
                or run.status == "cancelled"
            ):
                print("Run failed, expired or cancelled")
                return ""
            if run.status == "requires_action":
                if self.tools_delegate:
                    self.tools_delegate(self.client, thread, run)
            sleep(0.5)

    def clean_up(self):
        """Clean up the agent and its associated resources."""
        agent_cleanup(self.client, self.name, self.agent.id)
