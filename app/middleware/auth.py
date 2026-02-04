from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import PyJWTError as JWTError
from app.core.config import settings
from app.core.db import db
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify JWT token from Header or Cookie, return user"""
    try:
        token = None
        
        # 1. Try to get token from Authorization header
        if credentials:
            token = credentials.credentials
            logger.info("[AUTH DEBUG] Attempting authentication via Bearer token")
        
        # 2. Try to get token from session_token cookie if no header token
        if not token:
            token = request.cookies.get("session_token")
            if token:
                logger.info("[AUTH DEBUG] Attempting authentication via session_token cookie")
        
        if not token:
            logger.warning("[AUTH DEBUG] No authentication token found in Header or Cookie")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated: No token provided"
            )

        # 3. Verify JWT with Clerk's public key
        payload = None
        try:
            # Try PyJWT style (leeway is a top-level arg)
            options = {"verify_aud": False, "verify_azp": False}
            payload = jwt.decode(
        token,
        settings.CLERK_JWT_VERIFICATION_KEY,
        algorithms=["RS256"],
        options={
            "verify_aud": False,
            "verify_azp": False
        },
        leeway=600  # <--- ADD THIS LINE (Allows 60 seconds of clock drift)
    )
        except TypeError:
            # Fallback for python-jose style (leeway is inside options)
            logger.info("[AUTH DEBUG] Using jose-style leeway validation")
            options = {"verify_aud": False, "verify_azp": False, "leeway": 60}
            payload = jwt.decode(
                token,
                settings.CLERK_JWT_VERIFICATION_KEY,
                algorithms=["RS256"],
                options=options
            )
        except jwt.ExpiredSignatureError:
            logger.warning("[AUTH DEBUG] Token has expired even with leeway")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        except Exception as je:
            logger.error(f"[AUTH DEBUG] JWT decode failed: {str(je)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(je)}"
            )

        # 4. Extract subject and find user
        request.state.session_id = payload.get("sid")
        clerk_user_id: str = payload.get("sub")
        if not clerk_user_id:
            logger.error("[AUTH DEBUG] JWT missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        # Get user from database
        user = await db.userprofile.find_unique(
            where={"clerk_user_id": clerk_user_id},
            include={"tenant": True}
        )
        
        if not user:
            logger.error(f"[AUTH DEBUG] User with clerk_user_id {clerk_user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in local database"
            )
        
        # 5. Check user status
        if user.status == "disabled":
            logger.error(f"[AUTH DEBUG] User {user.email} is disabled")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        if user.status == "pending" and user.role != "SUPER_ADMIN":
            logger.error(f"[AUTH DEBUG] User {user.email} is pending setup")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account setup incomplete. Please set your password."
            )
        
        logger.info(f"[AUTH DEBUG] Successfully authenticated user: {user.email} ({user.role})")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AUTH DEBUG] Unexpected authentication error ({type(e).__name__}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication process failed: {type(e).__name__}: {str(e)}"
        )

def require_role(*allowed_roles: str):
    """Decorator to check user role"""
    async def role_checker(user = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
