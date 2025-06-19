import json

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AgentThread, ThreadRun
from tools.email_tool import mock_send_email
from tools.time_tool import current_time
from tools.weather_tool import fetch_weather
from services.logger_service import get_logger

logger = get_logger(__name__)

user_functions = {fetch_weather, current_time, mock_send_email}


def tools_delegate(client: AIProjectClient, thread: AgentThread, run: ThreadRun):
    logger.info(
        f"Delegating tools for thread {thread.id} and run {run.id} with required action: {run.required_action}"
    )
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool_call in tool_calls:
        if tool_call.function.name == "fetch_weather":
            location = json.loads(tool_call.function.arguments)["location"]
            output = fetch_weather(location)
            tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
        if tool_call.function.name == "current_time":
            output = current_time()
            tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

    client.agents.submit_tool_outputs_to_run(
        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
    )
