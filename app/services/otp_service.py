import secrets
import hashlib
from datetime import datetime, timedelta
from app.core.db import db
from app.core.config import settings

def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])

async def create_otp(user_id: str, ip_address: str = None, user_agent: str = None, db_client=None) -> str:
    """Create and store OTP for user. Optionally accepts a transaction client."""
    client = db_client or db
    otp_code = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(seconds=settings.OTP_EXPIRY)
    
    await client.loginotp.create(
        data={
            "user_id": user_id,
            "otp_code": otp_code,
            "expires_at": expires_at,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    )
    
    return otp_code

async def verify_otp(user_id: str, otp_code: str, db_client=None) -> bool:
    """Verify OTP code. Optionally accepts a transaction client."""
    client = db_client or db
    otp_record = await client.loginotp.find_first(
        where={
            "user_id": user_id,
            "otp_code": otp_code,
            "verified_at": None,
            "expires_at": {"gte": datetime.utcnow()}
        },
        order={"created_at": "desc"}
    )
    
    if not otp_record:
        return False
    
    # Mark as verified
    await client.loginotp.update(
        where={"otp_id": otp_record.otp_id},
        data={"verified_at": datetime.utcnow()}
    )
    
    return True

async def cleanup_expired_otps():
    """Delete expired OTPs (periodic cleanup)"""
    await db.loginotp.delete_many(
        where={"expires_at": {"lt": datetime.utcnow()}}
    )
