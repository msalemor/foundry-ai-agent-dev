# Concepts:
# - Create a simple agent or reload
# - Handle threads, messages and runs for different users
# - Implement a cleanup function to remove agents and threads


import json
from time import sleep
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool

# NOTE: Added the CKVStore
from ckvstore import CategoryKeyValueStore
from common import agent_cleanup
from settings import get_settings
from logger import get_logger

logger = get_logger(__name__)


store = CategoryKeyValueStore()
CATEGORY = "simple-agent"
CLEANUP = False


project_client = AIProjectClient.from_connection_string(
    conn_str=get_settings().connection_string, credential=DefaultAzureCredential()
)


def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location: The location to fetch weather for.
    :return: Weather information as a JSON string.
    """
    # Mock weather data for demonstration purposes
    mock_weather_data = {
        "New York": "Sunny, 25°C",
        "London": "Cloudy, 18°C",
        "Tokyo": "Rainy, 22°C",
    }
    weather = mock_weather_data.get(
        location, "Weather data not available for this location."
    )
    return json.dumps({"weather": weather})


# Define user functions
user_functions = {fetch_weather}


def create_recall_agent() -> any:
    logger.info("Creating or retrieving recall agent...")
    agent = None
    agent_id = store.get(CATEGORY, "agentid")
    if agent_id:
        agent = project_client.agents.get_agent(agent_id)
    else:
        functions = FunctionTool(functions=user_functions)
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="Simple Agent",
            description="A simple agent for demonstration purposes.",
            instructions="You are a helpful assistant.",
            temperature=0.1,
            tools=functions.definitions,
        )
        store.set(CATEGORY, "agentid", agent.id)
    return agent


agent = create_recall_agent()


def process(userid: str, prompt: str) -> str:
    logger.info(f"Processing prompt for user {userid}: {prompt}")

    thread = None
    if store.exists(CATEGORY, "thread-" + userid):
        thread_id = store.get(CATEGORY, "thread-" + userid)
        thread = project_client.agents.get_thread(thread_id)
    else:
        thread = project_client.agents.create_thread()
        store.set(CATEGORY, "thread-" + userid, thread.id)

    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content=prompt
    )

    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
    while True:
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        logger.info(f"Agent running with status: {run.status}")
        if run.status == "completed":
            messages = project_client.agents.list_messages(thread_id=thread.id)
            return messages.data[0].content if messages else "No response"
        if run.status == "expired" or run.status == "failed":
            print("Run expired")
            return ""
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call.name == "fetch_weather":
                    output = fetch_weather("New York")
                    tool_outputs.append(
                        {"tool_call_id": tool_call.id, "output": output}
                    )
            project_client.agents.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
            )
        sleep(0.5)

    # run = project_client.agents.create_and_process_run(
    #     thread_id=thread.id, agent_id=agent.id
    # )
    # Assuming the response is in the first message of the run

    return ""


if __name__ == "__main__":

    print(process("user1", "What is the capital of France?"))
    print(process("user2", "What is the capital of Germany?"))

    if CLEANUP:
        agent_cleanup(project_client, CATEGORY, agent.id)
