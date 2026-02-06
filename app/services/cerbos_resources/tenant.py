from typing import Dict, Any


def build_tenant_resource(
    *,
    tenant_id: str,
    status: str | None = None,
    is_global: bool = False,
) -> Dict[str, Any]:
    """
    Build Cerbos resource context for a tenant.

    IMPORTANT:
    - This function must be PURE (no DB calls)
    - Lifecycle enforcement happens via derived roles (principal attributes)
    """

    return {
        "kind": "tenant",
        "id": tenant_id,
        "attr": {
            "tenant_id": tenant_id,
            "status": status,
            "is_global": is_global,
        },
    }
