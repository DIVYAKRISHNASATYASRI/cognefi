from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from typing import Optional

# Password Setup
class SetPasswordRequest(BaseModel):
    token: str
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a number')
        return v

class SetPasswordResponse(BaseModel):
    message: str

# Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    email: str
    requires_otp: bool

# OTP Verification
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class UserInfo(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    role: str
    tenant_id: Optional[UUID]
    tenant_name: Optional[str]

class VerifyOTPResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo

# Existing Auth Context Response
class MeResponse(BaseModel):
    user_id: UUID
    email: str
    role: str
    tenant_id: Optional[UUID]
    tenant_name: Optional[str]
