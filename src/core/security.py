"""
Security module for the forex trading system.
Inspired by Vanta-ledger's NASA-grade security architecture.
"""

import os
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import structlog

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis

from src.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


@dataclass
class MasterPassword:
    """Master password system for emergency access."""
    password: str
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    is_used: bool = False


class SecurityManager:
    """Comprehensive security manager for the trading system."""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.redis.url)
        self.master_password: Optional[MasterPassword] = None
        self.failed_attempts: Dict[str, int] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=24)
    
    def generate_master_password(self) -> str:
        """Generate a new master password for emergency access."""
        # Generate 64-character random password
        password = secrets.token_urlsafe(48)
        
        # Create master password object
        self.master_password = MasterPassword(
            password=password,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            max_attempts=3
        )
        
        # Store in Redis with expiration
        self.redis_client.setex(
            f"master_password:{password}",
            1800,  # 30 minutes
            self.master_password.password
        )
        
        logger.warning("Master password generated", 
                      expires_at=self.master_password.expires_at.isoformat())
        
        return password
    
    def verify_master_password(self, password: str) -> bool:
        """Verify master password for emergency access."""
        if not self.master_password:
            return False
        
        # Check if password is expired
        if datetime.utcnow() > self.master_password.expires_at:
            logger.warning("Master password expired")
            return False
        
        # Check if max attempts exceeded
        if self.master_password.attempts >= self.master_password.max_attempts:
            logger.warning("Master password max attempts exceeded")
            return False
        
        # Check if already used
        if self.master_password.is_used:
            logger.warning("Master password already used")
            return False
        
        # Verify password
        if password == self.master_password.password:
            self.master_password.is_used = True
            logger.info("Master password verified successfully")
            return True
        
        self.master_password.attempts += 1
        logger.warning("Master password verification failed", 
                      attempts=self.master_password.attempts)
        return False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
            username: str = payload.get("sub")
            
            if username is None:
                return None
            
            return payload
        except JWTError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def check_account_lockout(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        if username in self.locked_accounts:
            lockout_time = self.locked_accounts[username]
            if datetime.utcnow() < lockout_time:
                return True
            else:
                # Remove lockout if expired
                del self.locked_accounts[username]
                self.failed_attempts[username] = 0
        
        return False
    
    def record_failed_attempt(self, username: str):
        """Record a failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = 0
        
        self.failed_attempts[username] += 1
        
        if self.failed_attempts[username] >= self.max_failed_attempts:
            self.locked_accounts[username] = datetime.utcnow() + self.lockout_duration
            logger.warning("Account locked due to failed attempts", 
                          username=username, 
                          lockout_until=self.locked_accounts[username].isoformat())
    
    def reset_failed_attempts(self, username: str):
        """Reset failed attempts for successful login."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.locked_accounts:
            del self.locked_accounts[username]
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate session token for user."""
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + self.session_timeout).isoformat()
        }
        
        session_token = secrets.token_urlsafe(32)
        
        # Store session in Redis
        self.redis_client.setex(
            f"session:{session_token}",
            int(self.session_timeout.total_seconds()),
            str(session_data)
        )
        
        return session_token
    
    def validate_session_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token."""
        session_data = self.redis_client.get(f"session:{session_token}")
        
        if not session_data:
            return None
        
        # Parse session data
        try:
            import json
            session = json.loads(session_data)
            expires_at = datetime.fromisoformat(session["expires_at"])
            
            if datetime.utcnow() > expires_at:
                # Remove expired session
                self.redis_client.delete(f"session:{session_token}")
                return None
            
            return session
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def revoke_session_token(self, session_token: str):
        """Revoke session token."""
        self.redis_client.delete(f"session:{session_token}")
    
    def create_audit_log(self, user_id: str, action: str, details: Dict[str, Any]):
        """Create audit log entry."""
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": "unknown",  # Would be extracted from request
            "user_agent": "unknown"   # Would be extracted from request
        }
        
        # Store in Redis for immediate access
        self.redis_client.lpush("audit_log", str(audit_entry))
        
        # Also store in database for persistence
        # This would be implemented with database models
        
        logger.info("Audit log created", 
                   user_id=user_id, 
                   action=action, 
                   details=details)
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission for resource and action."""
        # This would implement role-based access control
        # For now, return True for all authenticated users
        return True
    
    def generate_emergency_token(self) -> str:
        """Generate emergency access token."""
        token = secrets.token_urlsafe(32)
        
        # Store emergency token with short expiration
        self.redis_client.setex(
            f"emergency_token:{token}",
            300,  # 5 minutes
            datetime.utcnow().isoformat()
        )
        
        logger.warning("Emergency token generated", token=token)
        return token
    
    def verify_emergency_token(self, token: str) -> bool:
        """Verify emergency access token."""
        token_data = self.redis_client.get(f"emergency_token:{token}")
        
        if not token_data:
            return False
        
        # Remove token after use
        self.redis_client.delete(f"emergency_token:{token}")
        
        logger.warning("Emergency token used", token=token)
        return True


# Global security manager instance
security_manager = SecurityManager()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from JWT token."""
    token = credentials.credentials
    
    payload = security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return username


def require_master_password(password: str) -> bool:
    """Require master password for critical operations."""
    return security_manager.verify_master_password(password)


def create_audit_entry(user_id: str, action: str, details: Dict[str, Any]):
    """Create audit log entry."""
    security_manager.create_audit_log(user_id, action, details)


def check_permissions(user_id: str, resource: str, action: str) -> bool:
    """Check user permissions."""
    return security_manager.check_permission(user_id, resource, action)
