from fastapi import APIRouter, HTTPException, Body
from app.services.agentrunner import run_agent_secured
from app.services.agent_service import AgentService
from app.api.schemas import AgentCreate, AgentSubscribe, AgentRunRequest,AgentUpdate
from app.core.db import db

router = APIRouter()

@router.get("/marketplace")
async def get_marketplace():
    return await AgentService.get_marketplace()

@router.post("/subscribe")
async def subscribe(payload: AgentSubscribe):
    try:
        return await db.agentsubscription.create(
            data={"user_id": payload.user_id, "agent_id": payload.agent_id}
        )
    except:
        raise HTTPException(status_code=400, detail="Already subscribed")

@router.get("/my-agents/{user_id}/{tenant_id}")
async def my_agents(user_id: str, tenant_id: str):
    return await AgentService.get_my_agents(user_id, tenant_id)

@router.post("/run/{agent_id}")
async def run_agent_endpoint(agent_id: str, payload: AgentRunRequest):
    try:
        content = await run_agent_secured(agent_id, payload.user_id, payload.tenant_id, payload.message)
        return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
# --- UPDATE AGENT ---
@router.patch("/agents/{agent_id}")
async def update_agent(agent_id: str, payload: AgentUpdate):
    try:
        updated_agent = await AgentService.update_agent(agent_id, payload)
        return {"status": "success", "data": updated_agent}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

# --- DELETE AGENT ---
@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    try:
        await AgentService.delete_agent(agent_id)
        return {"status": "success", "message": f"Agent {agent_id} and all related configs deleted."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")

# --- UNSUBSCRIBE FROM MARKETPLACE AGENT ---
@router.delete("/unsubscribe/{user_id}/{agent_id}")
async def unsubscribe(user_id: str, agent_id: str):
    try:
        await db.agentsubscription.delete(
            where={
                "user_id_agent_id": {
                    "user_id": user_id,
                    "agent_id": agent_id
                }
            }
        )
        return {"status": "success", "message": "Unsubscribed successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Subscription not found")