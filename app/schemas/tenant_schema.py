from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TenantResponse(BaseModel):
    tenant_id: UUID
    tenant_name: str
    tenant_code: str
    industry: str | None
    subscription_plan: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateTenantRequest(BaseModel):
    tenant_name: str
    tenant_code: str
    industry: str | None = None
    subscription_plan: str = "free"
    admin_name: str
    admin_email: str


class UpdateTenantRequest(BaseModel):
    tenant_name: str | None = None
    industry: str | None = None
    subscription_plan: str | None = None


class UpdateTenantStatusRequest(BaseModel):
    status: str
