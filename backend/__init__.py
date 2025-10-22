from flask import Flask
from .config import config_by_name
from .extensions import db, bcrypt, login_manager, migrate, csrf, limiter, cache
from .security import apply_security_headers
from .logging_config import setup_app_logging
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Validate configuration
    config_by_name[config_name].validate_config()

    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize caching with fallback to simple cache if Redis is not available
    try:
        cache.init_app(app)
        app.logger.info(f"Caching initialized with {app.config.get('CACHE_TYPE', 'redis')} backend")
    except Exception as e:
        app.logger.warning(f"Failed to initialize Redis cache: {e}. Falling back to simple cache.")
        app.config['CACHE_TYPE'] = 'simple'
        cache.init_app(app)

    # --- Initialize Logging ---
    setup_app_logging(app)

    # --- Import and Register Blueprints ---
    # We import them here to avoid circular imports

    from .routes.auth import auth_bp
    from .routes.clients import clients_bp
    from .routes.products import products_bp
    from .routes.sales import sales_bp
    from .routes.purchases import purchases_bp
    from .routes.inventory import inventory_bp
    from .routes.dashboard import dashboard_bp
    from .routes.cache import cache_bp

    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(purchases_bp, url_prefix="/purchases")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(cache_bp, url_prefix="/cache")

    # --- Health Check Route ---
    @app.route("/health")
    def health_check():
        """Health check endpoint for monitoring."""
        from .production import HealthCheck
        
        health_status = HealthCheck.get_health_status()
        status_code = 200 if health_status["status"] == "healthy" else 503
        
        return health_status, status_code

    # --- Main Route ---
    @app.route("/")
    def home():
        response = app.make_response("Welcome to the Stock App API!")
        return apply_security_headers(response)

    # --- Security Headers ---
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        return apply_security_headers(response)

    # --- Error Handlers ---
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request"}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {"error": "Unauthorized"}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {"error": "Forbidden"}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return {"error": "Unprocessable entity"}, 422

    @app.errorhandler(429)
    def too_many_requests(error):
        return {"error": "Too many requests"}, 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error"}, 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return {"error": "Service unavailable"}, 503

    return app
