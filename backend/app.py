from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return "✅ Flask is running successfully!"

if __name__ == '__main__':
    app.run(debug=True)
