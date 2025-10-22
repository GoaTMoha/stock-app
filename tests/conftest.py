import pytest
import os
import tempfile
from backend import create_app
from backend.extensions import db
from backend.models import User, Client, Product, Category
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for testing."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()

    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Create sample data for tests."""
    with app.app_context():
        # Create test user with properly hashed password
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("password123"),
        )
        db.session.add(user)

        # Create test category
        category = Category(name="Electronics")
        db.session.add(category)

        # Create test product
        product = Product(
            name="Test Product",
            category_id=1,
            price=100.0,
            stock=10,
            alert_threshold=5,
            description="Test product description",
        )
        db.session.add(product)

        # Create test client
        client = Client(
            name="Test Client",
            email="client@example.com",
            phone="1234567890",
            address="Test Address",
        )
        db.session.add(client)

        db.session.commit()

        return {
            "user": user,
            "category": category,
            "product": product,
            "client": client,
        }


@pytest.fixture
def authenticated_client(client, sample_data):
    """Create an authenticated test client."""
    # Login to get session
    login_response = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "password123"}
    )

    # Return the client with session cookies
    return client
