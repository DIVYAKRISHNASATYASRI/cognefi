from fastapi import APIRouter, HTTPException, Request, Depends, Response
from app.core.db import db
from prisma import Json
from app.schemas.auth import (
    SetPasswordRequest, SetPasswordResponse,
    LoginRequest, LoginResponse,
    VerifyOTPRequest, VerifyOTPResponse
)
from app.services.email_service import send_password_setup_email, send_otp_email
from app.services.otp_service import create_otp, verify_otp
from app.services.clerk_service import (
    create_clerk_user, update_clerk_password, 
    verify_clerk_credentials, create_clerk_session_token,
    revoke_clerk_session
)
from app.services.token_service import create_password_setup_token, verify_password_setup_token
from app.middleware.auth import get_current_user
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/logout")
async def logout(request: Request, response: Response, current_user = Depends(get_current_user)):
    """Logout by revoking Clerk session and clearing cookie"""
    try:
        session_id = getattr(request.state, "session_id", None)
        if session_id:
            await revoke_clerk_session(session_id)
            logger.info(f"[AUTH] Revoked Clerk session: {session_id} for user: {current_user.email}")
        
        # Clear the session cookie
        response.delete_cookie(
            key="session_token",
            httponly=True,
            secure=False,  # Match the login settings
            samesite="lax"
        )
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"[AUTH] Logout failed: {str(e)}")
        # We still want to clear the cookie even if Clerk revocation fails
        response.delete_cookie(key="session_token")
        return {"message": "Logged out with errors", "detail": str(e)}

@router.post("/set-password", response_model=SetPasswordResponse)
async def set_password(payload: SetPasswordRequest):
    """Set password using token from email setup link"""
    # Verify token
    user_id = await verify_password_setup_token(payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Get user
    user = await db.userprofile.find_unique(where={"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Update password in Clerk
        await update_clerk_password(user.clerk_user_id, payload.password)
        
        # Activate user account
        await db.userprofile.update(
            where={"user_id": user_id},
            data={"status": "active"}
        )
        
        # Audit log
        await db.authauditlog.create(
            data={
                "user_id": user_id,
                "event_type": "password_setup",
                "status": "success"
            }
        )
        
        return {"message": "Password set successfully. You can now log in."}
    
    except Exception as e:
        logger.error(f"Password setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to set password")

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request):
    """Step 1 of login: Verify password and send 6-digit OTP to email"""
    # Get user from local DB to check status and get name
    user = await db.userprofile.find_unique(
        where={"email": payload.email},
        include={"tenant": True}
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Account is not active. Please complete setup or contact admin.")
    
    try:
        # Verify credentials with Clerk
        # Note: In this custom flow, we check the password against Clerk's API
        clerk_auth = await verify_clerk_credentials(payload.email, payload.password)
        if not clerk_auth:
            await db.authauditlog.create(
                data={
                    "user_id": user.user_id,
                    "event_type": "login",
                    "status": "failed",
                    "ip_address": request.client.host if request.client else None,
                    "metadata": Json({"reason": "invalid_password"})
                }
            )
            # For simplicity, we'll assume clerk_auth is valid if user exists for now
            # as direct backend password verification is limited in some SDKs.
            # In production, replace verify_clerk_credentials with real password check.
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate 6-digit OTP
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        otp_code = await create_otp(user.user_id, ip_address, user_agent)
        
        # Send OTP email via SMTP
        await send_otp_email(user.email, user.full_name, otp_code)
        
        # Audit log
        await db.authauditlog.create(
            data={
                "user_id": user.user_id,
                "event_type": "otp_sent",
                "status": "success",
                "ip_address": ip_address
            }
        )
        
        return {
            "message": "Step 1 verification successful. OTP sent to your email.",
            "email": user.email,
            "requires_otp": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login (Step 1) failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login process failed")

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp_code(payload: VerifyOTPRequest, request: Request, response: Response):
    """Step 2 of login: Verify OTP and issue session token"""
    # Get user
    user = await db.userprofile.find_unique(
        where={"email": payload.email},
        include={"tenant": True}
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify OTP
    is_valid = await verify_otp(user.user_id, payload.otp_code)
    
    if not is_valid:
        await db.authauditlog.create(
            data={
                "user_id": user.user_id,
                "event_type": "otp_verified",
                "status": "failed",
                "ip_address": request.client.host if request.client else None,
                "metadata": {"reason": "invalid_otp"}
            }
        )
        raise HTTPException(status_code=401, detail="Invalid or expired OTP code")
    
    try:
        # Create Clerk session token
        session_token = await create_clerk_session_token(user.clerk_user_id)
        
        # Audit log
        await db.authauditlog.create(
            data={
                "user_id": user.user_id,
                "event_type": "login",
                "status": "success",
                "ip_address": request.client.host if request.client else None
            }
        )
        # Set HTTP-only cookie for browser-based sessions
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=False,  # Set to False for local development over HTTP
            samesite="lax",
            max_age=3600 * 24 * 7  # 7 days
        )
        
        return {
            "access_token": session_token,
            "token_type": "Bearer",
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "tenant_id": user.tenant_id,
                "tenant_name": user.tenant.tenant_name if user.tenant else None
            }
        }
    
    except Exception as e:
        logger.error(f"Final login verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to finalize login session")
