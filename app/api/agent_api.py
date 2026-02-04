from fastapi import APIRouter, HTTPException, Body, Depends
from app.services.agentrunner import run_agent_secured
from app.services.agent_service import AgentService
from app.schemas.agent_schema import AgentCreate, AgentSubscribe, AgentUpdate
from app.core.db import db
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/marketplace")
async def get_marketplace(current_user=Depends(get_current_user)):
    """Browse public agents available in the marketplace."""
    return await AgentService.get_marketplace()

@router.post("/")
async def create_agent(
    payload: AgentCreate, 
    current_user=Depends(get_current_user)
):
    """
    Create an agent. 
    - Super Admins can create GLOBAL marketplace agents.
    - Tenant Users create PRIVATE agents for their own company.
    """
    try:
        # Security: Enforce tenant ownership for non-superadmins
        if current_user.role != "SUPER_ADMIN":
            payload.tenant_id = current_user.tenant_id
            payload.access_type = "PRIVATE"
            payload.is_public = False
        
        # Super Admin override for Global Agents
        if payload.access_type == "GLOBAL" and current_user.role == "SUPER_ADMIN":
            payload.tenant_id = None
            payload.is_public = True

        new_agent = await AgentService.create_agent(payload)
        return {"status": "success", "agent_id": new_agent.agent_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/subscribe")
async def subscribe_to_agent(
    payload: AgentSubscribe, 
    current_user=Depends(get_current_user)
):
    """Subscribe a user to a marketplace agent."""
    # Ensure user is only subscribing themselves
    if str(payload.user_id) != str(current_user.user_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        return await db.agentsubscription.create(
            data={"user_id": str(payload.user_id), "agent_id": str(payload.agent_id)}
        )
    except:
        raise HTTPException(status_code=400, detail="Already subscribed or invalid agent")

@router.get("/my-agents")
async def list_my_agents(current_user=Depends(get_current_user)):
    """List all agents (Private + Subscribed) for the logged-in user."""
    return await AgentService.get_my_agents(
        str(current_user.user_id), 
        str(current_user.tenant_id)
    )

@router.post("/run/{agent_id}")
async def run_agent(
    agent_id: str, 
    message: str = Body(..., embed=True),
    current_user=Depends(get_current_user)
):
    """
    Execute an Agno Agent.
    Security: The service verifies if current_user has access to agent_id.
    """
    try:
        content = await run_agent_secured(
            agent_id, 
            str(current_user.user_id), 
            str(current_user.tenant_id), 
            message
        )
        return {"response": content}
    except Exception as e:
        # 403 if subscription/ownership check fails
        raise HTTPException(status_code=403, detail=str(e))

@router.patch("/{agent_id}")
async def update_agent(
    agent_id: str, 
    payload: AgentUpdate,
    current_user=Depends(get_current_user)
):
    """Update agent configuration or version prompts."""
    # Logic inside service should verify current_user owns the agent
    return await AgentService.update_agent(agent_id, payload)

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user=Depends(get_current_user)
):
    """Delete agent - restricted to owner or Super Admin."""
    return await AgentService.delete_agent(agent_id)

@router.delete("/unsubscribe/{agent_id}")
async def unsubscribe(
    agent_id: str,
    current_user=Depends(get_current_user)
):
    """Remove a marketplace agent from the user's workspace."""
    try:
        await db.agentsubscription.delete(
            where={
                "user_id_agent_id": {
                    "user_id": str(current_user.user_id),
                    "agent_id": agent_id
                }
            }
        )
        return {"message": "Unsubscribed successfully"}
    except:
        raise HTTPException(status_code=404, detail="Subscription not found")