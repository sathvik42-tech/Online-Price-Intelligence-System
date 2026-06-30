"""
Authentication Router for FastAPI Backend
Handles user registration, login, and password reset
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import secrets
import logging
from datetime import datetime, timedelta

try:
    from backend.database import get_connection
except ImportError:
    from database import get_connection

try:
    from .email_service import send_password_reset
except (ImportError, ValueError):
    try:
        from backend.app.email_service import send_password_reset
    except ImportError:
        from email_service import send_password_reset

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
import bcrypt
# Pydantic Models
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    name: str
    email: EmailStr
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Password reset with token"""
    token: str
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class PasswordResetResponse(BaseModel):
    """Response for password reset"""
    success: bool
    message: str
    email: Optional[str] = None
    testing_token: Optional[str] = None

# ============================================================================
# Helper Functions
# ============================================================================

def get_db_connection():
    """Get database connection"""
    conn = get_connection()
    if not conn:
        logger.error("❌ Failed to connect to database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    return conn

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_reset_token() -> str:
    """Generate a secure 32-byte reset token"""
    return secrets.token_hex(32)

# ============================================================================
# Endpoints
# ============================================================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """Register a new user"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s;", (req.email,))
        if cur.fetchone():
            logger.warning(f"⚠️  Registration attempted with existing email: {req.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(req.password)
        
        # Insert user
        cur.execute(
            """
            INSERT INTO users (name, email, password, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id, name, email, created_at;
            """,
            (req.name, req.email, hashed_password)
        )
        user = cur.fetchone()
        conn.commit()
        
        logger.info(f"✅ User registered successfully: {req.email}")
        
        return {
            "success": True,
            "message": "User registered successfully. Please log in.",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "created_at": user[3].isoformat()
            }
        }
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    
    finally:
        conn.close()


@router.post("/login")
async def login(req: LoginRequest):
    """Login user and return JWT token"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor()
        
        # Find user
        cur.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s;",
            (req.email,)
        )
        user_row = cur.fetchone()
        
        if not user_row:
            logger.warning(f"⚠️  Login attempt with non-existent email: {req.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_id, name, email, hashed_password = user_row
        
        # Verify password
        if not verify_password(req.password, hashed_password):
            logger.warning(f"⚠️  Failed login attempt for: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logger.info(f"✅ User logged in successfully: {email}")
        
        # In production, generate JWT token here
        # For now, return basic info
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    
    finally:
        conn.close()


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(req: ForgotPasswordRequest):
    """Request password reset email"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT id, name FROM users WHERE email = %s;", (req.email,))
        user_row = cur.fetchone()
        
        if not user_row:
            # For security: don't reveal if email exists
            logger.info(f"ℹ️  Password reset requested for non-existent email: {req.email}")
            return PasswordResetResponse(
                success=True,
                message="If that email exists, a reset link has been sent."
            )
        
        user_id, user_name = user_row
        
        # Generate secure reset token
        reset_token = generate_reset_token()
        token_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token in database
        cur.execute(
            """
            UPDATE users 
            SET reset_password_token = %s, reset_password_expires = %s
            WHERE id = %s;
            """,
            (reset_token, token_expires, user_id)
        )
        conn.commit()
        
        logger.info(f"📝 Reset token generated for: {req.email}")
        logger.info(f"   Token expires at: {token_expires}")
        
        # Send email with reset link
        email_result = send_password_reset(req.email, reset_token, user_name)
        
        if email_result["success"]:
            logger.info(f"✅ Reset email sent successfully to {req.email}")
            return PasswordResetResponse(
                success=True,
                message="Password reset link sent to your email. Check your inbox and spam folder.",
                email=req.email
            )
        else:
            # Email failed, but return token for development/testing
            logger.warning(f"⚠️  Email sending failed, returning token for development")
            return PasswordResetResponse(
                success=False,
                message=email_result.get("message", "Email service unavailable. Token provided for testing."),
                email=req.email,
                testing_token=email_result.get("testing_token")
            )
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Forgot password error: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )
    
    finally:
        conn.close()


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Reset password with valid token"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor()
        
        # Verify reset token
        cur.execute(
            """
            SELECT id, email FROM users 
            WHERE reset_password_token = %s 
            AND reset_password_expires > NOW();
            """,
            (req.token,)
        )
        user_row = cur.fetchone()
        
        if not user_row:
            logger.warning(f"⚠️  Invalid or expired reset token attempted")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token is invalid or expired"
            )
        
        user_id, email = user_row
        
        # Hash new password
        hashed_password = hash_password(req.password)
        
        # Update password and clear reset token
        cur.execute(
            """
            UPDATE users 
            SET password = %s, reset_password_token = NULL, reset_password_expires = NULL
            WHERE id = %s;
            """,
            (hashed_password, user_id)
        )
        conn.commit()
        
        logger.info(f"✅ Password reset successful for: {email}")
        
        return {
            "success": True,
            "message": "Password reset successfully. Please log in with your new password.",
            "email": email
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )
    
    finally:
        conn.close()


@router.get("/verify-token/{token}")
async def verify_reset_token(token: str):
    """Verify if a reset token is still valid"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT id, email FROM users 
            WHERE reset_password_token = %s 
            AND reset_password_expires > NOW();
            """,
            (token,)
        )
        user_row = cur.fetchone()
        
        if not user_row:
            logger.info(f"ℹ️  Reset token verification failed: {token[:8]}...")
            return {
                "valid": False,
                "message": "Reset token is invalid or expired"
            }
        
        logger.info(f"✅ Reset token verified for: {user_row[1]}")
        
        return {
            "valid": True,
            "message": "Token is valid. You can proceed with password reset.",
            "email": user_row[1]
        }
    
    except Exception as e:
        logger.error(f"❌ Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )
    
    finally:
        conn.close()
