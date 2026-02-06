from typing import Dict, Any


def build_agent_resource(
    *,
    agent_id: str,
    tenant_id: str | None,
    owner_tenant_id: str | None,
    visibility: str,  # GLOBAL | PRIVATE
    is_subscribed: bool,
) -> Dict[str, Any]:
    """
    Cerbos resource context for agent authorization.

    NOTE:
    - No DB calls
    - No role logic
    - All decisions come from policy
    """

    return {
        "kind": "agent",
        "id": agent_id,
        "attr": {
            # Ownership & isolation
            "tenant_id": tenant_id,                 # tenant making the request
            "owner_tenant_id": owner_tenant_id,     # tenant that owns the agent

            # Visibility
            "visibility": visibility,               # GLOBAL / PRIVATE
            "is_global": visibility == "GLOBAL",

            # Subscription
            "is_subscribed": is_subscribed,
        },
    }
