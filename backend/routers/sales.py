from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

DATABASE = "database/stock.db"


# ---------- Helper ----------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Add a New Sale ----------
@sales_bp.route("/add", methods=["POST"])
def add_sale():
    """
    JSON payload example:
    {
        "client_search": "john@example.com",
        "products": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ]
    }
    """
    data = request.get_json()
    client_search = data.get("client_search")
    products = data.get("products", [])

    if not client_search or not products:
        return jsonify({"error": "Client and products are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find client by name, email, or phone
        cursor.execute("""
            SELECT * FROM clients
            WHERE name = ? OR email = ? OR phone = ?
        """, (client_search, client_search, client_search))
        client = cursor.fetchone()
        if not client:
            conn.close()
            return jsonify({"error": "Client not found"}), 404

        client_id = client["id"]

        total_price = 0
        total_items = 0
        sale_items = []

        for item in products:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)

            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            if not product:
                conn.close()
                return jsonify({"error": f"Product ID {product_id} not found"}), 404

            # Check stock
            if product["stock"] < quantity:
                conn.close()
                return jsonify({"error": f"Not enough stock for {product['name']}"}), 400

            price = product["price"] * quantity
            total_price += price
            total_items += quantity

            sale_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product["price"],
                "subtotal": price
            })

        # Insert into sales table
        cursor.execute("""
            INSERT INTO sales (client_id, date, total_items, total_price)
            VALUES (?, ?, ?, ?)
        """, (client_id, datetime.now(), total_items, total_price))
        sale_id = cursor.lastrowid

        # Insert into sale_items table and update stock
        for item in sale_items:
            cursor.execute("""
                INSERT INTO sale_items (sale_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (sale_id, item["product_id"], item["quantity"], item["price"]))

            cursor.execute("""
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
            """, (item["quantity"], item["product_id"]))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Sale added successfully!",
            "sale_id": sale_id,
            "total_items": total_items,
            "total_price": total_price
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Search Sales ----------
@sales_bp.route("/search", methods=["GET"])
def search_sales():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, c.name AS client, s.date, s.total_items, s.total_price
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        WHERE s.id LIKE ? OR c.name LIKE ? OR c.email LIKE ? OR s.date LIKE ?
        ORDER BY s.date DESC
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))

    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(sales), 200


# ---------- Get 7 Most Recent Sales ----------
@sales_bp.route("/recent", methods=["GET"])
def recent_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, c.name AS client, s.date, s.total_items, s.total_price
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        ORDER BY s.date DESC
        LIMIT 7
    """)

    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(sales), 200
