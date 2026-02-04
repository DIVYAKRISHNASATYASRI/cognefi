import asyncio
from jose import jwt
from app.core.config import settings
from app.services.clerk_service import create_clerk_session_token
import time

async def inspect_token():
    clerk_id = settings.SUPER_ADMIN_CLERK_ID
    if not clerk_id:
        print("No SUPER_ADMIN_CLERK_ID found")
        return

    token = await create_clerk_session_token(clerk_id)
    print(f"Generated Token: {token[:40]}...")
    
    # Decode without verification to see claims
    payload = jwt.get_unverified_claims(token)
    print(f"Claims: {payload}")
    
    exp = payload.get("exp")
    iat = payload.get("iat")
    if exp and iat:
        now = time.time()
        print(f"Issued at: {time.ctime(iat)}")
        print(f"Expires at: {time.ctime(exp)}")
        print(f"Current time: {time.ctime(now)}")
        print(f"Lifespan: {exp - iat} seconds")
        print(f"Time remaining: {exp - now} seconds")

if __name__ == "__main__":
    asyncio.run(inspect_token())
