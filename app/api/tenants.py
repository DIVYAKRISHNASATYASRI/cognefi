from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.schemas.tenant_schema import (
    TenantResponse,
    CreateTenantRequest,
    UpdateTenantRequest,
    UpdateTenantStatusRequest,
)
from prisma import Json

from app.services.cerbos_service import CerbosService
from app.services.auth_context import get_auth_context
from app.services.cerbos_resources.tenant import build_tenant_resource

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(auth=Depends(get_auth_context)):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="list",
        resource=build_tenant_resource(
            tenant_id=auth.tenant_id
        ),
    )

    return await db.tenant.find_many()


@router.post("/")
async def create_tenant(payload: CreateTenantRequest, auth=Depends(get_auth_context)):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="create",
        resource=build_tenant_resource(
            tenant_id=None
        ),
    )

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
                "permissions": Json(
                    {
                        "manage_users": True,
                        "manage_agents": True,
                    }
                ),
            }
        )

        return {
            "tenant_id": tenant.tenant_id,
            "tenant_code": tenant.tenant_code,
            "admin_email": admin.email,
        }


@router.patch("/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    payload: UpdateTenantRequest,
    auth=Depends(get_auth_context),
):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="update",
        resource=build_tenant_resource(
            tenant_id=tenant_id
        ),
    )

    data = {k: v for k, v in payload.dict().items() if v is not None}
    return await db.tenant.update(where={"tenant_id": tenant_id}, data=data)


@router.patch("/{tenant_id}/status")
async def update_tenant_status(
    tenant_id: str,
    payload: UpdateTenantStatusRequest,
    auth=Depends(get_auth_context),
):
    action = payload.status.lower()

    await CerbosService.is_allowed(
        principal=auth.principal,
        action=action,
        resource=build_tenant_resource(
            tenant_id=tenant_id,
            status=payload.status,
        ),
    )

    return await db.tenant.update(
        where={"tenant_id": tenant_id},
        data={"status": payload.status},
    )
