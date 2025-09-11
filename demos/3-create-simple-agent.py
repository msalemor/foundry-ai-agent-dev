# Concepts:
# - Create a simple agent or reload
# - Handle threads, messages and runs for different users
# - Implement a cleanup function to remove agents and threads


from time import sleep
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

import click

# NOTE: Added the CKVStore
# from services.message_processing import process_last_message
from services.ckvstore_service import CategoryKeyValueStore
from services.common import agent_cleanup
from services.settings_service import get_settings
from services.logger_service import get_logger

logger = get_logger(__name__)


store = CategoryKeyValueStore()
AGENT_NAME = "simple-agent"
CLEANUP = False


project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=get_settings().endpoint,
)


def create_recall_agent() -> any:
    logger.info("Creating or retrieving recall agent...")
    agent = None
    agent_id = store.get(AGENT_NAME, "agent_id")
    if agent_id:
        agent = project_client.agents.get_agent(agent_id)
    else:
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name=AGENT_NAME,
            description="A simple agent for demonstration purposes.",
            instructions="You are a helpful assistant.",
            temperature=0.1,
        )
        store.set(AGENT_NAME, "agent_id", agent.id)
    return agent


agent = create_recall_agent()


def process(user_id: str, prompt: str) -> str:
    logger.info(f"Processing prompt for user {user_id}: {prompt}")

    thread = None
    if store.exists(AGENT_NAME, "thread-" + user_id):
        thread_id = store.get(AGENT_NAME, "thread-" + user_id)
        thread = project_client.agents.threads.get(thread_id)
    else:
        thread = project_client.agents.threads.create()
        store.set(AGENT_NAME, "thread-" + user_id, thread.id)

    message = project_client.agents.messages.create(
        thread_id=thread.id, role="user", content=prompt
    )

    run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
    while True:
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        logger.info(f"Agent running with status: {run.status}")
        if run.status == "completed":
            messages = project_client.agents.messages.list(thread_id=thread.id)
            # return process_last_message(project_client, messages)
            # return messages.data[0].content if messages else "No response"
            for message in messages:
                print(message.content[0].text.value)
            return
        if (
            run.status == "expired"
            or run.status == "failed"
            or run.status == "cancelled"
        ):
            print("Run failed, expired or cancelled")
            return ""
        if run.status == "requires_action":
            print("Run requires action, retrying...")
            return ""
        sleep(0.5)

    # run = project_client.agents.create_and_process_run(
    #     thread_id=thread.id, agent_id=agent.id
    # )
    # Assuming the response is in the first message of the run

    return ""


if __name__ == "__main__":

    click.echo(
        click.style(process("user1", "What is the capital of France?"), fg="green")
    )
    click.echo(
        click.style(process("user2", "What is the capital of Germany?"), fg="green")
    )
    click.echo(
        click.style(
            process("user2", "Generate a graph of y=x^2 where x=[-2,2]"), fg="green"
        )
    )

    if CLEANUP:
        agent_cleanup(project_client, AGENT_NAME, agent.id)
