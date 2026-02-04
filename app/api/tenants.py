from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.schemas.tenant_schema import (
    TenantResponse, CreateTenantRequest, UpdateTenantRequest, UpdateTenantStatusRequest
)
from app.middleware.auth import get_current_user, require_role
from prisma import Json
from app.services.clerk_service import create_clerk_user
from app.services.email_service import send_password_setup_email
from app.services.token_service import create_password_setup_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=list[TenantResponse])
async def list_tenants(current_user=Depends(require_role("SUPER_ADMIN"))):
    """List all tenants - restricted to Super Admins."""
    return await db.tenant.find_many(order={"created_at": "desc"})

@router.post("/")
async def create_tenant(
    payload: CreateTenantRequest, 
    current_user=Depends(require_role("SUPER_ADMIN"))
):
    """
    1. Checks if Tenant/User exists.
    2. Creates User in Clerk Cloud.
    3. Creates Tenant & User in Local DB.
    4. Sends Activation Email.
    """
    # Check for existing tenant code
    existing_tenant = await db.tenant.find_unique(where={"tenant_code": payload.tenant_code})
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant code already exists")

    # Check for existing user email
    existing_user = await db.userprofile.find_unique(where={"email": payload.admin_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Admin email already registered")

    try:
        # Create user in Clerk first
        clerk_user_id = await create_clerk_user(payload.admin_email, payload.admin_name)
        
        async with db.tx() as tx:
            # Create Tenant
            tenant = await tx.tenant.create(
                data={
                    "tenant_name": payload.tenant_name,
                    "tenant_code": payload.tenant_code,
                    "industry": payload.industry,
                    "subscription_plan": payload.subscription_plan,
                }
            )
            
            # Create Admin UserProfile linked to Clerk
            user = await tx.userprofile.create(
                data={
                    "tenant_id": tenant.tenant_id,
                    "clerk_user_id": clerk_user_id,
                    "full_name": payload.admin_name,
                    "email": payload.admin_email,
                    "role": "TENANT_ADMIN",
                    "status": "pending", # Pending until password set
                    "permissions": Json({"manage_users": True, "manage_agents": True})
                }
            )
            
            # Generate Setup Token for the invitation email
            setup_token = await create_password_setup_token(user.user_id, db_client=tx)
            
            # Send Email (SMTP)
            await send_password_setup_email(user.email, user.full_name, setup_token)
            
            return {
                "message": "Tenant created and invitation sent.",
                "tenant_id": tenant.tenant_id,
                "admin_email": user.email
            }
            
    except Exception as e:
        logger.error(f"Tenant creation flow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

@router.patch("/{tenant_id}")
async def update_tenant(
    tenant_id: str, 
    payload: UpdateTenantRequest,
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    """Update tenant details. Tenant Admins can only update their own."""
    if current_user.role == "TENANT_ADMIN" and str(current_user.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this tenant")

    data = {k: v for k, v in payload.dict().items() if v is not None}
    return await db.tenant.update(where={"tenant_id": tenant_id}, data=data)

@router.patch("/{tenant_id}/status")
async def update_tenant_status(
    tenant_id: str, 
    payload: UpdateTenantStatusRequest,
    current_user=Depends(require_role("SUPER_ADMIN"))
):
    """Suspend or Activate a tenant - Super Admin only."""
    if payload.status not in ["active", "suspended"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    return await db.tenant.update(where={"tenant_id": tenant_id}, data={"status": payload.status})