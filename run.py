from backend import create_app
import os

# Get the environment config name from the .env file
# Defaults to 'development' if not set
config_name = os.getenv('FLASK_ENV', 'development')

# Create the app instance using the factory
app = create_app(config_name)

if __name__ == '__main__':
    # Run the app
    # debug=True will be set automatically if FLASK_ENV is 'development'
    app.run(debug=app.config.get('DEBUG', False))
