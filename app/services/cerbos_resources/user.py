from typing import Dict, Any


def build_user_resource(
    *,
    user_id: str,
    tenant_id: str,
    principal_user_id: str,
    is_super_admin: bool = False,
) -> Dict[str, Any]:
    """
    Build Cerbos resource context for a user.

    Rules:
    - User identity comparisons are explicit
    - No DB calls
    - No role inference
    """

    return {
        "kind": "user",
        "id": user_id,
        "attr": {
            "tenant_id": tenant_id,
            "is_self": user_id == principal_user_id,
            "is_super_admin": is_super_admin,
        },
    }
