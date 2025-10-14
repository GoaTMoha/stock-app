from flask import Blueprint, jsonify, request
import sqlite3

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

DATABASE = "database/stock.db"


# ---------- Helper ----------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Inventory Overview ----------
@inventory_bp.route("/overview", methods=["GET"])
def inventory_overview():
    """
    Returns summary stats for dashboard:
    - total products
    - low stock items
    - out of stock items
    - inventory value (sum of stock * price)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock = 0")
    out_of_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < alert_threshold AND stock > 0")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(stock * price) FROM products")
    inventory_value = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "inventory_value_dzd": round(inventory_value, 2)
    }), 200


# ---------- Filtered Product Search ----------
@inventory_bp.route("/filter", methods=["GET"])
def filter_inventory():
    """
    Query param: ?type=all|low|out
    Returns filtered products accordingly.
    """
    filter_type = request.args.get("type", "all")
    conn = get_db_connection()
    cursor = conn.cursor()

    if filter_type == "low":
        cursor.execute("""
            SELECT p.id, p.name, c.name AS category, p.stock, p.alert_threshold, p.price,
                   CASE 
                        WHEN p.stock = 0 THEN 'Out of Stock'
                        WHEN p.stock < p.alert_threshold THEN 'Low Stock'
                        ELSE 'In Stock'
                   END AS status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.stock < p.alert_threshold AND p.stock > 0
            ORDER BY p.id DESC
            LIMIT 7
        """)
    elif filter_type == "out":
        cursor.execute("""
            SELECT p.id, p.name, c.name AS category, p.stock, p.alert_threshold, p.price,
                   'Out of Stock' AS status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.stock = 0
            ORDER BY p.id DESC
            LIMIT 7
        """)
    else:  # all
        cursor.execute("""
            SELECT p.id, p.name, c.name AS category, p.stock, p.alert_threshold, p.price,
                   CASE 
                        WHEN p.stock = 0 THEN 'Out of Stock'
                        WHEN p.stock < p.alert_threshold THEN 'Low Stock'
                        ELSE 'In Stock'
                   END AS status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
            LIMIT 7
        """)

    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products), 200


# ---------- Search Inventory by Name ----------
@inventory_bp.route("/search", methods=["GET"])
def search_inventory():
    """
    Search inventory by product name or category name.
    """
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, c.name AS category, p.stock, p.alert_threshold, p.price,
               CASE 
                    WHEN p.stock = 0 THEN 'Out of Stock'
                    WHEN p.stock < p.alert_threshold THEN 'Low Stock'
                    ELSE 'In Stock'
               END AS status
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE ? OR c.name LIKE ?
        ORDER BY p.id DESC
        LIMIT 7
    """, (f"%{query}%", f"%{query}%"))

    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products), 200
