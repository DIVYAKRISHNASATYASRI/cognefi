import asyncio
from clerk_backend_api import Clerk, models
from app.core.config import settings

async def list_clerk_users():
    clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
    try:
        response = await clerk.users.list_async(request=models.GetUserListRequest(limit=10))
        users = response
        print(f"Found {len(users)} users:")
        for u in users:
            email = u.email_addresses[0].email_address if u.email_addresses else "No Email"
            print(f"- ID: {u.id}, Email: {email}, Created: {u.created_at}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_clerk_users())
