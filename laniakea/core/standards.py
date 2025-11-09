"""
Laniakea Protocol - Code Standards & Best Practices

استانداردهای کدنویسی و بهترین شیوه‌ها برای پروژه Laniakea v0.0.01

این فایل شامل:
- استانداردهای کدنویسی
- الگوهای امنیتی
- بهترین شیوه‌های مدیریت خطا
- قالب‌بندی و مستندسازی
"""

import logging
import asyncio
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import traceback
from functools import wraps
import time


class LogLevel(Enum):
    """سطوح لاگ استاندارد"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class SecurityConfig:
    """پیکربندی امنیتی استاندارد"""
    max_retries: int = 3
    timeout_seconds: int = 30
    rate_limit_per_minute: int = 100
    enable_audit_log: bool = True


class LaniakeaLogger:
    """لاگکن استاندارد برای پروژه"""
    
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # استانداردسازی فرمت لاگ
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Handler برای کنسول
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """لاگ سطح DEBUG"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """لاگ سطح INFO"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """لاگ سطح WARNING"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """لاگ سطح ERROR با جزئیات exception"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """لاگ سطح CRITICAL"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)


def secure_exception_handler(logger: LaniakeaLogger):
    """دکوراتور برای مدیریت امن خطا"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"ValueError in {func.__name__}", exception=e)
                raise
            except TypeError as e:
                logger.error(f"TypeError in {func.__name__}", exception=e)
                raise
            except PermissionError as e:
                logger.error(f"PermissionError in {func.__name__}", exception=e)
                raise
            except TimeoutError as e:
                logger.error(f"TimeoutError in {func.__name__}", exception=e)
                raise
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}", exception=e)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                logger.error(f"ValueError in {func.__name__}", exception=e)
                raise
            except TypeError as e:
                logger.error(f"TypeError in {func.__name__}", exception=e)
                raise
            except PermissionError as e:
                logger.error(f"PermissionError in {func.__name__}", exception=e)
                raise
            except TimeoutError as e:
                logger.error(f"TimeoutError in {func.__name__}", exception=e)
                raise
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}", exception=e)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """اعتبارسنجی ورودی‌ها"""
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Required field '{field}' is missing or null")
    return True


def sanitize_string(input_string: str, max_length: int = 1000) -> str:
    """پاکسازی ورودی‌های متنی"""
    if not isinstance(input_string, str):
        raise TypeError("Input must be a string")
    
    # حذف کاراکترهای خطرناک
    dangerous_chars = ['<', '>', '&', '"', "'", ';', '(', ')', '{', '}']
    sanitized = input_string
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # محدودیت طول
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


class PerformanceMonitor:
    """مانیتورینگ عملکرد"""
    
    def __init__(self, logger: LaniakeaLogger):
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, operation_name: str):
        """شروع زمان‌سنجی"""
        self.metrics[operation_name] = time.time()
    
    def end_timer(self, operation_name: str) -> float:
        """پایان زمان‌سنجی و ثبت نتیجه"""
        if operation_name not in self.metrics:
            self.logger.warning(f"Timer for '{operation_name}' was not started")
            return 0.0
        
        duration = time.time() - self.metrics[operation_name]
        self.logger.info(f"Operation '{operation_name}' completed in {duration:.4f}s")
        del self.metrics[operation_name]
        return duration


# استانداردهای جهانی برای پروژه
GLOBAL_LOGGER = LaniakeaLogger("Laniakea")
GLOBAL_SECURITY_CONFIG = SecurityConfig()
GLOBAL_PERFORMANCE_MONITOR = PerformanceMonitor(GLOBAL_LOGGER)


# الگوی singleton برای مدیریت منابع
class SingletonMeta(type):
    """متاکلاس برای پیاده‌سازی الگوی Singleton"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# استانداردهای کدنویسی
CODING_STANDARDS = {
    "max_line_length": 88,
    "max_function_length": 50,
    "max_class_length": 300,
    "naming_convention": {
        "classes": "PascalCase",
        "functions": "snake_case",
        "variables": "snake_case",
        "constants": "UPPER_CASE"
    },
    "documentation": {
        "docstring_format": "Google Style",
        "require_type_hints": True,
        "require_examples": True
    }
}