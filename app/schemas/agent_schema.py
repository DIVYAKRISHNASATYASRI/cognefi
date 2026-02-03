from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

# Tenant Schemas
class CreateTenantRequest(BaseModel):
    tenant_name: str
    tenant_code: str
    industry: Optional[str] = None
    subscription_plan: str = "free"
    admin_name: str
    admin_email: str

class UpdateTenantRequest(BaseModel):
    tenant_name: Optional[str] = None
    industry: Optional[str] = None
    subscription_plan: Optional[str] = None

# User Schemas
class CreateUserRequest(BaseModel):
    tenant_id: UUID
    full_name: str
    email: str
    role: str

# Agent Schemas
class AgentCreate(BaseModel):
    tenant_id: Optional[str] = None 
    created_by: str
    agent_name: str
    description: Optional[str] = None
    access_type: str = "PRIVATE" 
    is_public: bool = False
    model_provider: str = "openai"
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    instructions: str
    system_message: Optional[str] = "You are a helpful assistant."
    markdown: bool = True

class AgentUpdate(BaseModel):
    agent_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    instructions: Optional[str] = None
    system_message: Optional[str] = None

class AgentRunRequest(BaseModel):
    user_id: str
    tenant_id: str
    message: str

class AgentSubscribe(BaseModel):
    user_id: str
    agent_id: str