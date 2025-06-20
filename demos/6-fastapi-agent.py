from fastapi import FastAPI
from fastapi import HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from services.ckvstore_service import CategoryKeyValueStore
from services.agent_service import AgentService
from azure.ai.agents.models import FunctionTool, ToolSet
from tools.tools import tools_delegate, user_functions

# region: FastAPI Setup
app = FastAPI()


class Request(BaseModel):
    userid: str
    prompt: str


class Response(BaseModel):
    content: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# endregion

# region: Agent setup
CLEAN_UP = True
AGENT_NAME = "api-agent-demo"

state = CategoryKeyValueStore()
agent_id = state.get(AGENT_NAME, "agentid")

functions = FunctionTool(functions=user_functions)
tool_set = ToolSet()
tool_set.add(functions)
# endregion

agent = AgentService(AGENT_NAME, toolset=tool_set, tools_delegate=tools_delegate)
agent.create_or_reload_agent(agent_id)


@app.post("/process", response_model=Response)
async def process(
    request: Request,
):
    # Call the agent and process the user's prompt
    if not request.userid or not request.prompt:
        # the user id and prompt are required
        raise HTTPException(status_code=400, detail="userid and prompt are required")

    response = str(agent.process(request.userid, request.prompt))
    return Response(content=response)


if __name__ == "__main__":
    uvicorn.run(app)
