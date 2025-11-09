# laniakea/utils/logger.py

import logging
import sys
from laniakea.core.config import settings

def setup_logger(name: str = "laniakea", level: str = "INFO") -> logging.Logger:
    """
    Sets up a standardized logger for the Laniakea Protocol.
    """
    logger = logging.getLogger(name)
    
    # Map deployment environment to log level
    level_map = {'development': 'DEBUG', 'production': 'INFO', 'testing': 'DEBUG'}
    log_level = level_map.get(level.lower(), 'INFO')
    
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        # Create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(log_level)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(ch)
        
    return logger

def get_logger(name: str = "laniakea") -> logging.Logger:
    """
    Gets or creates a logger instance.
    """
    return logging.getLogger(name)

# Global logger instance
logger = setup_logger(level=settings.DEPLOYMENT_ENV if hasattr(settings, 'DEPLOYMENT_ENV') else 'INFO')

if __name__ == '__main__':
    logger.info("Logger initialized successfully.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
