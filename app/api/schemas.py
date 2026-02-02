from pydantic import BaseModel
from typing import Optional

class AgentCreate(BaseModel):
    tenant_id: Optional[str] = None # Null for Global
    created_by: str
    agent_name: str
    description: Optional[str] = None
    access_type: str = "PRIVATE" # GLOBAL or PRIVATE
    is_public: bool = False
    model_provider: str = "openai"
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    instructions: str
    system_message: Optional[str] = "You are a helpful assistant."

class AgentSubscribe(BaseModel):
    user_id: str
    agent_id: str

class AgentRunRequest(BaseModel):
    user_id: str
    tenant_id: str
    message: str

class AgentUpdate(BaseModel):
    agent_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    # Model Updates
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    # Prompt Updates
    instructions: Optional[str] = None
    system_message: Optional[str] = None
    # Ops Updates
    markdown: Optional[bool] = None