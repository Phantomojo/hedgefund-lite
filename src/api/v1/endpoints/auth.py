"""
Authentication endpoints for user management and security.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.core.security import security_manager, get_current_user
from src.core.config import settings

router = APIRouter()


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserCreate(BaseModel):
    """User creation model."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class MasterPasswordRequest(BaseModel):
    """Master password request model."""
    password: str


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint for user authentication."""
    try:
        # Check if account is locked
        if security_manager.check_account_lockout(form_data.username):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to failed attempts"
            )
        
        # Verify credentials (this would check against database)
        # For now, use placeholder authentication
        if form_data.username == "admin" and form_data.password == "password":
            # Reset failed attempts on successful login
            security_manager.reset_failed_attempts(form_data.username)
            
            # Create access token
            access_token = security_manager.create_access_token(
                data={"sub": form_data.username}
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.security.access_token_expire_minutes * 60
            )
        else:
            # Record failed attempt
            security_manager.record_failed_attempt(form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/register")
async def register(user: UserCreate):
    """Register a new user."""
    try:
        # Check if user already exists (this would check database)
        # For now, always allow registration
        
        # Hash password
        hashed_password = security_manager.hash_password(user.password)
        
        # Create user (this would save to database)
        # For now, just return success
        
        return {"message": "User registered successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """Logout endpoint."""
    try:
        # Invalidate session (this would remove from Redis)
        # For now, just return success
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information."""
    try:
        # Get user info from database
        # For now, return basic info
        return {
            "username": current_user,
            "email": f"{current_user}@example.com",
            "full_name": f"{current_user.title()} User",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )


@router.post("/master-password/generate")
async def generate_master_password(current_user: str = Depends(get_current_user)):
    """Generate a new master password for emergency access."""
    try:
        # Check if user has permission
        if not security_manager.check_permission(current_user, "master_password", "generate"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Generate master password
        master_password = security_manager.generate_master_password()
        
        return {
            "message": "Master password generated successfully",
            "master_password": master_password,
            "expires_at": security_manager.master_password.expires_at.isoformat() if security_manager.master_password else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate master password: {str(e)}"
        )


@router.post("/master-password/verify")
async def verify_master_password(request: MasterPasswordRequest):
    """Verify master password for emergency access."""
    try:
        # Verify master password
        is_valid = security_manager.verify_master_password(request.password)
        
        if is_valid:
            return {"message": "Master password verified successfully", "valid": True}
        else:
            return {"message": "Invalid master password", "valid": False}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify master password: {str(e)}"
        )


@router.post("/emergency-token/generate")
async def generate_emergency_token(current_user: str = Depends(get_current_user)):
    """Generate emergency access token."""
    try:
        # Check if user has permission
        if not security_manager.check_permission(current_user, "emergency", "generate"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Generate emergency token
        emergency_token = security_manager.generate_emergency_token()
        
        return {
            "message": "Emergency token generated successfully",
            "emergency_token": emergency_token,
            "expires_in": 300  # 5 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate emergency token: {str(e)}"
        )


@router.post("/emergency-token/verify")
async def verify_emergency_token(token: str):
    """Verify emergency access token."""
    try:
        # Verify emergency token
        is_valid = security_manager.verify_emergency_token(token)
        
        if is_valid:
            return {"message": "Emergency token verified successfully", "valid": True}
        else:
            return {"message": "Invalid emergency token", "valid": False}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify emergency token: {str(e)}"
        )


@router.get("/security-status")
async def get_security_status(current_user: str = Depends(get_current_user)):
    """Get security status and configuration."""
    try:
        return {
            "master_password_enabled": settings.security.master_password.enabled,
            "emergency_controls_enabled": settings.security.emergency.kill_switch_enabled,
            "audit_trails_enabled": True,  # Would come from settings
            "session_timeout_minutes": settings.security.access_token_expire_minutes,
            "max_failed_attempts": security_manager.max_failed_attempts,
            "lockout_duration_minutes": security_manager.lockout_duration.total_seconds() / 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security status: {str(e)}"
        )
