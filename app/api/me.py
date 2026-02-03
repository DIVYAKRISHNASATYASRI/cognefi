from fastapi import APIRouter, HTTPException
from app.core.db import db
from app.schemas.user_schema import MeResponse

router = APIRouter(prefix="/me", tags=["Profile"])

@router.get("/{user_id}", response_model=MeResponse)
async def get_my_profile(user_id: str):
    user = await db.userprofile.find_unique(
        where={"user_id": user_id},
        include={"tenant": True}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "tenant_name": user.tenant.tenant_name if user.tenant else None
    }