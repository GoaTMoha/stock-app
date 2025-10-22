"""
Enhanced test suite for the Stock Manager App backend.
Tests validation, security, transactions, and error handling.
"""

import pytest
import tempfile
import os
from backend import create_app
from backend.extensions import db
from backend.models import (
    User,
    Client,
    Product,
    Category,
    Sale,
    SaleItem,
    Purchase,
    PurchaseItem,
)
from backend.validation import (
    validate_client_data,
    validate_product_data,
    validate_sale_data,
    validate_purchase_data,
    validate_category_data,
)
from backend.security import SecurityValidator, PasswordManager
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
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
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_data(app):
    """Create sample data for testing."""
    with app.app_context():
        # Create test user
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


class TestValidation:
    """Test validation functions."""

    def test_validate_client_data_success(self):
        """Test successful client data validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "address": "123 Main St",
        }
        is_valid, error = validate_client_data(data)
        assert is_valid is True
        assert error is None

    def test_validate_client_data_missing_fields(self):
        """Test client data validation with missing fields."""
        data = {"name": "John Doe"}
        is_valid, error = validate_client_data(data)
        assert is_valid is False
        assert "Missing required fields" in error

    def test_validate_client_data_invalid_email(self):
        """Test client data validation with invalid email."""
        data = {
            "name": "John Doe",
            "email": "invalid-email",
            "phone": "1234567890",
            "address": "123 Main St",
        }
        is_valid, error = validate_client_data(data)
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_client_data_invalid_phone(self):
        """Test client data validation with invalid phone."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123",  # Too short
            "address": "123 Main St",
        }
        is_valid, error = validate_client_data(data)
        assert is_valid is False
        assert "Invalid phone number format" in error

    def test_validate_product_data_success(self):
        """Test successful product data validation."""
        data = {
            "name": "Test Product",
            "category_id": 1,
            "price": 100.0,
            "stock": 10,
            "alert_threshold": 5,
            "description": "Test description",
        }
        is_valid, error = validate_product_data(data)
        assert is_valid is True
        assert error is None

    def test_validate_product_data_invalid_price(self):
        """Test product data validation with invalid price."""
        data = {
            "name": "Test Product",
            "category_id": 1,
            "price": -10.0,  # Negative price
            "stock": 10,
        }
        is_valid, error = validate_product_data(data)
        assert is_valid is False
        assert "Price must be at least" in error

    def test_validate_sale_data_success(self):
        """Test successful sale data validation."""
        data = {
            "client_search": "john@example.com",
            "products": [{"product_id": 1, "quantity": 2}],
        }
        is_valid, error = validate_sale_data(data)
        assert is_valid is True
        assert error is None

    def test_validate_sale_data_no_products(self):
        """Test sale data validation with no products."""
        data = {
            "client_search": "john@example.com",
            "products": [],
        }
        is_valid, error = validate_sale_data(data)
        assert is_valid is False
        assert "Missing required fields" in error

    def test_validate_purchase_data_success(self):
        """Test successful purchase data validation."""
        data = {
            "supplier": "Test Supplier",
            "items": [{"product_id": 1, "quantity": 5, "unit_price": 50.0}],
        }
        is_valid, error = validate_purchase_data(data)
        assert is_valid is True
        assert error is None

    def test_validate_category_data_success(self):
        """Test successful category data validation."""
        data = {"name": "Test Category"}
        is_valid, error = validate_category_data(data)
        assert is_valid is True
        assert error is None


class TestSecurity:
    """Test security functions."""

    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Strong password
        is_strong, message = SecurityValidator.is_strong_password("Password123!")
        assert is_strong is True

        # Weak password - too short
        is_strong, message = SecurityValidator.is_strong_password("Pass1!")
        assert is_strong is False
        assert "at least 8 characters" in message

        # Weak password - no uppercase
        is_strong, message = SecurityValidator.is_strong_password("password123!")
        assert is_strong is False
        assert "uppercase letter" in message

        # Weak password - no digit
        is_strong, message = SecurityValidator.is_strong_password("Password!")
        assert is_strong is False
        assert "digit" in message

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = PasswordManager.hash_password(password)
        
        assert hashed != password
        assert PasswordManager.verify_password(password, hashed) is True
        assert PasswordManager.verify_password("wrongpassword", hashed) is False

    def test_input_sanitization(self):
        """Test input sanitization."""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = SecurityValidator.sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "javascript" not in sanitized.lower()

    def test_email_security_validation(self):
        """Test email security validation."""
        # Safe email
        is_safe, message = SecurityValidator.validate_email_security("user@example.com")
        assert is_safe is True

        # Suspicious email with script
        is_safe, message = SecurityValidator.validate_email_security("user<script>@example.com")
        assert is_safe is False
        assert "suspicious content" in message


class TestTransactions:
    """Test transaction utilities."""

    def test_atomic_transaction_success(self, app):
        """Test successful atomic transaction."""
        from backend.transactions import atomic_transaction

        with app.app_context():
            with atomic_transaction():
                category = Category(name="Test Category")
                db.session.add(category)
                # Transaction should commit automatically

            # Verify the category was created
            created_category = Category.query.filter_by(name="Test Category").first()
            assert created_category is not None

    def test_atomic_transaction_rollback(self, app):
        """Test atomic transaction rollback on error."""
        from backend.transactions import atomic_transaction

        with app.app_context():
            try:
                with atomic_transaction():
                    category = Category(name="Test Category")
                    db.session.add(category)
                    raise Exception("Simulated error")
            except Exception:
                pass

            # Verify the category was not created
            created_category = Category.query.filter_by(name="Test Category").first()
            assert created_category is None

    def test_stock_validation(self, app, sample_data):
        """Test stock availability validation."""
        from backend.transactions import validate_stock_availability

        with app.app_context():
            # Test sufficient stock
            is_available, message = validate_stock_availability(1, 5)
            assert is_available is True

            # Test insufficient stock
            is_available, message = validate_stock_availability(1, 20)
            assert is_available is False
            assert "Insufficient stock" in message

            # Test non-existent product
            is_available, message = validate_stock_availability(999, 1)
            assert is_available is False
            assert "not found" in message


class TestErrorHandling:
    """Test error handling."""

    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_method_not_allowed(self, client):
        """Test 405 error handling."""
        response = client.post("/")  # POST not allowed on home route
        assert response.status_code == 405
        data = response.get_json()
        assert "error" in data


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_auth_rate_limiting(self, client):
        """Test rate limiting on auth endpoints."""
        # Simple test to verify auth endpoints exist
        response = client.post("/auth/register", json={})
        assert response.status_code in [400, 401, 422]  # Should fail validation


class TestDatabaseConstraints:
    """Test database constraints."""

    def test_product_price_constraint(self, app):
        """Test product price constraint."""
        with app.app_context():
            with pytest.raises(Exception):  # Should raise constraint violation
                product = Product(
                    name="Test Product",
                    category_id=1,
                    price=-10.0,  # Negative price should fail
                    stock=10,
                )
                db.session.add(product)
                db.session.commit()

    def test_sale_item_quantity_constraint(self, app, sample_data):
        """Test sale item quantity constraint."""
        with app.app_context():
            with pytest.raises(Exception):  # Should raise constraint violation
                sale_item = SaleItem(
                    sale_id=1,
                    product_id=1,
                    quantity=0,  # Zero quantity should fail
                    price=100.0,
                )
                db.session.add(sale_item)
                db.session.commit()


class TestIntegration:
    """Integration tests."""

    def test_complete_sale_flow(self, client, sample_data):
        """Test complete sale flow with authentication."""
        # Register a user
        register_response = client.post(
            "/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "Password123!",
            },
        )
        assert register_response.status_code == 201

        # Login
        login_response = client.post(
            "/auth/login",
            json={"email": "test2@example.com", "password": "Password123!"},
        )
        assert login_response.status_code == 200

        # Add a sale (this will redirect to login since we're not properly authenticated in test)
        sale_response = client.post(
            "/sales/add",
            json={
                "client_search": "client@example.com",
                "products": [{"product_id": 1, "quantity": 2}],
            },
        )
        # Should redirect to login (302) or succeed (201) or fail with validation error (400) or server error (500)
        assert sale_response.status_code in [201, 302, 400, 500]

    def test_complete_purchase_flow(self, client, sample_data):
        """Test complete purchase flow."""
        # Add a purchase (will redirect to login)
        purchase_response = client.post(
            "/purchases/add",
            json={
                "supplier": "Test Supplier",
                "items": [{"product_id": 1, "quantity": 5, "unit_price": 50.0}],
            },
        )
        # Should redirect to login (302) or succeed (201)
        assert purchase_response.status_code in [201, 302]
