from typing import Dict, Any, Optional
import logging

from fastapi import HTTPException, status

from cerbos.sdk.model import Principal, Resource
from cerbos.sdk.grpc.client import CerbosClient as GrpcCerbosClient
from cerbos.sdk.model import CheckResourcesRequest


class CerbosService:
    """
    Single abstraction layer for all Cerbos authorization checks.

    This class is the ONLY place where:
    - Cerbos SDK is used
    - Authorization decisions are enforced
    """

    _client: Optional[GrpcCerbosClient] = None

    @classmethod
    def _get_client(cls) -> GrpcCerbosClient:
        """
        Lazy-initialize Cerbos gRPC client.
        """
        if cls._client is None:
            cls._client = GrpcCerbosClient(
                target="localhost:3593",
                tls=False  # plaintext as per current setup
            )
        return cls._client

    @classmethod
    async def is_allowed(
        cls,
        *,
        principal: Dict[str, Any],
        resource: Dict[str, Any],
        action: str,
    ) -> bool:
        """
        Ask Cerbos whether the given principal can perform an action on a resource.

        Enforcement rules:
        - EFFECT_ALLOW  -> continue execution
        - EFFECT_DENY   -> HTTP 403
        - Any error     -> HTTP 403 (fail-closed)

        Returns:
            True if allowed (execution continues)

        Raises:
            HTTPException(403) if denied or Cerbos fails
        """

        try:
            client = cls._get_client()

            cerbos_principal = Principal(
                id=principal["id"],
                roles=principal.get("roles", []),
                attr=principal.get("attr", {}),
            )

            cerbos_resource = Resource(
                kind=resource["kind"],
                id=resource["id"],
                attr=resource.get("attr", {}),
            )

            request = CheckResourcesRequest(
                principal=cerbos_principal,
                resources=[
                    {
                        "resource": cerbos_resource,
                        "actions": [action],
                    }
                ],
            )

            response = client.check_resources(request)

            result = response.results[0]
            decision = result.actions[action]

            if decision != "EFFECT_ALLOW":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied by authorization policy",
                )

            return True

        except HTTPException:
            # Explicit deny → propagate
            raise

        except Exception:
            # Any Cerbos / network / serialization error
            logging.exception("Cerbos authorization failed")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization service unavailable",
            )
