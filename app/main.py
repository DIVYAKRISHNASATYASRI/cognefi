from fastapi import FastAPI
from app.core.db import connect_db, disconnect_db
from app.api.agent_api import router as agent_v1

app = FastAPI(title="Agno Agent Ops Platform")

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

app.include_router(agent_v1, prefix="/api")