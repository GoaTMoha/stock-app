🏪 Stock App — Inventory & Sales Management System

A modern Flask + SQLite web application for managing clients, products, inventory, sales, and purchases.
This project aims to provide a complete business dashboard with clean analytics, quick insights, and easy CRUD operations.

🚀 Features
🧭 Dashboard

View key business metrics:

Total Clients

Total Products

Total Sales (DZD)

Low Stock Items

Interactive visualizations:

Sales Overview (bar chart)

Inventory Distribution (circle graph)

Quick summaries:

Recent Sales (5 latest)

Low Stock Products (5 lowest)

Add New Sale / New Purchase buttons

👥 Clients

➕ Add new clients (unique email & phone)

🔍 Search clients by name, email, phone, or address

📋 View 7 most recently added clients

✏️ Update or 🗑️ Delete clients

📦 Products

➕ Add categories and products

Products include:

Name

Category

Price (DZD)

Initial Stock

Alert Threshold

Description

🔍 Search products by name

📋 View 7 most recently added products

✏️ Update or 🗑️ Delete products

🧾 Sales

➕ Add a new sale:

Select existing client (by name/email/phone)

Add products & quantities

Auto-calculate total items and price

🔍 Search sales by ID, Client, or Date

📋 View 7 most recent sales

🛒 Purchases

➕ Add a new purchase:

Enter supplier name

Add products with quantity & unit price (DZD)

Auto-calculate total items and price

🔍 Search purchases by ID, Supplier, or Date

📋 View 7 most recent purchases

🏷️ Inventory

View:

Total Products

Low Stock Items

Out of Stock

Inventory Value (DZD)

🔍 Filter products (All, Low Stock, Out of Stock)

📋 View 7 recent products per filter

Data shown:

Name

Category

Current Stock

Alert Threshold

Price

Status

Actions

🧩 Tech Stack
Component	Technology
Backend	Flask (Python)
Database	SQLite
Environment	Python Dotenv
Frontend (upcoming)	HTML, CSS, JS (Flask templates or React frontend)
Version Control	Git + GitHub
📂 Project Structure
stock-app/
│
├── backend/
│   ├── app.py                # Main Flask app
│   ├── database.py           # SQLite setup and tables
│   ├── routers/
│   │   ├── clients.py
│   │   ├── products.py
│   │   ├── sales.py
│   │   ├── purchases.py
│   │   ├── inventory.py
│   │   └── dashboard.py
│   ├── templates/            # HTML files (future)
│   └── static/               # CSS, JS, images
│
├── database/
│   └── stock.db              # Auto-created SQLite database
│
├── .env                      # Environment variables
├── .gitignore
├── README.md
└── venv/                     # Virtual environment

⚙️ Setup Instructions
1️⃣ Clone the repo
git clone https://github.com/GoaTMoha/stock-app.git
cd stock-app

2️⃣ Create a virtual environment
python -m venv venv

3️⃣ Activate it

Windows PowerShell

.\venv\Scripts\activate


Linux/Mac

source venv/bin/activate

4️⃣ Install dependencies
pip install -r requirements.txt

5️⃣ Create your .env file
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=supersecretkey123
DATABASE_URL=sqlite:///database/stock.db

6️⃣ Initialize the database
python backend/database.py

7️⃣ Run the app
flask run

💾 Database Tables

The SQLite database (stock.db) includes:

clients — name, email, phone, address

categories — category names

products — name, category_id, price, stock, alert_threshold, description

sales — client_id, total_items, total_price, date

sale_items — link between sales and products

purchases — supplier, total_items, total_price, date

purchase_items — link between purchases and products

🧠 Future Enhancements

Add user authentication (admin login)

Add analytics dashboard charts (Flask + Chart.js)

Export reports (PDF, Excel)

Frontend React interface

REST API documentation
👨‍💻 Author

Hamani Moundir
📧 Contact: rojer.points@gmail.com
💻 GitHub: GoaTMoha
