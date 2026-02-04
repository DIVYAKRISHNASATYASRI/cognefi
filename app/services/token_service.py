import secrets
import hashlib
from datetime import datetime, timedelta
from app.core.db import db
from app.core.config import settings

def generate_token() -> tuple[str, str]:
    """Generate token and its hash. Returns (plain_token, hashed_token)"""
    plain_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(plain_token.encode()).hexdigest()
    return plain_token, hashed_token

async def create_password_setup_token(user_id: str, db_client=None) -> str:
    """Create password setup token. Optionally accepts a transaction client."""
    client = db_client or db
    plain_token, hashed_token = generate_token()
    expires_at = datetime.utcnow() + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_EXPIRY)
    
    await client.authtoken.create(
        data={
            "user_id": user_id,
            "token_type": "password_setup",
            "token_hash": hashed_token,
            "expires_at": expires_at
        }
    )
    
    return plain_token

async def verify_password_setup_token(token: str) -> str | None:
    """Verify token and return user_id if valid"""
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    
    token_record = await db.authtoken.find_first(
        where={
            "token_hash": hashed_token,
            "token_type": "password_setup",
            "used_at": None,
            "expires_at": {"gte": datetime.utcnow()}
        }
    )
    
    if not token_record:
        return None
    
    # Mark as used
    await db.authtoken.update(
        where={"token_id": token_record.token_id},
        data={"used_at": datetime.utcnow()}
    )
    
    return token_record.user_id
