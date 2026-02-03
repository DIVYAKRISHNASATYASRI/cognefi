from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    user_id: UUID
    tenant_id: Optional[UUID]
    full_name: str
    email: str
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    tenant_id: UUID
    full_name: str
    email: str
    role: str

class UpdateUserStatusRequest(BaseModel):
    status: str

class UpdateUserRoleRequest(BaseModel):
    role: str

class MeResponse(BaseModel):
    user_id: UUID
    email: str
    role: str
    tenant_id: Optional[UUID]
    tenant_name: Optional[str]