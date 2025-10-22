"""
Production configuration and deployment utilities for the Stock Manager App.
"""

import os
import logging
from typing import Dict, Any


class ProductionConfig:
    """Production-specific configuration and utilities."""
    
    @staticmethod
    def get_production_env_vars() -> Dict[str, str]:
        """
        Get recommended production environment variables.
        
        Returns:
            Dict[str, str]: Environment variables for production
        """
        return {
            "FLASK_ENV": "production",
            "SECRET_KEY": "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY",
            "DATABASE_URL": "postgresql://user:password@localhost/stock_db",
            "WTF_CSRF_ENABLED": "True",
            "SESSION_COOKIE_SECURE": "True",
            "SESSION_COOKIE_HTTPONLY": "True",
            "SESSION_COOKIE_SAMESITE": "Strict",
            "RATELIMIT_STORAGE_URL": "redis://localhost:6379",
            "LOG_LEVEL": "WARNING",
            "BCRYPT_LOG_ROUNDS": "13",
        }
    
    @staticmethod
    def validate_production_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate production configuration.
        
        Args:
            config: Configuration dictionary
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check required settings
        if config.get("FLASK_ENV") != "production":
            errors.append("FLASK_ENV must be set to 'production'")
        
        if not config.get("SECRET_KEY") or len(config.get("SECRET_KEY", "")) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long")
        
        if not config.get("DATABASE_URL"):
            errors.append("DATABASE_URL is required")
        
        if not config.get("WTF_CSRF_ENABLED", "").lower() == "true":
            errors.append("WTF_CSRF_ENABLED must be True in production")
        
        if not config.get("SESSION_COOKIE_SECURE", "").lower() == "true":
            errors.append("SESSION_COOKIE_SECURE must be True in production")
        
        return len(errors) == 0, errors


class DeploymentUtils:
    """Deployment utility functions."""
    
    @staticmethod
    def create_gunicorn_config() -> str:
        """
        Create Gunicorn configuration file content.
        
        Returns:
            str: Gunicorn configuration content
        """
        return """
# Gunicorn configuration for Stock Manager App
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "stock_manager_app"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
"""
    
    @staticmethod
    def create_systemd_service() -> str:
        """
        Create systemd service file content.
        
        Returns:
            str: systemd service file content
        """
        return """
[Unit]
Description=Stock Manager App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/stock-app
Environment=PATH=/opt/stock-app/venv/bin
ExecStart=/opt/stock-app/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    @staticmethod
    def create_nginx_config() -> str:
        """
        Create Nginx configuration file content.
        
        Returns:
            str: Nginx configuration content
        """
        return """
server {
    listen 80;
    server_name your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files (if any)
    location /static {
        alias /opt/stock-app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/stock_app_access.log;
    error_log /var/log/nginx/stock_app_error.log;
}
"""
    
    @staticmethod
    def create_dockerfile() -> str:
        """
        Create Dockerfile content.
        
        Returns:
            str: Dockerfile content
        """
        return """
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"]
"""
    
    @staticmethod
    def create_docker_compose() -> str:
        """
        Create docker-compose.yml content.
        
        Returns:
            str: docker-compose.yml content
        """
        return """
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/stock_db
      - SECRET_KEY=your-secret-key-here
      - WTF_CSRF_ENABLED=True
      - SESSION_COOKIE_SECURE=True
      - RATELIMIT_STORAGE_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=stock_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""


class HealthCheck:
    """Application health check utilities."""
    
    @staticmethod
    def check_database_connection():
        """
        Check database connection health.
        
        Returns:
            tuple: (is_healthy, message)
        """
        try:
            from backend.extensions import db
            from backend.models import User
            
            # Try to execute a simple query
            db.session.execute(db.text("SELECT 1"))
            db.session.commit()
            
            return True, "Database connection healthy"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    @staticmethod
    def check_redis_connection():
        """
        Check Redis connection health (if used for rate limiting).
        
        Returns:
            tuple: (is_healthy, message)
        """
        try:
            import redis
            from backend.config import Config
            
            redis_url = Config.RATELIMIT_STORAGE_URL
            if redis_url.startswith("redis://"):
                r = redis.from_url(redis_url)
                r.ping()
                return True, "Redis connection healthy"
            else:
                return True, "Redis not configured (using memory storage)"
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    @staticmethod
    def get_health_status():
        """
        Get overall application health status.
        
        Returns:
            dict: Health status information
        """
        db_healthy, db_message = HealthCheck.check_database_connection()
        redis_healthy, redis_message = HealthCheck.check_redis_connection()
        
        overall_healthy = db_healthy and redis_healthy
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": db_message
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "message": redis_message
            },
            "timestamp": str(logging.time.time())
        }


def setup_production_logging():
    """
    Set up production-optimized logging.
    
    Returns:
        logging.Logger: Configured logger
    """
    import logging
    import logging.handlers
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Set up logger
    logger = logging.getLogger("stock_app")
    logger.setLevel(logging.WARNING)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/production.log",
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    file_handler.setLevel(logging.WARNING)
    
    # Error handler
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/production_errors.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger
