import asyncio
from app.core.db import db

async def seed():
    await db.connect()
    
    # Super Admin configuration (should match environment or manual Clerk setup)
    admin_email = "admin@cognefi.com"
    clerk_user_id = "user_399p1J2KRKvFUSbDV1NM8RrZCYY"
    
    # 1. Create Super Admin (No tenant context)
    # Check if exists
    existing = await db.userprofile.find_unique(where={"email": admin_email})
    if existing:
        print(f"Super Admin {admin_email} already exists.")
    else:
        user = await db.userprofile.create(
            data={
                "clerk_user_id": clerk_user_id,
                "full_name": "Super Admin",
                "email": admin_email,
                "role": "SUPER_ADMIN",
                "status": "active"
            }
        )
        print(f"✅ Super Admin Seeded Successfully: {user.email}")
    
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())