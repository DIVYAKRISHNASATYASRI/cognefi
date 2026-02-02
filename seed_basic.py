import asyncio
from app.core.db import db

async def seed():
    await db.connect()
    tenant = await db.tenant.create(data={"tenant_name": "Default Org"})
    user = await db.userprofile.create(data={
        "tenant_id": tenant.tenant_id,
        "full_name": "Admin",
        "email": "admin@test.com"
    })
    print(f"TENANT_ID: {tenant.tenant_id}")
    print(f"USER_ID: {user.user_id}")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())