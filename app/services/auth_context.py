# app/services/auth_context.py

from typing import Dict, Any
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.core.db import db


class AuthContext(BaseModel):
    """
    Canonical authentication context.

    This is the SINGLE source of truth for:
    - API authorization
    - Cerbos principal construction
    - Future Clerk integration
    """

    user_id: str
    tenant_id: str
    role: str

    user_status: str
    tenant_status: str

    principal: Dict[str, Any]


async def get_auth_context(
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    """
    Mock authentication provider.

    Reads identity from headers and database.
    Produces a Cerbos-compatible principal.

    This function will later be replaced by Clerk,
    without changing ANY API or Cerbos code.
    """

    # ---- Load user ----
    user = await db.userprofile.find_unique(
        where={"user_id": x_user_id},
        include={"tenant": True},
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )

    # ---- Build principal for Cerbos ----
    principal = {
        "id": str(user.user_id),
        "roles": [user.role.lower()],  # e.g. super_admin, tenant_admin, user
        "attr": {
            "tenant_id": str(user.tenant_id),
            "user_status": user.status,
            "tenant_status": user.tenant.status,
        },
    }

    return AuthContext(
        user_id=str(user.user_id),
        tenant_id=str(user.tenant_id),
        role=user.role,
        user_status=user.status,
        tenant_status=user.tenant.status,
        principal=principal,
    )
