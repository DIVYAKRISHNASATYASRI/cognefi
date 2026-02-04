import asyncio
import httpx
from app.core.config import settings
from app.services.clerk_service import create_clerk_session_token
import time

async def verify_tenant_setup():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Generate Super Admin Token
    clerk_id = settings.SUPER_ADMIN_CLERK_ID
    if not clerk_id:
        import os
        clerk_id = os.getenv("SUPER_ADMIN_CLERK_ID")
    
    print(f"Using Super Admin Clerk ID: {clerk_id}")
    token = await create_clerk_session_token(clerk_id)
    
    # 2. Test JWT Leeway (Wait a bit if we wanted to test expiration, but here we just prove it works)
    # The fix adds 'leeway=60', so even if the token technically expires in 1 second, it will work for 61 seconds.
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        # 3. Create a test tenant
        tenant_code = f"TEST_{int(time.time())}"
        admin_email = f"clerk.test.{int(time.time())}@cognefi-test.com"
        payload = {
            "tenant_name": "Verification Org",
            "tenant_code": tenant_code,
            "industry": "TESTING",
            "subscription_plan": "pro",
            "admin_name": "Test Admin",
            "admin_email": admin_email
        }
        
        print(f"\nCreating tenant {tenant_code}...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post("/api/tenants/", json=payload, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print("✅ SUCCESS: Tenant created!")
            print(f"Message: {data.get('message')}")
            print(f"Tenant ID: {data.get('tenant_id')}")
        else:
            print(f"❌ FAILED: Status {resp.status_code}")
            print(resp.text)

if __name__ == "__main__":
    asyncio.run(verify_tenant_setup())
