from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.schemas.user_schema import (
    UserResponse,
    CreateUserRequest,
    UpdateUserStatusRequest,
    UpdateUserRoleRequest,
)
from app.services.cerbos_service import CerbosService
from app.services.auth_context import get_auth_context
from app.services.cerbos_resources.user import build_user_resource

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(tenant_id: str | None = None, auth=Depends(get_auth_context)):
    await CerbosService.is_allowed(
        principal=auth.principal,
        action="list",
        resource=build_user_resource(
            tenant_id=auth.tenant_id
        ),
    )

    if tenant_id:
        return await db.userprofile.find_many(where={"tenant_id": tenant_id})

    return await db.userprofile.find_many(where={"tenant_id": auth.tenant_id})


@router.post("/")
async def create_user(
    payload: CreateUserRequest,
    auth=Depends(get_auth_context),
):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="create",
        resource=build_user_resource(
            tenant_id=payload.tenant_id
        ),
    )

    return await db.userprofile.create(
        data={
            "tenant_id": str(payload.tenant_id),
            "full_name": payload.full_name,
            "email": payload.email,
            "role": payload.role,
        }
    )


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str,
    payload: UpdateUserStatusRequest,
    auth=Depends(get_auth_context),
):

    user = await db.userprofile.find_unique(where={"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="update_status",
        resource=build_user_resource(
            tenant_id=user.tenant_id,
            user_id=user_id,
            status=payload.status,
        ),
    )

    return await db.userprofile.update(
        where={"user_id": user_id},
        data={"status": payload.status},
    )


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    auth=Depends(get_auth_context),
):

    user = await db.userprofile.find_unique(where={"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="update_role",
        resource=build_user_resource(
            tenant_id=user.tenant_id,
            user_id=user_id,
            role=payload.role,
        ),
    )

    return await db.userprofile.update(
        where={"user_id": user_id},
        data={"role": payload.role},
    )
