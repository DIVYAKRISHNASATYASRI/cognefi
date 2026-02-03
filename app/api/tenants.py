from fastapi import APIRouter, HTTPException
from app.core.db import db
from app.schemas.tenant_schema import (
    TenantResponse, CreateTenantRequest, UpdateTenantRequest, UpdateTenantStatusRequest
)
from prisma import Json

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=list[TenantResponse])
async def list_tenants():
    return await db.tenant.find_many()

@router.post("/")
async def create_tenant(payload: CreateTenantRequest):
    existing = await db.tenant.find_unique(where={"tenant_code": payload.tenant_code})
    if existing:
        raise HTTPException(status_code=400, detail="Tenant code already exists")

    async with db.tx() as tx:
        tenant = await tx.tenant.create(
            data={
                "tenant_name": payload.tenant_name,
                "tenant_code": payload.tenant_code,
                "industry": payload.industry,
                "subscription_plan": payload.subscription_plan,
            }
        )
        admin = await tx.userprofile.create(
            data={
                "tenant_id": tenant.tenant_id,
                "full_name": payload.admin_name,
                "email": payload.admin_email,
                "role": "TENANT_ADMIN",
                "permissions": Json({"manage_users": True, "manage_agents": True})
            }
        )
        return {"tenant_id": tenant.tenant_id, "tenant_code": tenant.tenant_code, "admin_email": admin.email}

@router.patch("/{tenant_id}")
async def update_tenant(tenant_id: str, payload: UpdateTenantRequest):
    data = {k: v for k, v in payload.dict().items() if v is not None}
    return await db.tenant.update(where={"tenant_id": tenant_id}, data=data)

@router.patch("/{tenant_id}/status")
async def update_tenant_status(tenant_id: str, payload: UpdateTenantStatusRequest):
    return await db.tenant.update(where={"tenant_id": tenant_id}, data={"status": payload.status})