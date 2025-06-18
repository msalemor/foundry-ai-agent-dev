from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import uvicorn

app = FastAPI(title="Agent Prompt Manager API")


# Data models
class PromptRequest(BaseModel):
    content: str
    agent_id: Optional[str] = None
    context: Optional[dict] = None


class PromptResponse(BaseModel):
    id: str
    content: str
    agent_id: Optional[str]
    context: Optional[dict]
    created_at: datetime
    status: str = "pending"


# In-memory storage (replace with database in production)
prompts_db = {}


@app.post("/prompts", response_model=PromptResponse)
async def create_prompt(prompt: PromptRequest):
    """Create a new agent prompt"""
    prompt_id = str(uuid.uuid4())
    prompt_data = PromptResponse(
        id=prompt_id,
        content=prompt.content,
        agent_id=prompt.agent_id,
        context=prompt.context,
        created_at=datetime.now(),
        status="pending",
    )
    prompts_db[prompt_id] = prompt_data
    return prompt_data


@app.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str):
    """Get a specific prompt by ID"""
    if prompt_id not in prompts_db:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts_db[prompt_id]


@app.get("/prompts", response_model=List[PromptResponse])
async def list_prompts(agent_id: Optional[str] = None):
    """List all prompts, optionally filtered by agent_id"""
    prompts = list(prompts_db.values())
    if agent_id:
        prompts = [p for p in prompts if p.agent_id == agent_id]
    return prompts


@app.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Delete a prompt"""
    if prompt_id not in prompts_db:
        raise HTTPException(status_code=404, detail="Prompt not found")
    del prompts_db[prompt_id]
    return {"message": "Prompt deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
