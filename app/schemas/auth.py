from pydantic import BaseModel
from uuid import UUID

class MeResponse(BaseModel):
    user_id: UUID
    email: str
    role: str
    tenant_id: UUID | None
    tenant_name: str | None
