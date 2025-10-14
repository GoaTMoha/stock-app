from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

DATABASE = "database/stock.db"


# ---------- Helper ----------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Add New Sale ----------
@dashboard_bp.route("/add-sale", methods=["POST"])
def add_sale():
    """
    Add a new sale:
    {
        "client_id": 1,
        "items": [
            {"product_id": 2, "quantity": 3},
            {"product_id": 5, "quantity": 1}
        ]
    }
    """
    data = request.get_json()
    client_id = data.get("client_id")
    items = data.get("items", [])

    if not client_id or not items:
        return jsonify({"error": "Client ID and items are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Calculate total and check stock availability
    total_price = 0
    for item in items:
        cursor.execute("SELECT price, stock FROM products WHERE id = ?", (item["product_id"],))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": f"Product ID {item['product_id']} not found"}), 404
        if product["stock"] < item["quantity"]:
            return jsonify({"error": f"Not enough stock for product ID {item['product_id']}"}), 400
        total_price += product["price"] * item["quantity"]

    # Insert sale
    cursor.execute(
        "INSERT INTO sales (client_id, date, total, items) VALUES (?, ?, ?, ?)",
        (client_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_price, len(items)),
    )
    sale_id = cursor.lastrowid

    # Update product stocks
    for item in items:
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Sale added successfully", "sale_id": sale_id, "total": total_price}), 201


# ---------- Add New Purchase ----------
@dashboard_bp.route("/add-purchase", methods=["POST"])
def add_purchase():
    """
    Add a new purchase:
    {
        "supplier": "Tech Supplier Co",
        "items": [
            {"product_id": 2, "quantity": 5, "unit_price": 1800}
        ]
    }
    """
    data = request.get_json()
    supplier = data.get("supplier")
    items = data.get("items", [])

    if not supplier or not items:
        return jsonify({"error": "Supplier and items are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    total_cost = 0
    for item in items:
        total_cost += item["unit_price"] * item["quantity"]
        # Update product stock
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item["quantity"], item["product_id"]))

    cursor.execute(
        "INSERT INTO purchases (supplier, date, total, items) VALUES (?, ?, ?, ?)",
        (supplier, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_cost, len(items)),
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Purchase added successfully", "total": total_cost}), 201


# ---------- Dashboard Overview ----------
@dashboard_bp.route("/overview", methods=["GET"])
def dashboard_overview():
    """
    Returns main dashboard stats:
    - total clients
    - total products
    - total sales (DZD)
    - low stock count
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM clients")
    total_clients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM sales")
    total_sales = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < alert_threshold")
    low_stock_items = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total_clients": total_clients,
        "total_products": total_products,
        "total_sales_dzd": round(total_sales, 2),
        "low_stock_items": low_stock_items
    }), 200


# ---------- Sales Overview (Bar Graph) ----------
@dashboard_bp.route("/sales-overview", methods=["GET"])
def sales_overview():
    """
    Returns last 7 sales totals for bar graph visualization.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, total FROM sales
        ORDER BY date DESC
        LIMIT 7
    """)
    sales = [{"date": row["date"], "total": row["total"]} for row in cursor.fetchall()]
    conn.close()

    # Sort chronologically
    sales.reverse()

    return jsonify(sales), 200


# ---------- Inventory Distribution (Relative Circle) ----------
@dashboard_bp.route("/inventory-distribution", methods=["GET"])
def inventory_distribution():
    """
    Returns distribution between in stock, low stock, and out of stock products.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock > alert_threshold")
    in_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock = 0")
    out_of_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < alert_threshold AND stock > 0")
    low_stock = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "in_stock": in_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    }), 200


# ---------- Recent Sales (Last 5) ----------
@dashboard_bp.route("/recent-sales", methods=["GET"])
def recent_sales():
    """
    Returns last 5 sales with ID, client name, date, total, items.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, c.name AS client, s.date, s.total, s.items
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        ORDER BY s.date DESC
        LIMIT 5
    """)
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(sales), 200


# ---------- Low Stock Products (Last 5) ----------
@dashboard_bp.route("/low-stock", methods=["GET"])
def low_stock_products():
    """
    Returns 5 products that are currently low in stock.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, c.name AS category, p.stock, p.alert_threshold, p.price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.stock < p.alert_threshold
        ORDER BY p.stock ASC
        LIMIT 5
    """)

    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products), 200
