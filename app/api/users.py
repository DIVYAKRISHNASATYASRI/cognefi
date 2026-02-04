from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.schemas.user_schema import (
    UserResponse, CreateUserRequest, UpdateUserStatusRequest, UpdateUserRoleRequest
)
from app.middleware.auth import get_current_user, require_role
from app.services.clerk_service import create_clerk_user
from app.services.token_service import create_password_setup_token
from app.services.email_service import send_password_setup_email

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(
    tenant_id: str = None, 
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    # Tenant admin can only see users of their own tenant
    if current_user.role == "TENANT_ADMIN":
        if tenant_id and tenant_id != str(current_user.tenant_id):
            raise HTTPException(status_code=403, detail="Access denied to this tenant's users")
        return await db.userprofile.find_many(where={"tenant_id": str(current_user.tenant_id)})
    
    if tenant_id:
        return await db.userprofile.find_many(where={"tenant_id": tenant_id})
    return await db.userprofile.find_many()

@router.post("/")
async def create_user(
    payload: CreateUserRequest,
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    # Enforcement: Tenant admin can only create users for their own tenant
    if current_user.role == "TENANT_ADMIN" and str(payload.tenant_id) != str(current_user.tenant_id):
        raise HTTPException(status_code=403, detail="Cannot create users for another tenant")

    # Check if email exists
    existing = await db.userprofile.find_unique(where={"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    try:
        # Create in Clerk first (external API call outside DB transaction)
        clerk_user_id = await create_clerk_user(payload.email, payload.full_name)

        async with db.tx() as tx:
            # Create in DB
            user = await tx.userprofile.create(
                data={
                    "tenant_id": str(payload.tenant_id),
                    "clerk_user_id": clerk_user_id,
                    "full_name": payload.full_name,
                    "email": payload.email,
                    "role": payload.role,
                    "status": "pending"
                }
            )

            # Generate password setup token within the same transaction
            token = await create_password_setup_token(user.user_id, db_client=tx)
            
            # Send invitation email
            await send_password_setup_email(payload.email, payload.full_name, token)

            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str, 
    payload: UpdateUserStatusRequest,
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    # Check if target user belongs to same tenant or requester is super admin
    target_user = await db.userprofile.find_unique(where={"user_id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "TENANT_ADMIN" and str(target_user.tenant_id) != str(current_user.tenant_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    return await db.userprofile.update(where={"user_id": user_id}, data={"status": payload.status})

@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: str, 
    payload: UpdateUserRoleRequest,
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    # Same enforcement as status
    target_user = await db.userprofile.find_unique(where={"user_id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "TENANT_ADMIN" and str(target_user.tenant_id) != str(current_user.tenant_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    return await db.userprofile.update(where={"user_id": user_id}, data={"role": payload.role})
