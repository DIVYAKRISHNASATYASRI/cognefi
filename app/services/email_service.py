import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, html_content: str):
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise

async def send_password_setup_email(to_email: str, full_name: str, token: str):
    """Send password setup email"""
    setup_link = f"{settings.FRONTEND_URL}/auth/set-password?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #2c3e50;">Welcome to Cognefi AI Platform!</h2>
            <p>Hi {full_name},</p>
            <p>Your account has been created for the Agent Marketplace. Please set your password to activate your account and start using our agents.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{setup_link}" 
                   style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
                    Set Your Password
                </a>
            </div>
            <p>Or copy this link to your browser:</p>
            <p style="color: #666; font-size: 14px; word-break: break-all;">{setup_link}</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRY // 3600} hour(s).<br>
                If you did not expect this invitation, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    await send_email(to_email, "Set Your Password - Cognefi AI Platform", html_content)

async def send_otp_email(to_email: str, full_name: str, otp_code: str):
    """Send OTP code for login"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #2c3e50;">Your Login Verification Code</h2>
            <p>Hi {full_name},</p>
            <p>Your one-time password (OTP) for logging in is:</p>
            <div style="text-align: center; margin: 30px 0;">
                <h1 style="color: #4CAF50; letter-spacing: 12px; font-size: 42px; margin: 0;">{otp_code}</h1>
            </div>
            <p>This code will expire in {settings.OTP_EXPIRY // 60} minutes.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                If you didn't request this code, please ignore this email and consider updating your password.
            </p>
        </div>
    </body>
    </html>
    """
    
    await send_email(to_email, "Your Login Code - Cognefi AI Platform", html_content)
