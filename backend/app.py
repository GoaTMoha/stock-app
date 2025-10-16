from flask import Flask
from config import Config
from dotenv import load_dotenv
import os

from routes.clients import clients_bp
from routes.products import products_bp
from routers.sales import sales_bp
from routers.purchases import purchases_bp
from routers.inventory import inventory_bp
from routers.dashboard import dashboard_bp


# Register blueprints
app.register_blueprint(clients_bp)
app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(purchases_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(dashboard_bp)


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def home():
    return "Hello, Flask with Config!"

if __name__ == "__main__":
    # Use environment variable to control debug mode
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode)
