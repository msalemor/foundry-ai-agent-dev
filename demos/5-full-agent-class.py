# Pending

from services.ckvstore_service import CategoryKeyValueStore
from services.agent_service import AgentService
from azure.ai.agents.models import FunctionTool, ToolSet
from tools.tools import tools_delegate, user_functions

CLEAN_UP = True
AGENT_NAME = "full-agent-class"

if __name__ == "__main__":

    state = CategoryKeyValueStore()
    agent_id = state.get(AGENT_NAME, "agentid")

    functions = FunctionTool(functions=user_functions)
    tool_set = ToolSet()
    tool_set.add(functions)

    agent = AgentService(AGENT_NAME, toolset=tool_set, tools_delegate=tools_delegate)

    agent.create_or_reload_agent(agent_id)
    print(agent.process("user2", "What is the current time?"))

    if CLEAN_UP:
        agent.clean_up()
