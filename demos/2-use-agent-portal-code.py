# Concepts:
# - Load an existing agent and thread from the Azure AI Projects service
# - List messages in the thread (in AI Message messages are persistent)
# - Print the role and content of each message

# pip install azure-ai-projects==1.0.0b10
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# NOTE: Added the CKVStore
from services.ckvstore_service import CategoryKeyValueStore
from services.settings_service import get_settings
from services.logger_service import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":

    CATEGORY = "portal-agent"

    store = CategoryKeyValueStore()
    store.set(CATEGORY, "agentid", "asst_vSadmbuvzji9rmoGGrN5yrPg")
    store.set(CATEGORY, "threadid", "thread_O3tVMv81IoTqzNeXEiJfXLnx")

    conn_str = get_settings().connection_string
    agentid = store.get(CATEGORY, "agentid")
    threadid = store.get(CATEGORY, "threadid")

    # Get a project client
    project_client = AIProjectClient.from_connection_string(
        conn_str=conn_str, credential=DefaultAzureCredential()
    )

    # Get the agent by ID
    agent = project_client.agents.get_agent(agentid)

    # Get the thread by ID
    thread = project_client.agents.get_thread(threadid)

    # NOTE: Removed the following lines
    # message = project_client.agents.create_message(
    #     thread_id=thread.id, role="user", content="What is the speed of light?"
    # )
    # run = project_client.agents.create_and_process_run(
    #     thread_id=thread.id, agent_id=agent.id
    # )

    messages = project_client.agents.list_messages(thread_id=thread.id)

    # NOTE: Replaced the following lines
    # for text_message in messages.text_messages:
    #     print(text_message.as_dict())

    # Display the role and content of each message
    # NOTE: The first message is the last message in the thread
    for message in messages.data:
        print(message.role, message.content)
