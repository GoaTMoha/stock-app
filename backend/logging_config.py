"""
Logging configuration for the Stock Manager App.
Provides centralized logging with file and console output.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class LoggerConfig:
    """Centralized logging configuration."""
    
    @staticmethod
    def setup_logging(app_name: str = "stock_app", log_level: str = "INFO") -> logging.Logger:
        """
        Set up centralized logging for the application.
        
        Args:
            app_name: Name of the application
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up logger
        logger = logging.getLogger(app_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{app_name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{app_name}_errors.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name (defaults to 'stock_app')
        
        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(name or "stock_app")


class RequestLogger:
    """Request logging utilities."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, user_id: Optional[int] = None):
        """
        Log HTTP request details.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            response_time: Response time in seconds
            user_id: User ID if authenticated
        """
        user_info = f"user_id={user_id}" if user_id else "anonymous"
        
        self.logger.info(
            f"HTTP {method} {path} - {status_code} - "
            f"{response_time:.3f}s - {user_info}"
        )
    
    def log_error(self, error: Exception, context: str = ""):
        """
        Log application errors.
        
        Args:
            error: Exception instance
            context: Additional context information
        """
        context_info = f" - Context: {context}" if context else ""
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}{context_info}",
            exc_info=True
        )


class DatabaseLogger:
    """Database operation logging."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_query(self, query: str, params: Optional[dict] = None, 
                 execution_time: Optional[float] = None):
        """
        Log database queries (for debugging).
        
        Args:
            query: SQL query
            params: Query parameters
            execution_time: Query execution time
        """
        if self.logger.isEnabledFor(logging.DEBUG):
            params_info = f" - Params: {params}" if params else ""
            time_info = f" - Time: {execution_time:.3f}s" if execution_time else ""
            
            self.logger.debug(f"DB Query: {query}{params_info}{time_info}")
    
    def log_transaction(self, operation: str, success: bool, 
                       details: Optional[str] = None):
        """
        Log database transactions.
        
        Args:
            operation: Transaction operation (e.g., 'sale_creation')
            success: Whether transaction succeeded
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        details_info = f" - {details}" if details else ""
        
        self.logger.info(f"Transaction {operation}: {status}{details_info}")


class SecurityLogger:
    """Security event logging."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_auth_attempt(self, email: str, success: bool, ip_address: str):
        """
        Log authentication attempts.
        
        Args:
            email: User email
            success: Whether authentication succeeded
            ip_address: Client IP address
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Auth attempt: {email} - {status} - IP: {ip_address}")
    
    def log_rate_limit(self, endpoint: str, ip_address: str):
        """
        Log rate limit violations.
        
        Args:
            endpoint: API endpoint
            ip_address: Client IP address
        """
        self.logger.warning(f"Rate limit exceeded: {endpoint} - IP: {ip_address}")
    
    def log_suspicious_activity(self, activity: str, ip_address: str, 
                              details: Optional[str] = None):
        """
        Log suspicious activities.
        
        Args:
            activity: Type of suspicious activity
            ip_address: Client IP address
            details: Additional details
        """
        details_info = f" - {details}" if details else ""
        self.logger.warning(
            f"Suspicious activity: {activity} - IP: {ip_address}{details_info}"
        )


def setup_app_logging(app):
    """
    Set up logging for Flask application.
    
    Args:
        app: Flask application instance
    """
    # Get log level from config
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Set up main logger
    logger = LoggerConfig.setup_logging("stock_app", log_level)
    
    # Set Flask app logger
    app.logger = logger
    
    # Set up specialized loggers
    request_logger = RequestLogger(logger)
    db_logger = DatabaseLogger(logger)
    security_logger = SecurityLogger(logger)
    
    # Store loggers in app config for access in routes
    app.config['REQUEST_LOGGER'] = request_logger
    app.config['DB_LOGGER'] = db_logger
    app.config['SECURITY_LOGGER'] = security_logger
    
    # Log application startup
    logger.info(f"Stock Manager App started - Log level: {log_level}")
    
    return logger
