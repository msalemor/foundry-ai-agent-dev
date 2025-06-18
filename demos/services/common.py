from ckvstore_service import CategoryKeyValueStore
from logger_service import get_logger

logger = get_logger(__name__)
store = CategoryKeyValueStore()


def agent_cleanup(client, category: str, agent_id: str) -> None:

    items = store.get_category(category)
    if items:
        for key in items.keys():
            if key.startswith("thread-"):
                logger.info(f"Deleting thread for key: {key}")
                thread_id = items[key]
                try:
                    client.agents.delete_thread(thread_id)
                    store.delete(category, key)
                except Exception as e:
                    logger.exception(f"Error deleting thread {thread_id}: {e}")

    if agent_id:
        try:
            logger.info(f"Deleting agent with ID: {agent_id}")
            client.agents.delete_agent(agent_id)
            store.delete(category, "agentid")
        except Exception as e:
            logger.exception(f"Error deleting agent {agent_id}: {e}")

    logger.info(f"Deleting category: {category}")
    store.delete_category(category)
