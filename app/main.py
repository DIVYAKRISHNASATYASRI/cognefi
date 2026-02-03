from fastapi import FastAPI
from app.api import health, tenants, users, me

app = FastAPI(title="Tenant Management Service")

app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(me.router)
