"""
Email Service for Password Reset and Notifications
Uses Python smtplib to send emails via Gmail SMTP
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    """Handle email sending functionality"""
    
    def __init__(self):
        self.smtp_server = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT", 587))
        self.sender_email = os.getenv("EMAIL_USER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        
        # Validate configuration
        if not self.sender_email or not self.sender_password:
            logger.warning("⚠️  Email credentials not configured in .env")
            logger.warning("   Set EMAIL_USER and EMAIL_PASSWORD to enable email sending")
            self.is_configured = False
        else:
            self.is_configured = True
            logger.info("✅ Email service configured successfully")
    
    def send_password_reset_email(self, recipient_email: str, reset_token: str, user_name: str = None) -> dict:
        """
        Send password reset email with secure token link
        
        Args:
            recipient_email: User's email address
            reset_token: Secure reset token (32-byte hex string)
            user_name: User's name (optional, for personalization)
        
        Returns:
            dict: {"success": bool, "message": str, "log": str}
        """
        
        if not self.is_configured:
            msg = f"❌ Email service not configured. Reset token for testing: {reset_token}"
            logger.warning(msg)
            return {
                "success": False,
                "message": "Email service not configured. Contact admin.",
                "testing_token": reset_token
            }
        
        try:
            # Build reset link
            reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🔐 Password Reset Request - Price Intelligence"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Plain text version (fallback)
            text = f"""
Hello {user_name or 'User'},

You requested a password reset for your Price Intelligence account.

Click the link below to reset your password (valid for 60 minutes):
{reset_link}

If you did not request this, please ignore this email.

Best regards,
Price Intelligence Team
"""
            
            # HTML version (preferred)
            html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ color: #6366f1; text-align: center; margin-bottom: 30px; }}
        .content {{ color: #333; line-height: 1.6; }}
        .button-container {{ text-align: center; margin: 30px 0; }}
        .button {{ background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; }}
        .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }}
        .token-info {{ background: #f0f0f0; padding: 10px; border-left: 3px solid #6366f1; font-family: monospace; font-size: 12px; word-break: break-all; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        
        <div class="content">
            <p>Hello {user_name or 'User'},</p>
            
            <p>You requested a password reset for your <strong>Price Intelligence</strong> account.</p>
            
            <p>Click the button below to reset your password. This link is valid for <strong>60 minutes</strong>.</p>
            
            <div class="button-container">
                <a href="{reset_link}" class="button">Reset Password →</a>
            </div>
            
            <p>Or copy this link in your browser:</p>
            <div class="token-info">{reset_link}</div>
            
            <div class="warning">
                ⚠️ <strong>Security Notice:</strong> If you did not request this password reset, please ignore this email. Your account is secure.
            </div>
            
            <p>Reset token: <code>{reset_token}</code></p>
        </div>
        
        <div class="footer">
            <p>Price Intelligence Team | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Attach both text and HTML versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email via SMTP
            logger.info(f"📧 Attempting to send reset email to {recipient_email}...")
            logger.info(f"   SMTP Server: {self.smtp_server}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Use TLS for secure connection
                server.starttls()
                logger.info("   ✅ TLS connection established")
                
                # Login
                server.login(self.sender_email, self.sender_password)
                logger.info(f"   ✅ Authenticated as {self.sender_email}")
                
                # Send email
                server.send_message(message)
                logger.info(f"   ✅ Email sent successfully to {recipient_email}")
            
            return {
                "success": True,
                "message": f"Password reset link sent to {recipient_email}. Check your inbox and spam folder.",
                "email": recipient_email,
                "timestamp": datetime.now().isoformat()
            }
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Email authentication failed: {str(e)}"
            logger.error(error_msg)
            logger.error("   Check EMAIL_USER and EMAIL_PASSWORD in .env file")
            logger.error("   For Gmail: Use 'App Password' from https://myaccount.google.com/apppasswords")
            return {
                "success": False,
                "message": "Email authentication failed. Admin has been notified.",
                "error": "SMTP authentication error",
                "testing_token": reset_token
            }
        
        except smtplib.SMTPException as e:
            error_msg = f"❌ SMTP error while sending email: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": "Failed to send reset email. Please try again later.",
                "error": str(e),
                "testing_token": reset_token
            }
        
        except Exception as e:
            error_msg = f"❌ Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            logger.exception("Full exception traceback:")
            return {
                "success": False,
                "message": "An unexpected error occurred while sending the email.",
                "error": str(e),
                "testing_token": reset_token
            }

# Global instance
email_service = EmailService()

# Convenience functions
def send_password_reset(email: str, token: str, name: str = None) -> dict:
    """Send password reset email"""
    return email_service.send_password_reset_email(email, token, name)
