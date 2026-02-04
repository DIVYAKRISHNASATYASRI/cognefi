import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # AI APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY")
    CLERK_JWT_VERIFICATION_KEY: str = os.getenv("CLERK_JWT_VERIFICATION_KEY")
    
    # SMTP Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@cognefi.com")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Cognefi AI Platform")
    
    # Application URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    
    # Security Settings
    PASSWORD_RESET_TOKEN_EXPIRY: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRY", "3600"))
    OTP_EXPIRY: int = int(os.getenv("OTP_EXPIRY", "300"))
    OTP_LENGTH: int = int(os.getenv("OTP_LENGTH", "6"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))

    # Super Admin Setup
    SUPER_ADMIN_EMAIL: str = os.getenv("SUPER_ADMIN_EMAIL", "admin@cognefi.com")
    SUPER_ADMIN_CLERK_ID: str = os.getenv("SUPER_ADMIN_CLERK_ID", "")

settings = Settings()