# Objective:
# - Showcase using loading an agent, loading a thread, and listing the messages for a pre-provision Agent

# Fundamentals:
# - Load an existing agent and thread from the Azure AI Projects service
# - List messages in the thread (in AI Message messages are persistent)
# - Print the role and content of each message

# pip install azure-ai-projects==1.0.0b10
import click
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# NOTE: Added the CKVStore
from services.ckvstore_service import CategoryKeyValueStore
from services.settings_service import get_settings
from services.logger_service import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":

    AGENT_NAME = "portal-agent"

    store = CategoryKeyValueStore()
    store.set(AGENT_NAME, "agent_id", "asst_O7kmJzvx0IQxVpZ3fpuTsAac")
    store.set(AGENT_NAME, "thread_id", "thread_o3YosvSY559DDuNRP5xOhSDA")

    conn_str = get_settings().connection_string
    agent_id = store.get(AGENT_NAME, "agent_id")
    thread_id = store.get(AGENT_NAME, "thread_id")

    # Get a project client
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=get_settings().endpoint,
    )

    # Get the agent by ID
    agent = project_client.agents.get_agent(agent_id)

    # Get the thread by ID
    thread = project_client.agents.threads.get(thread_id)

    # NOTE: Removed the following lines
    # message = project_client.agents.create_message(
    #     thread_id=thread.id, role="user", content="What is the speed of light?"
    # )
    # run = project_client.agents.create_and_process_run(
    #     thread_id=thread.id, agent_id=agent.id
    # )

    messages = project_client.agents.messages.list(thread_id=thread.id)

    # NOTE: Replaced the following lines
    # for text_message in messages.text_messages:
    #     print(text_message.as_dict())

    # Display the role and content of each message
    # NOTE: The first message is the last message in the thread
    for message in messages:
        click.echo(
            click.style(f"{message.role}, {message.content[0].text.value}", fg="green")
        )
