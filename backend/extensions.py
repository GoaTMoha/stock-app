from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Create extension instances
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)
cache = Cache()

# Configure login manager
# This tells Flask-Login which view (function name) to redirect to
# if a user tries to access a page that requires login.
login_manager.login_view = "auth.login"

# Optional: Set the message category for flashed messages
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Import here to avoid circular imports

    return User.query.get(int(user_id))
