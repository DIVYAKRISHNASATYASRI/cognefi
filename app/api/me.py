from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.schemas.user_schema import MeResponse
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/me", tags=["Profile"])

@router.get("/", response_model=MeResponse)
async def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id,
        "tenant_name": current_user.tenant.tenant_name if current_user.tenant else None
    }
