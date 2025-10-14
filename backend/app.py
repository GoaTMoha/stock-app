from flask import Flask
from config import Config
from dotenv import load_dotenv
import os

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
