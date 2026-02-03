from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.user import UserProfile
from app.models.tenant import Tenant
from app.schemas.auth import MeResponse

router = APIRouter(tags=["Auth"])


@router.get("/me", response_model=MeResponse)
def get_me(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tenant_name = None
    if user.tenant_id:
        tenant = db.query(Tenant).filter(
            Tenant.tenant_id == user.tenant_id
        ).first()
        tenant_name = tenant.tenant_name if tenant else None

    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "tenant_name": tenant_name
    }
