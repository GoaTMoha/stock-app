import os
from dotenv import load_dotenv

# Find the absolute path to the .env file (in the root folder)
# This makes sure it's found correctly from run.py or flask commands
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

    # Define the base database URI
    # This points to the stock.db file inside the 'database' folder
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "database", "stock.db"
    )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security settings
    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )
    SESSION_COOKIE_HTTPONLY = (
        os.environ.get("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
    )
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")

    # CSRF Protection
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "True").lower() == "true"
    WTF_CSRF_TIME_LIMIT = int(os.environ.get("WTF_CSRF_TIME_LIMIT", 3600))
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY") or SECRET_KEY

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "200 per day, 50 per hour")
    RATELIMIT_HEADERS_ENABLED = True

    # Logging Configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE_MAX_SIZE = int(os.environ.get("LOG_FILE_MAX_SIZE", 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", 5))

    # Redis and Caching Configuration
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    
    # Cache configuration
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")  # redis, simple, or null
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 60))  # 60 seconds
    CACHE_KEY_PREFIX = os.environ.get("CACHE_KEY_PREFIX", "stock_app")
    
    # Redis connection URL for Flask-Caching
    @property
    def CACHE_REDIS_URL(self):
        """Build Redis URL for Flask-Caching."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @staticmethod
    def validate_config():
        """Validate required configuration."""
        if not Config.SECRET_KEY or len(Config.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return True


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    FLASK_ENV = "production"
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


# Dictionary to easily access configs by name
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
