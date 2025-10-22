# 📚 Stock Manager App - API Documentation

## Overview

The Stock Manager App is a comprehensive Flask-based REST API for managing inventory, sales, purchases, clients, and products. It features robust authentication, validation, transaction management, and security measures.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- SQLite (development) or PostgreSQL (production)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd stock-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
python run.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///database/stock.db
WTF_CSRF_ENABLED=True
RATELIMIT_STORAGE_URL=memory://
```

## 🔐 Authentication

All API endpoints (except auth endpoints) require authentication. Use Flask-Login session-based authentication.

### Register User
```http
POST /auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

**Response:**
```json
{
    "message": "User registered successfully"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

### Logout
```http
POST /auth/logout
```

### Check Auth Status
```http
GET /auth/status
```

**Response:**
```json
{
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

## 👥 Clients API

### Add Client
```http
POST /clients/add
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St"
}
```

**Response:**
```json
{
    "message": "Client added successfully",
    "client_id": 1
}
```

### Search Clients
```http
GET /clients/search?q=john
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "address": "123 Main St",
        "created_at": "2024-01-01T10:00:00"
    }
]
```

### Get Recent Clients
```http
GET /clients/recent
```

### Get All Clients
```http
GET /clients/all
```

## 🛍️ Products API

### Add Category
```http
POST /products/categories/add
Content-Type: application/json

{
    "name": "Electronics"
}
```

**Response:**
```json
{
    "message": "Category added successfully",
    "category_id": 1
}
```

### Add Product
```http
POST /products/add
Content-Type: application/json

{
    "name": "Laptop",
    "category_id": 1,
    "price": 999.99,
    "stock": 10,
    "alert_threshold": 5,
    "description": "High-performance laptop"
}
```

**Response:**
```json
{
    "message": "Product added successfully",
    "product_id": 1
}
```

### Search Products
```http
GET /products/search?q=laptop
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "price": 999.99,
        "stock": 10,
        "alert_threshold": 5,
        "description": "High-performance laptop",
        "created_at": "2024-01-01T10:00:00"
    }
]
```

### Get Recent Products
```http
GET /products/recent
```

### Get All Categories
```http
GET /products/categories
```

### Get All Products
```http
GET /products/all
```

## 💸 Sales API

### Add Sale
```http
POST /sales/add
Content-Type: application/json

{
    "client_search": "john@example.com",
    "products": [
        {
            "product_id": 1,
            "quantity": 2
        },
        {
            "product_id": 2,
            "quantity": 1
        }
    ]
}
```

**Response:**
```json
{
    "message": "Sale added successfully!",
    "sale_id": 1,
    "total_items": 3,
    "total_price": 1999.98
}
```

### Search Sales
```http
GET /sales/search?q=john
```

**Response:**
```json
[
    {
        "id": 1,
        "client": "John Doe",
        "date": "2024-01-01T10:00:00",
        "total_items": 3,
        "total_price": 1999.98
    }
]
```

### Get Recent Sales
```http
GET /sales/recent
```

## 🧾 Purchases API

### Add Purchase
```http
POST /purchases/add
Content-Type: application/json

{
    "supplier": "Tech Supplier Co",
    "items": [
        {
            "product_id": 1,
            "quantity": 5,
            "unit_price": 800.00
        }
    ]
}
```

**Response:**
```json
{
    "message": "Purchase added successfully",
    "purchase_id": 1,
    "total": 4000.00,
    "items_count": 1
}
```

### Search Purchases
```http
GET /purchases/search?q=tech
```

**Response:**
```json
[
    {
        "id": 1,
        "supplier": "Tech Supplier Co",
        "date": "2024-01-01T10:00:00",
        "total": 4000.00,
        "items_count": 1
    }
]
```

### Get Recent Purchases
```http
GET /purchases/recent
```

### Get Purchase Details
```http
GET /purchases/<purchase_id>
```

## 📦 Inventory API

### Get Inventory Overview
```http
GET /inventory/overview
```

**Response:**
```json
{
    "total_products": 50,
    "low_stock": 5,
    "out_of_stock": 2,
    "inventory_value_dzd": 25000.00
}
```

### Filter Inventory
```http
GET /inventory/filter?type=low
```

**Query Parameters:**
- `type`: `all`, `low`, `out`

**Response:**
```json
[
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "stock": 3,
        "alert_threshold": 5,
        "price": 999.99,
        "status": "Low Stock"
    }
]
```

### Search Inventory
```http
GET /inventory/search?q=laptop
```

## 📊 Dashboard API

### Get Dashboard Overview
```http
GET /dashboard/overview
```

**Response:**
```json
{
    "total_clients": 25,
    "total_products": 50,
    "total_sales_dzd": 15000.00,
    "low_stock_items": 5
}
```

### Get Sales Overview
```http
GET /dashboard/sales-overview
```

**Response:**
```json
[
    {
        "date": "2024-01-01T10:00:00",
        "total": 500.00
    }
]
```

### Get Inventory Distribution
```http
GET /dashboard/inventory-distribution
```

**Response:**
```json
{
    "in_stock": 40,
    "low_stock": 5,
    "out_of_stock": 2
}
```

### Get Recent Sales
```http
GET /dashboard/recent-sales
```

**Response:**
```json
[
    {
        "id": 1,
        "client": "John Doe",
        "date": "2024-01-01T10:00:00",
        "total": 999.99,
        "items": 2
    }
]
```

### Get Low Stock Products
```http
GET /dashboard/low-stock-products
```

**Response:**
```json
[
    {
        "name": "Laptop",
        "category": "Electronics",
        "stock": 3,
        "alert_threshold": 5,
        "price": 999.99
    }
]
```

## 🔒 Security Features

### Rate Limiting
- Authentication endpoints: 5-10 requests per minute
- Sales/Purchases: 20 requests per minute
- General API: 200 requests per day, 50 per hour

### CSRF Protection
- Enabled by default
- Configured via `WTF_CSRF_ENABLED` environment variable

### Security Headers
All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Input Validation
- Comprehensive validation for all endpoints
- Email format validation
- Phone number validation
- Password strength requirements
- SQL injection prevention via ORM

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_backend.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Coverage
- Unit tests for all models
- Integration tests for API endpoints
- Validation tests
- Security tests
- Transaction tests

## 🚀 Production Deployment

### Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Environment Configuration
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/stock_db
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

### Database Migration
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## 📝 Error Handling

### Standard Error Responses
```json
{
    "error": "Error message description"
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `405`: Method Not Allowed
- `422`: Unprocessable Entity
- `429`: Too Many Requests
- `500`: Internal Server Error

## 🔧 Development

### Code Style
```bash
# Format code
black backend/ tests/

# Lint code
flake8 backend/ tests/
```

### Database Management
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## 📞 Support

For issues and questions:
1. Check the test suite for usage examples
2. Review the validation functions in `backend/validation.py`
3. Check security utilities in `backend/security.py`
4. Review transaction handling in `backend/transactions.py`

## 🔄 API Versioning

Current API version: v1
- All endpoints are prefixed with their respective modules
- Backward compatibility maintained through careful validation
- Breaking changes will be communicated in advance
