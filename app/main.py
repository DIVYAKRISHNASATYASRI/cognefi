from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import connect_db, disconnect_db
from app.api import tenants, users, me, agent_api, auth

app = FastAPI(title="Cognefi Integrated AI platform")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# Register All Routers
app.include_router(auth.router, prefix="/api")
app.include_router(tenants.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(me.router, prefix="/api")
app.include_router(agent_api.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "online", "message": "Unified Backend Engine is Ready"}
