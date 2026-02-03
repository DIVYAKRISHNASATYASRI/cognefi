from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.user import UserProfile
from app.schemas.tenant import (
    TenantResponse,
    CreateTenantRequest,
    UpdateTenantRequest,
    UpdateTenantStatusRequest,
)

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/", response_model=list[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).all()


@router.post("/")
def create_tenant(
    payload: CreateTenantRequest,
    db: Session = Depends(get_db)
):
    existing = db.query(Tenant).filter(
        Tenant.tenant_code == payload.tenant_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Tenant with this tenant_code already exists"
        )

    tenant = Tenant(
        tenant_name=payload.tenant_name,
        tenant_code=payload.tenant_code,
        industry=payload.industry,
        subscription_plan=payload.subscription_plan,
        status="active"
    )

    db.add(tenant)
    db.flush()  # get tenant_id

    admin_user = UserProfile(
        tenant_id=tenant.tenant_id,
        full_name=payload.admin_name,
        email=payload.admin_email,
        role="TENANT_ADMIN",
        status="active",
        permissions={
            "manage_users": True,
            "manage_agents": True
        }
    )

    db.add(admin_user)
    db.commit()

    return {
        "tenant_id": tenant.tenant_id,
        "tenant_code": tenant.tenant_code,
        "admin_email": admin_user.email
    }


@router.patch("/{tenant_id}")
def update_tenant(
    tenant_id: UUID,
    payload: UpdateTenantRequest,
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if payload.tenant_name is not None:
        tenant.tenant_name = payload.tenant_name
    if payload.industry is not None:
        tenant.industry = payload.industry
    if payload.subscription_plan is not None:
        tenant.subscription_plan = payload.subscription_plan

    db.commit()

    return {
        "tenant_id": tenant.tenant_id,
        "tenant_name": tenant.tenant_name,
        "industry": tenant.industry,
        "subscription_plan": tenant.subscription_plan
    }


@router.patch("/{tenant_id}/status")
def update_tenant_status(
    tenant_id: UUID,
    payload: UpdateTenantStatusRequest,
    db: Session = Depends(get_db)
):
    if payload.status not in ["active", "suspended"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use 'active' or 'suspended'."
        )

    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.status = payload.status
    db.commit()

    return {
        "tenant_id": tenant.tenant_id,
        "status": tenant.status
    }
