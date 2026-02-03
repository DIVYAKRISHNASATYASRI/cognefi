from fastapi import APIRouter, HTTPException
from app.core.db import db
from app.schemas.user_schema import (
    UserResponse, CreateUserRequest, UpdateUserStatusRequest, UpdateUserRoleRequest
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(tenant_id: str = None):
    if tenant_id:
        return await db.userprofile.find_many(where={"tenant_id": tenant_id})
    return await db.userprofile.find_many()

@router.post("/")
async def create_user(payload: CreateUserRequest):
    return await db.userprofile.create(
        data={
            "tenant_id": str(payload.tenant_id),
            "full_name": payload.full_name,
            "email": payload.email,
            "role": payload.role
        }
    )

@router.patch("/{user_id}/status")
async def update_user_status(user_id: str, payload: UpdateUserStatusRequest):
    return await db.userprofile.update(where={"user_id": user_id}, data={"status": payload.status})

@router.patch("/{user_id}/role")
async def update_user_role(user_id: str, payload: UpdateUserRoleRequest):
    return await db.userprofile.update(where={"user_id": user_id}, data={"role": payload.role})