# 🧾 Stock Management App

A simple yet powerful **inventory and sales management system** built with **Flask** and **SQLite**.  
This backend provides APIs for managing **clients**, **products**, **sales**, **purchases**, **inventory**, and a **dashboard overview**.

---

## 🚀 Features

### 🧍 Clients
- ➕ Add a new client (unique email, phone, and address)
- 🔍 Search clients by name, email, phone, or address
- 📋 View the 7 most recently added clients
- 🗑️ Update or delete clients

### 📦 Products
- ➕ Add new categories and products
- 🔍 Search products by name
- 📋 View the 7 most recently added products (Name, Category, Price, Stock, Description)
- 🗑️ Update or delete products

### 💰 Sales
- ➕ Create new sales by selecting a client and adding products with quantity
- 🔍 Search sales by ID, client, or date
- 📋 View the 7 most recent sales with ID, client, date, total, and items count

### 🧾 Purchases
- ➕ Add a new purchase (supplier info, products, quantities, unit prices)
- 🔍 Search purchases by ID, supplier, or date
- 📋 View 7 most recent purchases with supplier and total

### 🏷️ Inventory
- 📊 View total products, low stock items, out-of-stock items, and total inventory value
- 🔍 Filter inventory (All / Low Stock / Out of Stock)
- 📋 Display 7 recent products per filter (Name, Category, Stock, Price, etc.)

### 📈 Dashboard
- 🧠 Overview with total counts (clients, products, sales in DZD)
- 📊 Low Stock Items alert
- 📋 Sales Overview bar chart
- 🎯 Inventory Distribution pie chart
- 🧾 Recent sales and low stock product lists

---

## 🏗️ Project Structure

stock-app/
│
├── backend/
│ ├── app.py # Main Flask application entry point
│ ├── database.py # Handles SQLite setup and table creation
│ ├── routers/
│ │ ├── clients.py
│ │ ├── products.py
│ │ ├── sales.py
│ │ ├── purchases.py
│ │ ├── inventory.py
│ │ └── dashboard.py
│ ├── static/ # CSS, JS, and images (if needed)
│ └── templates/ # HTML templates (for web interface)
│
├── database/
│ └── stock.db # SQLite database (auto-generated)
│
├── .env # Environment variables (ignored by Git)
├── .gitignore # Ignore files (venv, db, etc.)
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── venv/ # Virtual environment (ignored by Git)

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/stock-app.git
cd stock-app

python -m venv venv
.\venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt

FLASK_ENV=development
DATABASE_PATH=database/stock.db

python backend/database.py

✅ Database initialized successfully.

flask run

Then visit:
👉 http://127.0.0.1:5000

📡 API Overview

Each router handles a different part of the system:

Route File	Endpoint Base	Description
clients.py	/clients	Manage clients
products.py	/products	Manage products and categories
sales.py	/sales	Create and list sales
purchases.py	/purchases	Manage supplier purchases
inventory.py	/inventory	View and filter stock levels
dashboard.py	/dashboard	Display summary and charts
🧠 Example Request
➕ Add a Client
POST /clients/add
Content-Type: application/json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+213654789123",
  "address": "Algiers, Algeria"
}

✅ Response
{
  "message": "Client added successfully",
  "client_id": 1
}

🧰 Tech Stack

Backend: Flask (Python)

Database: SQLite3

Environment Management: python-dotenv

ORM / Queries: sqlite3 module (no ORM for simplicity)

Architecture: Modular Flask routers (RESTful APIs)

📜 License

This project is licensed under the MIT License — free to use, modify, and share.

👨‍💻 Author

Hamani Moundir
📧 Contact: rojer.points@gmail.com
💻 GitHub: GoaTMoha
