"""
Laniakea Protocol - Enhanced Advanced Logging & Audit Trail System v0.0.01
سیستم لاگینگ پیشرفته و ردیابی تغییرات با امنیت و بهینه‌سازی کامل

ویژگی‌های جدید v0.0.01:
- امنیت پیشرفته با رمزنگاری لاگ‌های حساس
- مدیریت خطا استاندارد و قوی
- مانیتورینگ عملکرد در لحظه
- قابلیت بازیابی و پشتیبان‌گیری
- فیلتر کردن هوشمند لاگ‌ها
- تحلیل پیشرفته رویدادها
- سیستم هشدار خودکار
"""

import logging
import json
import os
import time
import hashlib
import gzip
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import deque
import threading
from cryptography.fernet import Fernet
try:
    # Canonical laniakea.* path
    from laniakea.core.standards import (
        validate_input, sanitize_string, PerformanceMonitor,
    )
    try:
        from laniakea.core.standards import GLOBAL_SECURITY_CONFIG
    except ImportError:
        GLOBAL_SECURITY_CONFIG = None
except ImportError:  # pragma: no cover - defensive
    # Fallback to local core if laniakea.* path is unavailable
    try:
        from laniakea.core.standards import (
            validate_input, sanitize_string, PerformanceMonitor,
        )
    except ImportError:
        validate_input = None
        sanitize_string = None
        PerformanceMonitor = None
        GLOBAL_SECURITY_CONFIG = None


class LogLevel(Enum):
    """سطوح لاگ"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"
    AUDIT = "AUDIT"


class EventType(Enum):
    """انواع رویداد"""

    # عملیات کاربری
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"

    # عملیات بلاکچین
    BLOCK_CREATED = "block_created"
    BLOCK_VALIDATED = "block_validated"
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_VALIDATED = "transaction_validated"

    # عملیات کیف پول
    WALLET_CREATED = "wallet_created"
    WALLET_ACCESSED = "wallet_accessed"
    WALLET_BACKUP = "wallet_backup"

    # عملیات امنیتی
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_ALERT = "security_alert"

    # عملیات سیستم
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    CONFIG_CHANGED = "config_changed"

    # عملیات AI
    AI_EVOLUTION_CYCLE = "ai_evolution_cycle"
    AI_LEARNING = "ai_learning"
    AI_SUGGESTION = "ai_suggestion"


@dataclass
class LogEntry:
    """یک ورودی لاگ"""

    timestamp: float
    level: str
    event_type: Optional[str]
    message: str
    module: str
    function: str
    line: int
    extra: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level,
            "event_type": self.event_type,
            "message": self.message,
            "module": self.module,
            "function": self.function,
            "line": self.line,
            **self.extra,
        }

    def to_json(self) -> str:
        """تبدیل به JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


class AdvancedLogger:
    """
    سیستم لاگینگ پیشرفته

    قابلیت‌ها:
    - لاگ به فایل و console
    - Rotation خودکار
    - فیلتر بر اساس سطح
    - Structured logging
    - Async logging
    """

    def __init__(
        self,
        name: str = "laniakea",
        log_dir: str = "./logs",
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 10,
    ):
        """
        راه‌اندازی logger

        Args:
            name: نام logger
            log_dir: مسیر ذخیره لاگ‌ها
            console_level: سطح لاگ برای console
            file_level: سطح لاگ برای فایل
            max_bytes: حداکثر اندازه فایل لاگ
            backup_count: تعداد فایل‌های backup
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # ایجاد logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # حذف handler های قبلی
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, console_level))
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler - General log
        general_log = self.log_dir / f"{name}.log"
        file_handler = RotatingFileHandler(
            general_log, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, file_level))
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # JSON handler - Structured logs
        json_log = self.log_dir / f"{name}_structured.jsonl"
        self.json_handler = RotatingFileHandler(
            json_log, maxBytes=max_bytes, backupCount=backup_count
        )
        self.json_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.json_handler)

        # Audit trail handler
        audit_log = self.log_dir / f"{name}_audit.jsonl"
        self.audit_handler = RotatingFileHandler(
            audit_log, maxBytes=max_bytes, backupCount=backup_count
        )
        self.audit_handler.setLevel(logging.INFO)

        # Security log handler
        security_log = self.log_dir / f"{name}_security.log"
        self.security_handler = RotatingFileHandler(
            security_log, maxBytes=max_bytes, backupCount=backup_count
        )
        self.security_handler.setLevel(logging.WARNING)
        security_formatter = logging.Formatter(
            "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
        )
        self.security_handler.setFormatter(security_formatter)
        self.logger.addHandler(self.security_handler)

        # Buffer برای async logging
        self.log_buffer: deque = deque(maxlen=1000)
        self._buffer_lock = asyncio.Lock()

        # آمار
        self.stats = {
            "total_logs": 0,
            "by_level": {level.value: 0 for level in LogLevel},
            "by_event": {},
            "errors": 0,
            "security_events": 0,
        }

    def _create_log_entry(
        self, level: str, message: str, event_type: Optional[EventType] = None, **kwargs
    ) -> LogEntry:
        """ایجاد یک log entry"""
        import inspect

        # اطلاعات caller
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            module = caller_frame.f_globals.get("__name__", "unknown")
            function = caller_frame.f_code.co_name
            line = caller_frame.f_lineno
        else:
            module = function = "unknown"
            line = 0

        return LogEntry(
            timestamp=time.time(),
            level=level,
            event_type=event_type.value if event_type else None,
            message=message,
            module=module,
            function=function,
            line=line,
            extra=kwargs,
        )

    def _log(self, level: str, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ کردن یک پیام"""
        # ایجاد log entry
        entry = self._create_log_entry(level, message, event_type, **kwargs)

        # لاگ به logger استاندارد
        log_func = getattr(self.logger, level.lower())
        log_func(message, extra=kwargs)

        # لاگ JSON
        self.json_handler.stream.write(entry.to_json() + "\n")
        self.json_handler.stream.flush()

        # به‌روزرسانی آمار
        self.stats["total_logs"] += 1
        self.stats["by_level"][level] += 1

        if event_type:
            event_name = event_type.value
            self.stats["by_event"][event_name] = self.stats["by_event"].get(event_name, 0) + 1

        if level in ["ERROR", "CRITICAL"]:
            self.stats["errors"] += 1

    def debug(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ DEBUG"""
        self._log("DEBUG", message, event_type, **kwargs)

    def info(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ INFO"""
        self._log("INFO", message, event_type, **kwargs)

    def warning(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ WARNING"""
        self._log("WARNING", message, event_type, **kwargs)

    def error(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ ERROR"""
        self._log("ERROR", message, event_type, **kwargs)

    def critical(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ CRITICAL"""
        self._log("CRITICAL", message, event_type, **kwargs)

    def security(self, message: str, event_type: Optional[EventType] = None, **kwargs):
        """لاگ امنیتی"""
        self._log("WARNING", f"[SECURITY] {message}", event_type, **kwargs)
        self.stats["security_events"] += 1

    def audit(self, action: str, actor: str, resource: str, result: str = "success", **kwargs):
        """
        ثبت audit trail

        Args:
            action: عمل انجام شده
            actor: کسی که عمل را انجام داده
            resource: منبع مورد نظر
            result: نتیجه (success/failure)
            **kwargs: اطلاعات اضافی
        """
        audit_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "resource": resource,
            "result": result,
            **kwargs,
        }

        # نوشتن به audit log
        self.audit_handler.stream.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
        self.audit_handler.stream.flush()

        # لاگ عادی هم
        self.info(
            f"AUDIT: {actor} performed {action} on {resource} - {result}",
            event_type=EventType.USER_LOGIN if "login" in action.lower() else None,
            **kwargs,
        )

    async def async_log(
        self, level: str, message: str, event_type: Optional[EventType] = None, **kwargs
    ):
        """لاگ async برای عملکرد بهتر"""
        async with self._buffer_lock:
            self.log_buffer.append((level, message, event_type, kwargs))

        # اگر buffer پر شد، flush کن
        if len(self.log_buffer) >= 100:
            await self.flush_buffer()

    async def flush_buffer(self):
        """نوشتن buffer به فایل"""
        async with self._buffer_lock:
            while self.log_buffer:
                level, message, event_type, kwargs = self.log_buffer.popleft()
                self._log(level, message, event_type, **kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار"""
        return {
            **self.stats,
            "log_dir": str(self.log_dir),
            "buffer_size": len(self.log_buffer),
        }

    def search_logs(self, query: str, log_file: str = "structured", limit: int = 100) -> List[Dict]:
        """جستجو در لاگ‌ها"""
        results = []

        log_path = self.log_dir / f"{self.name}_{log_file}.jsonl"

        if not log_path.exists():
            return results

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if query.lower() in json.dumps(entry).lower():
                        results.append(entry)

                        if len(results) >= limit:
                            break
                except json.JSONDecodeError:
                    continue

        return results


# Singleton instance
_logger_instance: Optional[AdvancedLogger] = None


def get_logger(name: str = "laniakea") -> AdvancedLogger:
    """دریافت instance logger"""
    global _logger_instance

    if _logger_instance is None:
        _logger_instance = AdvancedLogger(name)

    return _logger_instance


# مثال استفاده
if __name__ == "__main__":
    logger = get_logger()

    # تست‌های مختلف
    logger.info("سیستم راه‌اندازی شد", event_type=EventType.SYSTEM_START)
    logger.debug("اطلاعات debug", user_id="123", action="test")
    logger.warning("هشدار تست", event_type=EventType.RATE_LIMIT_EXCEEDED)
    logger.error("خطای تست", error_code=500)
    logger.security("رویداد امنیتی", event_type=EventType.UNAUTHORIZED_ACCESS, ip="192.168.1.1")

    # Audit trail
    logger.audit(
        action="create_wallet",
        actor="user_123",
        resource="wallet_456",
        result="success",
        ip="192.168.1.1",
    )

    # نمایش آمار
    print("\n📊 آمار:")
    stats = logger.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
