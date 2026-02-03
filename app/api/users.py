from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.models.user import UserProfile
from app.models.tenant import Tenant
from app.schemas.user import (
    UserResponse,
    CreateUserRequest,
    UpdateUserStatusRequest,
    UpdateUserRoleRequest,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    tenant_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    query = db.query(UserProfile)

    if tenant_id:
        query = query.filter(UserProfile.tenant_id == tenant_id)

    return query.all()


@router.post("/")
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == payload.tenant_id
    ).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    existing = db.query(UserProfile).filter(
        UserProfile.email == payload.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    user = UserProfile(
        tenant_id=payload.tenant_id,
        full_name=payload.full_name,
        email=payload.email,
        role=payload.role,
        status="active",
        permissions={}
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id
    }


@router.patch("/{user_id}/status")
def update_user_status(
    user_id: UUID,
    payload: UpdateUserStatusRequest,
    db: Session = Depends(get_db)
):
    if payload.status not in ["active", "disabled"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use 'active' or 'disabled'."
        )

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = payload.status
    db.commit()

    return {
        "user_id": user.user_id,
        "status": user.status
    }


@router.patch("/{user_id}")
def update_user_role(
    user_id: UUID,
    payload: UpdateUserRoleRequest,
    db: Session = Depends(get_db)
):
    if payload.role not in ["USER", "TENANT_ADMIN"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Use 'USER' or 'TENANT_ADMIN'."
        )

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()

    return {
        "user_id": user.user_id,
        "role": user.role
    }
