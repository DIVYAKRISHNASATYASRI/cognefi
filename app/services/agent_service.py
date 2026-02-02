from app.core.db import db
from app.api.schemas import AgentCreate,AgentUpdate

class AgentService:
    @staticmethod
    async def get_marketplace():
        return await db.agent.find_many(
            where={"access_type": "GLOBAL", "is_public": True},
            include={"agent_model_config": True}
        )

    @staticmethod
    async def get_my_agents(user_id: str, tenant_id: str):
        return await db.agent.find_many(
            where={
                "OR": [
                    {"tenant_id": tenant_id},
                    {"subscriptions": {"some": {"user_id": user_id}}}
                ]
            },
            include={"agent_model_config": True}
        )

    @staticmethod
    async def create_agent(data: AgentCreate):
        return await db.agent.create(
            data={
                "tenant_id": data.tenant_id,
                "created_by": data.created_by,
                "agent_name": data.agent_name,
                "access_type": data.access_type,
                "is_public": data.is_public,
                "agent_model_config": {"create": {"model_provider": data.model_provider, "model_name": data.model_name, "temperature": data.temperature}},
                "prompts": {"create": [{"instructions": data.instructions, "system_message": data.system_message, "is_active": True}]},
                "ops_config": {"create": {}},
                "memory_config": {"create": {}}
            }
        )

    @staticmethod
    async def update_agent(agent_id: str, data: AgentUpdate):
        """
        Updates agent configuration across multiple tables.
        If prompts change, it creates a new version instead of overwriting.
        """
        # 1. Update Core Agent Table
        core_data = {k: v for k, v in data.dict().items() if v is not None and k in ['agent_name', 'description', 'status']}
        if core_data:
            await db.agent.update(where={"agent_id": agent_id}, data=core_data)

        # 2. Update Model Config
        m_data = {k: v for k, v in data.dict().items() if v is not None and k in ['model_provider', 'model_name', 'temperature']}
        if m_data:
            await db.agentmodelconfig.update(where={"agent_id": agent_id}, data=m_data)

        # 3. Update Prompts (Versioning Logic)
        if data.instructions or data.system_message:
            # Deactivate current active prompt
            await db.agentprompt.update_many(
                where={"agent_id": agent_id, "is_active": True},
                data={"is_active": False}
            )
            # Create a new version
            await db.agentprompt.create(
                data={
                    "agent_id": agent_id,
                    "instructions": data.instructions,
                    "system_message": data.system_message,
                    "is_active": True
                }
            )

        # 4. Update Ops Config
        if data.markdown is not None:
            await db.agentopsconfig.update(
                where={"agent_id": agent_id},
                data={"markdown": data.markdown}
            )

        return await AgentService.get_agent_full_details(agent_id)

    @staticmethod
    async def delete_agent(agent_id: str):
        """
        Deletes the agent. 
        Note: Prisma 'onDelete: Cascade' in schema handles related tables.
        """
        return await db.agent.delete(where={"agent_id": agent_id})

    @staticmethod
    async def get_agent_full_details(agent_id: str):
        return await db.agent.find_unique(
            where={"agent_id": agent_id},
            include={
                "agent_model_config": True,
                "prompts": {"where": {"is_active": True}},
                "ops_config": True
            }
        )