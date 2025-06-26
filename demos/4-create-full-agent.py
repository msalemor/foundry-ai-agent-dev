# Concepts:
# - Created or recall agent
# - Added Tools, Code Interpreter, File Search

import json
from time import sleep
import uuid

import click
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    CodeInterpreterTool,
    FileSearchTool,
    FilePurpose,
    ToolSet,
    ToolResources,
    FileSearchToolResource,
    FileSearchToolDefinition,
    CodeInterpreterToolDefinition,
    CodeInterpreterToolResource,
)

from services.message_processing import process_last_messages
from tools.tools import tools_delegate, user_functions


# NOTE: Added the CKVStore
from services.ckvstore_service import CategoryKeyValueStore
from services.common import agent_cleanup, get_openai_file
from services.settings_service import get_settings
from services.logger_service import get_logger

logger = get_logger(__name__)


store = CategoryKeyValueStore()
AGENT_NAME = "full-agent"
CLEANUP = True


project_client = AIProjectClient.from_connection_string(
    conn_str=get_settings().connection_string, credential=DefaultAzureCredential()
)


# Adding tools
functions = FunctionTool(functions=user_functions)

# Code interpreter tool
file_path = "demos/data/failed_banks.csv"
code_file = get_openai_file(project_client, file_path)
if code_file:
    store.set(AGENT_NAME, "file-" + str(uuid.uuid4())[:8], code_file.id)
code_interpreter = CodeInterpreterTool(file_ids=[code_file.id])

# Adding File search
# Define the path to the file to be uploaded
file_path = "demos/data/faq.md"
file = get_openai_file(project_client, file_path)
if file:
    store.set(AGENT_NAME, "file-" + str(uuid.uuid4())[:8], file.id)
vector_store = project_client.agents.create_vector_store_and_poll(
    data_sources=[], name="sample_vector_store", file_ids=[file.id]
)
# # Create a vector store with the uploaded file
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

tool_set = ToolSet()
tool_set.add(functions)
tool_set.add(code_interpreter)
# Add file search tool if file is successfully uploaded
tool_set.add(file_search)


def create_recall_agent() -> any:
    logger.info("Creating or retrieving recall agent...")
    agent = None
    agent_id = store.get(AGENT_NAME, "agentid")
    if agent_id:
        agent = project_client.agents.get_agent(agent_id)
    else:
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name=AGENT_NAME,
            description="A simple agent for demonstration purposes.",
            instructions="You are a helpful assistant.",
            temperature=0.1,
            toolset=tool_set,
        )
        store.set(AGENT_NAME, "agentid", agent.id)
    return agent


agent = create_recall_agent()


def process(userid: str, prompt: str) -> str:
    logger.info(f"Processing prompt for user {userid}: {prompt}")

    thread = None
    if store.exists(AGENT_NAME, "thread-" + userid):
        thread_id = store.get(AGENT_NAME, "thread-" + userid)
        thread = project_client.agents.get_thread(thread_id)
    else:
        thread = project_client.agents.create_thread()
        store.set(AGENT_NAME, "thread-" + userid, thread.id)

    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content=prompt
    )

    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
    while True:
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        logger.info(f"Agent running with status: {run.status}")
        if run.status == "completed":
            messages = project_client.agents.list_messages(thread_id=thread.id)
            # return messages.data[0].content if messages else "No response"
            return process_last_messages(project_client, messages)
        if (
            run.status == "expired"
            or run.status == "failed"
            or run.status == "cancelled"
        ):
            print("Run failed, expired or cancelled")
            return ""
        if run.status == "requires_action":
            tools_delegate(project_client, thread, run)
        sleep(0.5)

    # run = project_client.agents.create_and_process_run(
    #     thread_id=thread.id, agent_id=agent.id
    # )
    # Assuming the response is in the first message of the run

    return ""


if __name__ == "__main__":

    # click.echo(
    #     click.style(
    #         process(
    #             "user1", "What is the current time? What is the weather in New York?"
    #         ),
    #         fg="green",
    #     )
    # )
    # click.echo(
    #     click.style(
    #         process("user1", "What are the company values?"),
    #         fg="green",
    #     )
    # )
    # click.echo(
    #     click.style(
    #         process("user1", "What is the 1001st prime number?"),
    #         fg="green",
    #     )
    # )
    click.echo(
        click.style(
            process("user1", "Generate a chart of y=x^3 where x=[-5,5]?"),
            fg="green",
        )
    )
    # print(process("user2", "What is the capital of Germany?"))

    if CLEANUP:
        agent_cleanup(project_client, AGENT_NAME, agent.id)
