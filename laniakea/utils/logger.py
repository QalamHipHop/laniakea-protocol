"""
LaniakeA Protocol - Advanced Logging System
Comprehensive logging with developer mode, error tracking, and performance monitoring
Version: 3.0.0
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for beautiful terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis for different log levels"""
    
    # Emoji and color mapping for each log level
    FORMATS = {
        logging.DEBUG: f"{Colors.BRIGHT_BLACK}🔍 [DEBUG]{Colors.RESET} %(message)s {Colors.DIM}(%(filename)s:%(lineno)d){Colors.RESET}",
        logging.INFO: f"{Colors.BRIGHT_CYAN}ℹ️  [INFO]{Colors.RESET} %(message)s",
        logging.WARNING: f"{Colors.BRIGHT_YELLOW}⚠️  [WARNING]{Colors.RESET} %(message)s",
        logging.ERROR: f"{Colors.BRIGHT_RED}❌ [ERROR]{Colors.RESET} %(message)s {Colors.DIM}(%(filename)s:%(lineno)d){Colors.RESET}",
        logging.CRITICAL: f"{Colors.RED}{Colors.BOLD}🚨 [CRITICAL]{Colors.RESET} %(message)s"
    }
    
    def format(self, record):
        # Get the format for this log level
        log_fmt = self.FORMATS.get(record.levelno, "%(message)s")
        
        # Add timestamp in developer mode
        if hasattr(record, 'dev_mode') and record.dev_mode:
            timestamp = f"{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}]{Colors.RESET} "
            log_fmt = timestamp + log_fmt
        
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class DeveloperModeFilter(logging.Filter):
    """Filter to add developer mode flag to log records"""
    
    def __init__(self, dev_mode: bool = False):
        super().__init__()
        self.dev_mode = dev_mode
    
    def filter(self, record):
        record.dev_mode = self.dev_mode
        return True


class PerformanceLogger:
    """Logger for performance metrics and profiling"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def log_metric(self, name: str, value: float, unit: str = ''):
        """Log a performance metric"""
        self.metrics[name] = {
            'value': value,
            'unit': unit,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.debug(f"📊 Metric: {name} = {value} {unit}")
    
    def log_timing(self, operation: str, duration: float):
        """Log operation timing"""
        self.log_metric(f"{operation}_duration", duration, 'ms')
        
        # Warn if operation is slow
        if duration > 1000:  # > 1 second
            self.logger.warning(f"⏱️  Slow operation: {operation} took {duration:.2f}ms")
    
    def get_metrics(self):
        """Get all collected metrics"""
        return self.metrics


class ErrorTracker:
    """Track and analyze errors for debugging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.errors = []
        self.error_counts = {}
    
    def track_error(self, error: Exception, context: dict = None):
        """Track an error with context"""
        error_data = {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.errors.append(error_data)
        
        # Count error types
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        self.logger.error(
            f"Error tracked: {error_type} - {str(error)}",
            extra={'extra_data': error_data}
        )
    
    def get_error_summary(self):
        """Get summary of tracked errors"""
        return {
            'total_errors': len(self.errors),
            'error_counts': self.error_counts,
            'recent_errors': self.errors[-10:]  # Last 10 errors
        }


def setup_logger(
    name: str = 'laniakea',
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    dev_mode: bool = False,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup comprehensive logging system
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        dev_mode: Enable developer mode with extra features
        json_format: Use JSON format for structured logging
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    console_handler.addFilter(DeveloperModeFilter(dev_mode))
    logger.addHandler(console_handler)
    
    # File handler if log file specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        # Use JSON format for file logs
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Add performance logger and error tracker as attributes
    logger.performance = PerformanceLogger(logger)
    logger.error_tracker = ErrorTracker(logger)
    
    # Log initial message
    if dev_mode:
        logger.info("🔧 Logger initialized in DEVELOPER MODE")
        logger.debug(f"Log level: {logging.getLevelName(log_level)}")
        if log_file:
            logger.debug(f"Log file: {log_file}")
    else:
        logger.info("📝 Logger initialized")
    
    return logger


def get_logger(name: str = 'laniakea') -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)


class LogContext:
    """Context manager for logging with automatic timing"""
    
    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.INFO):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"▶️  Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds() * 1000
        
        if exc_type is not None:
            self.logger.error(
                f"❌ Failed: {self.operation} ({duration:.2f}ms)",
                exc_info=(exc_type, exc_val, exc_tb)
            )
            if hasattr(self.logger, 'error_tracker'):
                self.logger.error_tracker.track_error(
                    exc_val,
                    {'operation': self.operation, 'duration_ms': duration}
                )
        else:
            self.logger.log(self.level, f"✅ Completed: {self.operation} ({duration:.2f}ms)")
            if hasattr(self.logger, 'performance'):
                self.logger.performance.log_timing(self.operation, duration)
        
        return False  # Don't suppress exceptions


# Convenience function for timing operations
def log_operation(logger: logging.Logger, operation: str, level: int = logging.INFO):
    """Decorator for logging operations with automatic timing"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with LogContext(logger, operation, level):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage and testing
if __name__ == '__main__':
    # Setup logger in dev mode
    logger = setup_logger('test', log_level=logging.DEBUG, dev_mode=True, log_file='test.log')
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test log context
    with LogContext(logger, "Test Operation"):
        import time
        time.sleep(0.1)
    
    # Test error tracking
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error_tracker.track_error(e, {'test': 'context'})
    
    # Test performance logging
    logger.performance.log_metric("test_metric", 42.5, "units")
    
    # Print summaries
    print("\nError Summary:")
    print(json.dumps(logger.error_tracker.get_error_summary(), indent=2, default=str))
    
    print("\nPerformance Metrics:")
    print(json.dumps(logger.performance.get_metrics(), indent=2, default=str))
