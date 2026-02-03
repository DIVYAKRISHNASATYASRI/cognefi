import asyncio
from app.core.db import db

async def seed():
    await db.connect()
    
    # 1. Create Tenant (Now with the required tenant_code)
    tenant = await db.tenant.create(
        data={
            "tenant_name": "Main Platform",
            "tenant_code": "MAIN001", 
            "industry": "Software",
            "subscription_plan": "pro"
        }
    )
    
    # 2. Create User
    user = await db.userprofile.create(
        data={
            "tenant_id": tenant.tenant_id,
            "full_name": "Super Admin",
            "email": "admin@cognefi.com",
            "role": "SUPERADMIN"
        }
    )
    
    print(f"✅ DB Seeded Successfully!")
    print(f"TENANT_ID: {tenant.tenant_id}")
    print(f"USER_ID: {user.user_id}")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())