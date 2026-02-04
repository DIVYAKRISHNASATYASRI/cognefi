from clerk_backend_api import Clerk, models
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Clerk client
clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

async def create_clerk_user(email: str, full_name: str, password: str = None) -> str:
    """Create user in Clerk and return clerk_user_id"""
    try:
        # Split name safely
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Generate a username (some Clerk instances require it)
        # We use the email prefix + first 4 chars of email hash to ensure uniqueness and URL safety
        import hashlib
        email_prefix = email.split('@')[0].replace('.', '_').replace('-', '_')
        email_hash = hashlib.md5(email.encode()).hexdigest()[:4]
        username = f"{email_prefix}_{email_hash}"

        user_params = {
            "email_address": [email],
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "public_metadata": {"platform": "agent_marketplace"}
        }
        
        if password:
            user_params["password"] = password
        else:
            user_params["skip_password_requirement"] = True

        user = await clerk.users.create_async(**user_params)
        return user.id
    except Exception as e:
        logger.error(f"Failed to create Clerk user: {str(e)}")
        raise

async def update_clerk_password(clerk_user_id: str, password: str):
    """Update user password in Clerk"""
    try:
        await clerk.users.update_async(
            user_id=clerk_user_id,
            password=password
        )
    except Exception as e:
        logger.error(f"Failed to update Clerk password: {str(e)}")
        raise

async def verify_clerk_credentials(email: str, password: str) -> dict:
    """
    Verify email and password with Clerk.
    We first find the user by email, then verify the password using the SDK.
    """
    try:
        response = await clerk.users.list_async(request=models.GetUserListRequest(email_address=[email]))
        users = response
        if not users or len(users) == 0:
            return None
        
        clerk_user = users[0]
        # Verify the password with Clerk
        try:
            verification = await clerk.users.verify_password_async(
                user_id=clerk_user.id,
                password=password
            )
            if not verification.verified:
                logger.warning(f"Password verification failed for user: {email}")
                return None
        except Exception as ve:
            logger.error(f"Clerk password verification error for {email}: {str(ve)}")
            return None

        return {"clerk_user_id": clerk_user.id, "email": email}
    except Exception as e:
        logger.error(f"Failed to verify credentials: {str(e)}")
        return None

async def create_clerk_session_token(clerk_user_id: str) -> str:
    """Generate JWT session token for user using Clerk Sessions (Async)"""
    try:
        # 1. Create a session for the user
        session = await clerk.sessions.create_async(
            request=models.CreateSessionRequestBody(user_id=clerk_user_id)
        )
        
        # 2. Generate a JWT token for this session with a longer lifespan for dev testing
        # Standard Clerk tokens are 60s, but we can extend them here.
        token_response = await clerk.sessions.create_token_async(
            session_id=session.id,
            expires_in_seconds=3600  # 1 hour lifespan
        )
        
        return token_response.jwt
    except Exception as e:
        logger.error(f"Failed to create session token: {str(e)}")
        raise

async def revoke_clerk_session(session_id: str):
    """Revoke a specific session in Clerk (Async)"""
    try:
        await clerk.sessions.revoke_async(session_id=session_id)
    except Exception as e:
        logger.error(f"Failed to revoke Clerk session: {str(e)}")
        raise

async def delete_clerk_user(clerk_user_id: str):
    """Delete user from Clerk (Async)"""
    try:
        await clerk.users.delete_async(user_id=clerk_user_id)
    except Exception as e:
        logger.error(f"Failed to delete Clerk user: {str(e)}")
        raise
