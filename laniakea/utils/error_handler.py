"""
Error handling utilities for Laniakea Protocol

This module provides decorators and utilities for consistent error handling
across the protocol.
"""

import functools
import logging
import traceback
from typing import Callable, Any, Type, Optional
from laniakea.core.exceptions import LaniakeaException, get_error_code

logger = logging.getLogger(__name__)


def handle_errors(
    error_class: Type[LaniakeaException] = LaniakeaException,
    log_traceback: bool = True,
    reraise: bool = True,
    default_return: Any = None
):
    """
    Decorator for handling errors in functions with consistent logging
    
    Args:
        error_class: The exception class to catch and handle
        log_traceback: Whether to log full traceback
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return if not reraising
    
    Usage:
        @handle_errors(BlockchainError)
        def my_function():
            ...
        
        @handle_errors(reraise=False, default_return=[])
        async def my_async_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except error_class as e:
                error_code = get_error_code(e)
                logger.error(
                    f"[{error_code}] Error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'error_code': error_code,
                        'error_type': type(e).__name__,
                        'details': getattr(e, 'details', {})
                    }
                )
                
                if log_traceback:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                return default_return
                
            except Exception as e:
                logger.exception(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'error_type': type(e).__name__
                    }
                )
                
                if reraise:
                    # Wrap unexpected errors in the specified error class
                    raise error_class(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        details={'original_error': str(e)}
                    ) from e
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_class as e:
                error_code = get_error_code(e)
                logger.error(
                    f"[{error_code}] Error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'error_code': error_code,
                        'error_type': type(e).__name__,
                        'details': getattr(e, 'details', {})
                    }
                )
                
                if log_traceback:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                return default_return
                
            except Exception as e:
                logger.exception(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'error_type': type(e).__name__
                    }
                )
                
                if reraise:
                    # Wrap unexpected errors in the specified error class
                    raise error_class(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        details={'original_error': str(e)}
                    ) from e
                return default_return
        
        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def safe_execute(
    func: Callable,
    *args,
    error_class: Type[LaniakeaException] = LaniakeaException,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_class: Exception class to catch
        default_return: Value to return on error
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or default_return on error
    
    Usage:
        result = safe_execute(risky_function, arg1, arg2, default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except error_class as e:
        error_code = get_error_code(e)
        logger.error(
            f"[{error_code}] Error in safe_execute({func.__name__}): {str(e)}",
            extra={
                'function': func.__name__,
                'error_code': error_code,
                'error_type': type(e).__name__
            }
        )
        return default_return
    except Exception as e:
        logger.exception(
            f"Unexpected error in safe_execute({func.__name__}): {str(e)}",
            extra={
                'function': func.__name__,
                'error_type': type(e).__name__
            }
        )
        return default_return


class ErrorContext:
    """
    Context manager for error handling
    
    Usage:
        with ErrorContext(BlockchainError, "Mining operation"):
            # risky code here
            mine_block()
    """
    
    def __init__(
        self,
        error_class: Type[LaniakeaException] = LaniakeaException,
        operation_name: str = "Operation",
        reraise: bool = True,
        log_traceback: bool = True
    ):
        self.error_class = error_class
        self.operation_name = operation_name
        self.reraise = reraise
        self.log_traceback = log_traceback
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        if issubclass(exc_type, self.error_class):
            error_code = get_error_code(exc_val)
            logger.error(
                f"[{error_code}] Error in {self.operation_name}: {str(exc_val)}",
                extra={
                    'operation': self.operation_name,
                    'error_code': error_code,
                    'error_type': exc_type.__name__
                }
            )
            
            if self.log_traceback:
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            return not self.reraise
        
        # Unexpected error
        logger.exception(
            f"Unexpected error in {self.operation_name}: {str(exc_val)}",
            extra={
                'operation': self.operation_name,
                'error_type': exc_type.__name__
            }
        )
        
        if self.reraise:
            # Wrap in error_class
            raise self.error_class(
                f"Unexpected error in {self.operation_name}: {str(exc_val)}",
                details={'original_error': str(exc_val)}
            ) from exc_val
        
        return True


def validate_parameters(**validators):
    """
    Decorator for validating function parameters
    
    Args:
        **validators: Dictionary of parameter_name: validation_function
    
    Usage:
        @validate_parameters(
            amount=lambda x: x > 0,
            address=lambda x: len(x) == 42
        )
        def transfer(amount, address):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate parameters
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        from laniakea.core.exceptions import InvalidParameterError
                        raise InvalidParameterError(
                            f"Invalid parameter '{param_name}': {value}",
                            details={
                                'parameter': param_name,
                                'value': value,
                                'function': func.__name__
                            }
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function on error
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch
    
    Usage:
        @retry_on_error(max_retries=3, delay=1.0)
        def unreliable_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
