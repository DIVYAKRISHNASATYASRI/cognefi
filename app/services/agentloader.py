from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

async def hydrate_agent(record) -> Agent:
    m_cfg = record.agent_model_config
    p_cfg = next((p for p in record.prompts if p.is_active), None)
    o_cfg = record.ops_config
    mem_cfg = record.memory_config

    provider = m_cfg.model_provider.lower() if m_cfg else "openai"
    model_id = m_cfg.model_name if m_cfg else "gpt-4o"
    temp = float(m_cfg.temperature) if m_cfg else 0.7

    if provider == "google":
        model = Gemini(id=model_id, temperature=temp)
    else:
        model = OpenAIChat(id=model_id, temperature=temp)

    return Agent(
        name=record.agent_name,
        model=model,
        instructions=p_cfg.instructions if p_cfg else None,
        system_message=p_cfg.system_message if p_cfg else None,
        markdown=o_cfg.markdown if o_cfg else True,
        add_history_to_context=mem_cfg.enable_agentic_memory if mem_cfg else False,
        num_history_runs=mem_cfg.num_history_runs if mem_cfg else 3,
    )