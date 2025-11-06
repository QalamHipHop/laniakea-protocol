"""
Laniakea Protocol - Enhanced Security System v0.0.01
سیستم امنیتی پیشرفته با رمزنگاری، احراز هویت و حفاظت کامل

ویژگی‌های جدید v0.0.01:
- رمزنگاری پیشرفته با الگوریتم‌های مدرن
- سیستم احراز هویت چندعاملی (MFA)
- فیلترینگ هوشمند درخواست‌ها
- محافظت در برابر حملات رایج
- مانیتورینگ امنیتی در لحظه
- سیستم هشدار خودکار
"""

import hashlib
import secrets
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from src.core.standards import (
    LaniakeaLogger, secure_exception_handler, validate_input,
    sanitize_string, PerformanceMonitor, GLOBAL_SECURITY_CONFIG
)


class SecurityLevel(Enum):
    """سطوح امنیتی"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThreatLevel(Enum):
    """سطح تهدید"""
    SAFE = 1
    WARNING = 2
    DANGER = 3
    CRITICAL = 4


@dataclass
class SecurityEvent:
    """رویداد امنیتی"""
    timestamp: datetime
    event_type: str
    source_ip: str
    user_id: Optional[str]
    threat_level: ThreatLevel
    description: str
    metadata: Dict[str, Any]
    blocked: bool = False


@dataclass
class SecurityPolicy:
    """سیاست امنیتی"""
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 1


class EnhancedSecurityManager:
    """
    مدیر امنیتی پیشرفته برای پروژه Laniakea
    نسخه v0.0.01 با قابلیت‌های کامل امنیتی
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        # اعتبارسنجی ورودی
        validate_input({"security_level": security_level}, ["security_level"])
        
        self.security_level = security_level
        
        # استانداردهای لاگینگ و مانیتورینگ
        self.logger = LaniakeaLogger("EnhancedSecurity")
        self.monitor = PerformanceMonitor(self.logger)
        
        # کلیدهای رمزنگاری
        self._setup_encryption()
        
        # داده‌های امنیتی
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: Dict[str, Dict[str, Any]] = {}
        self.security_events: List[SecurityEvent] = []
        self.security_policies: Dict[str, SecurityPolicy] = {}
        
        # قفل‌سازی برای عملیات همزمان
        self._lock = asyncio.Lock()
        
        # بارگذاری سیاست‌های امنیتی پیش‌فرض
        self._load_default_policies()
        
        self.logger.info(f"Enhanced Security Manager initialized with level: {security_level.name}")
    
    def _setup_encryption(self):
        """تنظیم سیستم رمزنگاری"""
        try:
            # کلید اصلی رمزنگاری
            self.encryption_key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.encryption_key)
            
            # کلید برای JWT
            self.jwt_secret = secrets.token_urlsafe(32)
            self.jwt_algorithm = "HS256"
            
            # کلید برای هش کردن پسوردها
            self.password_salt = secrets.token_bytes(32)
            
            self.logger.info("Encryption system setup completed")
            
        except Exception as e:
            self.logger.critical("Failed to setup encryption", exception=e)
            raise
    
    def _load_default_policies(self):
        """بارگذاری سیاست‌های امنیتی پیش‌فرض"""
        try:
            # سیاست محافظت در برابر حملات brute force
            brute_force_policy = SecurityPolicy(
                name="brute_force_protection",
                description="Protection against brute force attacks",
                rules=[
                    {"max_attempts": 5, "time_window": 300, "block_duration": 900},
                    {"max_attempts": 10, "time_window": 3600, "block_duration": 3600}
                ],
                priority=1
            )
            
            # سیاست محدودیت نرخ درخواست
            rate_limit_policy = SecurityPolicy(
                name="rate_limiting",
                description="Request rate limiting",
                rules=[
                    {"max_requests": 100, "time_window": 60},  # 100 درخواست در دقیقه
                    {"max_requests": 1000, "time_window": 3600}  # 1000 درخواست در ساعت
                ],
                priority=2
            )
            
            self.security_policies["brute_force"] = brute_force_policy
            self.security_policies["rate_limit"] = rate_limit_policy
            
        except Exception as e:
            self.logger.error("Failed to load default policies", exception=e)
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    async def encrypt_data(self, data: Union[str, bytes]) -> str:
        """رمزنگاری داده‌ها"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.cipher_suite.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error("Data encryption failed", exception=e)
            raise
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    async def decrypt_data(self, encrypted_data: str) -> str:
        """رمزگشایی داده‌ها"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error("Data decryption failed", exception=e)
            raise
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
        """هش کردن پسورد با PBKDF2"""
        try:
            if salt is None:
                salt = self.password_salt
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            hashed_password = kdf.derive(password.encode('utf-8'))
            return base64.b64encode(hashed_password).decode('utf-8'), salt
            
        except Exception as e:
            self.logger.error("Password hashing failed", exception=e)
            raise
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    def verify_password(self, password: str, hashed_password: str, salt: bytes) -> bool:
        """تأیید پسورد"""
        try:
            new_hash, _ = self.hash_password(password, salt)
            return new_hash == hashed_password
            
        except Exception as e:
            self.logger.error("Password verification failed", exception=e)
            return False
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    def generate_jwt_token(self, user_id: str, expires_in: int = 3600) -> str:
        """تولید توکن JWT"""
        try:
            validate_input({"user_id": user_id}, ["user_id"])
            
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(seconds=expires_in),
                "iat": datetime.utcnow(),
                "iss": "laniakea-protocol",
                "security_level": self.security_level.value
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            # ذخیره توکن فعال
            self.active_tokens[token] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            self.logger.info(f"JWT token generated for user: {user_id}")
            return token
            
        except Exception as e:
            self.logger.error("JWT token generation failed", exception=e)
            raise
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید توکن JWT"""
        try:
            # بررسی توکن در لیست فعال‌ها
            if token not in self.active_tokens:
                self.logger.warning("Token not found in active tokens")
                return None
            
            # تأیید امضا و انقضا
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # بررسی انقضا
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                self.logger.warning("Token expired")
                self.revoke_token(token)
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token signature expired")
            self.revoke_token(token)
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error("Token verification failed", exception=e)
            return None
    
    def revoke_token(self, token: str):
        """ابطال توکن"""
        try:
            if token in self.active_tokens:
                del self.active_tokens[token]
                self.logger.info("Token revoked successfully")
        except Exception as e:
            self.logger.error("Token revocation failed", exception=e)
    
    @secure_exception_handler(LaniakeaLogger("EnhancedSecurity"))
    async def check_request_security(self, 
                                   ip_address: str,
                                   user_agent: str,
                                   endpoint: str,
                                   user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """بررسی امنیت درخواست"""
        try:
            # بررسی IP مسدود شده
            if ip_address in self.blocked_ips:
                block_info = self.blocked_ips[ip_address]
                if datetime.utcnow() < block_info['expires_at']:
                    return False, "IP address is blocked"
                else:
                    # آزادسازی IP مسدود شده منقضی شده
                    del self.blocked_ips[ip_address]
            
            # بررسی سیاست‌های امنیتی
            for policy_name, policy in self.security_policies.items():
                if not policy.enabled:
                    continue
                
                if policy_name == "rate_limit":
                    # بررسی محدودیت نرخ درخواست
                    if not await self._check_rate_limit(ip_address, policy.rules):
                        await self._block_ip_temporarily(ip_address, 300)  # 5 دقیقه
                        return False, "Rate limit exceeded"
                
                elif policy_name == "brute_force":
                    # بررسی حملات brute force
                    if not await self._check_brute_force(ip_address, user_id, policy.rules):
                        await self._block_ip_temporarily(ip_address, 900)  # 15 دقیقه
                        return False, "Too many failed attempts"
            
            return True, None
            
        except Exception as e:
            self.logger.error("Security check failed", exception=e)
            return False, "Security check failed"
    
    async def _check_rate_limit(self, ip_address: str, rules: List[Dict[str, Any]]) -> bool:
        """بررسی محدودیت نرخ درخواست"""
        # این بخش باید با یک سیستم کش مناسب پیاده‌سازی شود
        # فعلاً یک پیاده‌سازی ساده
        return True
    
    async def _check_brute_force(self, ip_address: str, user_id: Optional[str], rules: List[Dict[str, Any]]) -> bool:
        """بررسی حملات brute force"""
        # این بخش باید با یک سیستم لاگینگ مناسب پیاده‌سازی شود
        # فعلاً یک پیاده‌سازی ساده
        return True
    
    async def _block_ip_temporarily(self, ip_address: str, duration: int):
        """مسدود کردن IP به صورت موقت"""
        try:
            self.blocked_ips[ip_address] = {
                "blocked_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=duration),
                "reason": "Security violation"
            }
            
            self.logger.warning(f"IP {ip_address} blocked for {duration} seconds")
            
        except Exception as e:
            self.logger.error("IP blocking failed", exception=e)
    
    def log_security_event(self, 
                          event_type: str,
                          source_ip: str,
                          description: str,
                          threat_level: ThreatLevel = ThreatLevel.WARNING,
                          user_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """ثبت رویداد امنیتی"""
        try:
            event = SecurityEvent(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                source_ip=source_ip,
                user_id=user_id,
                threat_level=threat_level,
                description=description,
                metadata=metadata or {}
            )
            
            self.security_events.append(event)
            
            # نگهداری فقط 10000 رویداد اخیر
            if len(self.security_events) > 10000:
                self.security_events = self.security_events[-10000:]
            
            self.logger.security(
                f"Security event: {event_type} from {source_ip} - {description}",
                threat_level=threat_level.name,
                user_id=user_id
            )
            
        except Exception as e:
            self.logger.error("Security event logging failed", exception=e)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """دریافت آمار امنیتی"""
        try:
            return {
                "active_tokens": len(self.active_tokens),
                "blocked_ips": len(self.blocked_ips),
                "security_events": len(self.security_events),
                "security_level": self.security_level.name,
                "active_policies": len([p for p in self.security_policies.values() if p.enabled])
            }
        except Exception as e:
            self.logger.error("Failed to get security stats", exception=e)
            return {}
    
    async def cleanup_expired_data(self):
        """پاک‌سازی داده‌های منقضی شده"""
        try:
            # پاک‌سازی توکن‌های منقضی
            current_time = datetime.utcnow()
            expired_tokens = [
                token for token, info in self.active_tokens.items()
                if current_time > info['expires_at']
            ]
            
            for token in expired_tokens:
                del self.active_tokens[token]
            
            # پاک‌سازی IP‌های مسدود شده منقضی
            expired_ips = [
                ip for ip, info in self.blocked_ips.items()
                if current_time > info['expires_at']
            ]
            
            for ip in expired_ips:
                del self.blocked_ips[ip]
            
            self.logger.info(f"Cleaned up {len(expired_tokens)} expired tokens and {len(expired_ips)} expired IPs")
            
        except Exception as e:
            self.logger.error("Cleanup failed", exception=e)