from app.core.db import db
from .agentloader import hydrate_agent
from prisma import Json

async def run_agent_secured(agent_id: str, user_id: str, tenant_id: str, message: str):
    # 1. VERIFY ACCESS
    agent_record = await db.agent.find_first(
        where={
            "agent_id": agent_id,
            "OR": [
                {"tenant_id": tenant_id}, # Owner
                {"subscriptions": {"some": {"user_id": user_id}}} # Subscribed
            ]
        },
        include={"agent_model_config": True, "prompts": True, "ops_config": True, "memory_config": True}
    )

    if not agent_record:
        raise Exception("Access Denied: You must subscribe to this agent first.")

    # 2. RUN
    session = await db.agentsession.create(data={"agent_id": agent_id})
    try:
        agno_agent = await hydrate_agent(agent_record)
        response = agno_agent.run(message)

        await db.agentoutput.create(
            data={
                "session": {"connect": {"session_id": session.session_id}},
                "input_payload": message,
                "raw_response": Json({"content": str(response.content)})
            }
        )
        return response.content
    except Exception as e:
        await db.agentsession.update(where={"session_id": session.session_id}, data={"status": "failed"})
        raise e