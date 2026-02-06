from fastapi import APIRouter, HTTPException, Depends, Body
from app.services.agentrunner import run_agent_secured
from app.services.agent_service import AgentService
from app.schemas.agent_schema import (
    AgentCreate,
    AgentSubscribe,
    AgentRunRequest,
    AgentUpdate,
)
from app.core.db import db
from app.services.cerbos_service import CerbosService
from app.services.auth_context import get_auth_context
from app.services.cerbos_resources.agent import build_agent_resource

router = APIRouter()


@router.get("/marketplace")
async def get_marketplace(auth=Depends(get_auth_context)):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="list_marketplace",
        resource=build_agent_resource(),
    )

    return await AgentService.get_marketplace()


@router.post("/agents")
async def create_agent_endpoint(
    payload: AgentCreate,
    auth=Depends(get_auth_context),
):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="create",
        resource=build_agent_resource(
            access_type=payload.access_type,
            tenant_id=payload.tenant_id,
        ),
    )

    if payload.access_type == "GLOBAL" and payload.tenant_id is not None:
        payload.tenant_id = None

    try:
        new_agent = await AgentService.create_agent(payload)
        return {
            "status": "success",
            "message": f"Agent {new_agent.agent_name} created successfully",
            "agent_id": new_agent.agent_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Creation failed: {str(e)}")


@router.post("/subscribe")
async def subscribe(
    payload: AgentSubscribe,
    auth=Depends(get_auth_context),
):

    agent = await db.agent.find_unique(where={"agent_id": payload.agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="subscribe",
        resource=build_agent_resource(
            agent_id=agent.agent_id,
            access_type=agent.access_type,
            tenant_id=agent.tenant_id,
        ),
    )

    try:
        return await db.agentsubscription.create(
            data={
                "user_id": payload.user_id,
                "agent_id": payload.agent_id,
            }
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Already subscribed")


@router.get("/my-agents/{user_id}/{tenant_id}")
async def my_agents(
    user_id: str,
    tenant_id: str,
    auth=Depends(get_auth_context),
):

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="list_my_agents",
        resource=build_agent_resource(
            tenant_id=tenant_id,
            user_id=user_id,
        ),
    )

    return await AgentService.get_my_agents(user_id, tenant_id)


@router.post("/run/{agent_id}")
async def run_agent_endpoint(
    agent_id: str,
    payload: AgentRunRequest,
    auth=Depends(get_auth_context),
):

    agent = await db.agent.find_unique(where={"agent_id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="run",
        resource=build_agent_resource(
            agent_id=agent.agent_id,
            tenant_id=payload.tenant_id,
            access_type=agent.access_type,
        ),
    )

    try:
        content = await run_agent_secured(
            agent_id,
            payload.user_id,
            payload.tenant_id,
            payload.message,
        )
        return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/agents/{agent_id}")
async def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    auth=Depends(get_auth_context),
):

    agent = await db.agent.find_unique(where={"agent_id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="update",
        resource=build_agent_resource(
            agent_id=agent.agent_id,
            tenant_id=agent.tenant_id,
            access_type=agent.access_type,
        ),
    )

    try:
        updated_agent = await AgentService.update_agent(agent_id, payload)
        return {"status": "success", "data": updated_agent}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    auth=Depends(get_auth_context),
):

    agent = await db.agent.find_unique(where={"agent_id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="delete",
        resource=build_agent_resource(
            agent_id=agent.agent_id,
            tenant_id=agent.tenant_id,
            access_type=agent.access_type,
        ),
    )

    try:
        await AgentService.delete_agent(agent_id)
        return {
            "status": "success",
            "message": f"Agent {agent_id} and all related configs deleted.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")


@router.delete("/unsubscribe/{user_id}/{agent_id}")
async def unsubscribe(
    user_id: str,
    agent_id: str,
    auth=Depends(get_auth_context),
):

    agent = await db.agent.find_unique(where={"agent_id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await CerbosService.is_allowed(
        principal=auth.principal,
        action="unsubscribe",
        resource=build_agent_resource(
            agent_id=agent.agent_id,
            tenant_id=agent.tenant_id,
        ),
    )

    try:
        await db.agentsubscription.delete(
            where={
                "user_id_agent_id": {
                    "user_id": user_id,
                    "agent_id": agent_id,
                }
            }
        )
        return {"status": "success", "message": "Unsubscribed successfully."}
    except Exception:
        raise HTTPException(status_code=400, detail="Subscription not found")
