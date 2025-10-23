# 🏪 Stock App — Inventory & Sales Management System

A modern Flask + SQLAlchemy web application for managing clients, products, inventory, sales, and purchases. This project is built on a scalable "App Factory" pattern, uses an ORM for database safety, and includes user authentication.

---

## 🚀 Features

* **🔐 Authentication:** Secure user registration and login (Admin/User roles can be added).
* **🧭 Dashboard:** View key business metrics: Total Clients, Total Products, Total Sales, and Low Stock Items.
* **👥 Clients:** Full CRUD (Create, Read, Update, Delete) for customer management.
* **📦 Products:** Manage products, categories, pricing, and stock levels.
* **🧾 Sales:** Create new sales linked to clients and products; automatically updates inventory.
* **🛒 Purchases:** Record new stock purchases from suppliers; automatically updates inventory.
* **🏷️ Inventory:** View current stock levels, low-stock warnings, and out-of-stock items.

---

## 🧩 Tech Stack

Backend:Flask (Python)
Database ORM: Flask-SQLAlchemy(Object-Relational Mapper)
Database System: SQLite
Migrations: Flask-Migrate(handles database schema changes)
Authentication: Flask-Login (session management)
Security: Flask-Bcrypt (password hashing)
Environment: Python Dotenv
Frontend: HTML/CSS/JS
Version Control: Git + GitHub

---

## 📂 Project Structure

The project uses the **App Factory** pattern for scalability and testability.

stock-app/
│
├── backend/
│   │
│   ├── init.py     # ⬅️ App Factory (create_app)
│   ├── config.py       # Configuration classes
│   ├── extensions.py   # ⬅️ Holds db, bcrypt, login_manager
│   ├── models.py       # ⬅️ All database models (SQLAlchemy)
│   │
│   ├── routes/         # ⬅️ All app blueprints
│   │   ├── auth.py     # Login/Register routes
│   │   ├── clients.py
│   │   ├── products.py
│   │   ├── sales.py
│   │   ├── purchases.py
│   │   ├── inventory.py
│   │   └── dashboard.py
│   │
│   ├── static/         # CSS, JS, images
│   └── templates/      # HTML files (login, dashboard, etc.)
│
├── database/
│   └── stock.db        # SQLite database file (managed by Flask-Migrate)
│
├── migrations/         # ⬅️ Flask-Migrate (Alembic) folder
│
├── run.py              # ⬅️ Main entry point to run the app
├── .env                # Environment variables
├── requirements.txt
└── README.md

---

⚙️ Setup Instructions

​1️⃣ Clone the repo

git clone [https://github.com/GoaTMoha/stock-app.git]
(https://github.com/GoaTMoha/stock-app.git)

cd stock-app


2️⃣ Create and activate a virtual environment


# Create

python -m venv venv

# Activate (Windows)

.\venv\Scripts\activate

# Activate (Linux/Mac)

source venv/bin/activate


3️⃣ Install dependencies
​(These are the new required packages)

pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-Bcrypt python-dotenv

(Tip: Run pip freeze > requirements.txt to save them)


4️⃣ Create your .env file
Create a file named .env in the root stock-app/ folder and add:

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=supersecretkey123

(The DATABASE_URL is now set inside config.py)


5️⃣ Initialize the Database (New Method)
Do not run the old database.py file. We now use Flask-Migrate.

# (Windows)
set FLASK_APP=run.py
# (Linux/Mac)
export FLASK_APP=run.py

# 1. Initialize the migrations folder (run this only ONCE)
flask db init

# 2. Create the first migration (reads models.py)
flask db migrate -m "Initial database migration"

# 3. Apply the migration to the database (creates all tables)
flask db upgrade

Your database/stock.db file will be created automatically.


6️⃣ Initialize the database with sample data
```bash
python init_db.py
```

7️⃣ Run the app
```bash
flask run
# or
python run.py
```

The application will be available at `http://localhost:5000`

## 🔐 Default Login Credentials

After running `python init_db.py`, you can login with:
- **Username**: admin
- **Email**: admin@stockapp.com
- **Password**: admin123

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_backend.py -v

# Run with coverage
python -m pytest tests/ --cov=backend
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user info
- `GET /auth/status` - Check authentication status

### Clients
- `POST /clients/add` - Add new client
- `GET /clients/search?q=query` - Search clients
- `GET /clients/recent` - Get recent clients
- `GET /clients/all` - Get all clients

### Products
- `POST /products/categories/add` - Add new category
- `POST /products/add` - Add new product
- `GET /products/search?q=query` - Search products
- `GET /products/recent` - Get recent products
- `GET /products/categories` - Get all categories
- `GET /products/all` - Get all products

### Sales
- `POST /sales/add` - Add new sale
- `GET /sales/search?q=query` - Search sales
- `GET /sales/recent` - Get recent sales

### Purchases
- `POST /purchases/add` - Add new purchase
- `GET /purchases/search?q=query` - Search purchases
- `GET /purchases/recent` - Get recent purchases
- `GET /purchases/<id>` - Get purchase details

### Inventory
- `GET /inventory/overview` - Get inventory overview
- `GET /inventory/filter?type=all|low|out` - Filter inventory
- `GET /inventory/search?q=query` - Search inventory

### Dashboard
- `GET /dashboard/overview` - Get dashboard statistics
- `GET /dashboard/sales-overview` - Get sales overview
- `GET /dashboard/inventory-distribution` - Get inventory distribution
- `GET /dashboard/recent-sales` - Get recent sales
- `GET /dashboard/low-stock` - Get low stock products

## 🛡️ Security Features

- **Authentication**: Flask-Login with session management
- **Password Hashing**: Flask-Bcrypt with configurable rounds
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Rate Limiting**: Flask-Limiter with configurable limits
- **Input Validation**: Comprehensive validation on all endpoints
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

💾 Database Models (ORM)
The database schema is now managed by SQLAlchemy models in backend/models.py.
users: Stores user info with hashed passwords.
clients: name, email, phone, address
categories: category names
products: name, category, price, stock, alert_threshold
sales: links to client, total price, date
sale_items: (Association table) links sales to products
purchases: supplier, total price, date
purchase_items: (Association table) links purchases to products


🧠 Future Enhancements
Add analytics dashboard charts (Flask + Chart.js)
Export reports (PDF, Excel)
Build a full frontend React interface
Implement user roles and permissions (Admin vs. User)


👨‍💻 Author
Hamani Moundir
📧 Contact: rojer.points@gmail.com
💻 GitHub: GoaTMoha