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

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=list[TenantResponse])
async def list_tenants(current_user=Depends(require_role("SUPER_ADMIN"))):
    return await db.tenant.find_many()

@router.post("/")
async def create_tenant(
    payload: CreateTenantRequest, 
    current_user=Depends(require_role("SUPER_ADMIN"))
):
    """
    Create a new tenant and its initial admin user.
    Automatically creates a Clerk user and sends a password setup email.
    """
    # 1. Check for existing tenant code
    existing = await db.tenant.find_unique(where={"tenant_code": payload.tenant_code})
    if existing:
        raise HTTPException(status_code=400, detail="Tenant code already exists")

    # 2. Check if admin email already exists
    existing_user = await db.userprofile.find_unique(where={"email": payload.admin_email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Admin email already registered")

    try:
        # 3. Create user in Clerk first (without password)
        clerk_user_id = await create_clerk_user(payload.admin_email, payload.admin_name)
        
        async with db.tx() as tx:
            # 4. Create Tenant
            tenant = await tx.tenant.create(
                data={
                    "tenant_name": payload.tenant_name,
                    "tenant_code": payload.tenant_code,
                    "industry": payload.industry,
                    "subscription_plan": payload.subscription_plan,
                }
            )
            
            # 5. Create Admin UserProfile
            user = await tx.userprofile.create(
                data={
                    "tenant_id": tenant.tenant_id,
                    "clerk_user_id": clerk_user_id,
                    "full_name": payload.admin_name,
                    "email": payload.admin_email,
                    "role": "TENANT_ADMIN",
                    "status": "pending",  # Active after password setup
                    "permissions": Json({"manage_users": True, "manage_agents": True})
                }
            )
            
            # 6. Generate Password Setup Token
            setup_token = await create_password_setup_token(user.user_id, db_client=tx)
            
            # 7. Send Setup Email
            await send_password_setup_email(user.email, user.full_name, setup_token)
            
            return {
                "message": "Tenant and Admin created successfully. Password setup email sent.",
                "tenant_id": tenant.tenant_id,
                "tenant_code": tenant.tenant_code,
                "admin_email": user.email
            }
            
    except Exception as e:
        # If DB fails, we should ideally delete the Clerk user, but for now we log
        import logging
        logging.getLogger(__name__).error(f"Tenant creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

@router.patch("/{tenant_id}")
async def update_tenant(
    tenant_id: str, 
    payload: UpdateTenantRequest,
    current_user=Depends(require_role("SUPER_ADMIN", "TENANT_ADMIN"))
):
    # Tenant admins can only update their own tenant
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
    return await db.tenant.update(where={"tenant_id": tenant_id}, data={"status": payload.status})
