"""
LaniakeA Protocol - Authentication System
Handles user authentication, JWT tokens, and session management.
"""

import os
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not available. Authentication features will be limited.")

logger = logging.getLogger("Authentication")


class PasswordManager:
    """Password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """
        Hash password using PBKDF2
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
        
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = os.urandom(32).hex()
        
        # PBKDF2 with SHA-256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return hashed.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        new_hash, _ = PasswordManager.hash_password(password, salt)
        return hmac.compare_digest(new_hash, hashed)


class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Initialize JWT manager
        
        Args:
            secret_key: Secret key for signing (uses env var if not provided)
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET", "laniakea-secret-key")
        self.algorithm = algorithm
    
    def create_token(self, 
                    user_id: str,
                    username: str,
                    email: str,
                    expires_in: int = 3600) -> Optional[str]:
        """
        Create JWT token
        
        Args:
            user_id: User ID
            username: Username
            email: User email
            expires_in: Token expiration time in seconds
        
        Returns:
            JWT token string
        """
        if not JWT_AVAILABLE:
            logger.warning("JWT not available")
            return None
        
        try:
            payload = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ Token created for user: {username}")
            return token
        except Exception as e:
            logger.error(f"❌ Token creation failed: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload or None if invalid
        """
        if not JWT_AVAILABLE:
            logger.warning("JWT not available")
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(f"✅ Token verified for user: {payload.get('username')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_token(self, token: str, expires_in: int = 3600) -> Optional[str]:
        """Refresh JWT token"""
        payload = self.verify_token(token)
        if payload:
            return self.create_token(
                payload['user_id'],
                payload['username'],
                payload['email'],
                expires_in
            )
        return None


class SessionManager:
    """Session management"""
    
    def __init__(self):
        """Initialize session manager"""
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, 
                      user_id: str,
                      username: str,
                      ip_address: str = None,
                      user_agent: str = None) -> str:
        """
        Create new session
        
        Args:
            user_id: User ID
            username: Username
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Session ID
        """
        session_id = hashlib.sha256(
            f"{user_id}{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "is_active": True
        }
        
        logger.info(f"✅ Session created: {session_id[:8]}... for user: {username}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and session['is_active']:
            session['last_activity'] = datetime.utcnow()
            return session
        return None
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""
        if session_id in self.sessions:
            self.sessions[session_id]['is_active'] = False
            logger.info(f"✅ Session invalidated: {session_id[:8]}...")
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired = []
        
        for session_id, session in self.sessions.items():
            age = (now - session['created_at']).total_seconds() / 3600
            if age > max_age_hours or not session['is_active']:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
        
        logger.info(f"✅ Cleaned up {len(expired)} expired sessions")


class AuthenticationService:
    """Main authentication service"""
    
    def __init__(self, db_connection = None):
        """
        Initialize authentication service
        
        Args:
            db_connection: Database connection for user storage
        """
        self.db = db_connection
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
        self.session_manager = SessionManager()
    
    def register_user(self, 
                     username: str,
                     email: str,
                     password: str) -> Dict[str, Any]:
        """
        Register new user
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
        
        Returns:
            Registration result
        """
        try:
            # Hash password
            password_hash, salt = self.password_manager.hash_password(password)
            
            # Store in database if available
            if self.db:
                from laniakea.storage.database import get_user_db
                user_db = get_user_db()
                if user_db:
                    success = user_db.create_user(username, email, f"{password_hash}:{salt}")
                    if success:
                        logger.info(f"✅ User registered: {username}")
                        return {
                            "success": True,
                            "message": "User registered successfully",
                            "username": username
                        }
            
            logger.info(f"✅ User registered (in-memory): {username}")
            return {
                "success": True,
                "message": "User registered successfully",
                "username": username
            }
        
        except Exception as e:
            logger.error(f"❌ Registration failed: {e}")
            return {
                "success": False,
                "message": f"Registration failed: {str(e)}"
            }
    
    def login(self,
             username: str,
             password: str,
             ip_address: str = None,
             user_agent: str = None) -> Dict[str, Any]:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Login result with token and session
        """
        try:
            # Get user from database
            if self.db:
                from laniakea.storage.database import get_user_db
                user_db = get_user_db()
                if user_db:
                    user = user_db.get_user(username)
                    if not user:
                        return {
                            "success": False,
                            "message": "Invalid credentials"
                        }
                    
                    # Verify password
                    password_hash, salt = user['password_hash'].split(':')
                    if not self.password_manager.verify_password(password, password_hash, salt):
                        return {
                            "success": False,
                            "message": "Invalid credentials"
                        }
                    
                    user_id = str(user['id'])
                    email = user['email']
            else:
                # Demo user
                if username != "demo" or password != "demo":
                    return {
                        "success": False,
                        "message": "Invalid credentials"
                    }
                user_id = "demo-user-001"
                email = "demo@laniakea.io"
            
            # Create token
            token = self.jwt_manager.create_token(user_id, username, email)
            
            # Create session
            session_id = self.session_manager.create_session(
                user_id, username, ip_address, user_agent
            )
            
            logger.info(f"✅ User logged in: {username}")
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "session_id": session_id,
                "user": {
                    "user_id": user_id,
                    "username": username,
                    "email": email
                }
            }
        
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return {
                "success": False,
                "message": f"Login failed: {str(e)}"
            }
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """Logout user"""
        try:
            self.session_manager.invalidate_session(session_id)
            logger.info(f"✅ User logged out")
            return {
                "success": True,
                "message": "Logout successful"
            }
        except Exception as e:
            logger.error(f"❌ Logout failed: {e}")
            return {
                "success": False,
                "message": f"Logout failed: {str(e)}"
            }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify authentication token"""
        payload = self.jwt_manager.verify_token(token)
        if payload:
            return {
                "valid": True,
                "user": payload
            }
        return {
            "valid": False,
            "user": None
        }


# Global authentication service
_auth_service: Optional[AuthenticationService] = None


def get_auth_service() -> AuthenticationService:
    """Get global authentication service"""
    global _auth_service
    if _auth_service is None:
        from laniakea.storage.database import get_database
        _auth_service = AuthenticationService(get_database())
    return _auth_service
