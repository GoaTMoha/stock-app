from flask import Blueprint, jsonify
from flask_login import login_required
from ..extensions import db
from ..models import Client, Product, Sale, Category
from ..cache_utils import cached_with_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


# ---------- Dashboard Overview ----------
@dashboard_bp.route("/overview", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache for 60 seconds
def dashboard_overview():
    """
    Returns main dashboard stats:
    - total clients
    - total products
    - total sales (DZD)
    - low stock count
    """
    total_clients = Client.query.count()
    total_products = Product.query.count()
    total_sales = db.session.query(db.func.sum(Sale.total)).scalar() or 0
    low_stock_items = Product.query.filter(
        Product.stock < Product.alert_threshold
    ).count()

    return (
        jsonify(
            {
                "total_clients": total_clients,
                "total_products": total_products,
                "total_sales_dzd": round(total_sales, 2),
                "low_stock_items": low_stock_items,
            }
        ),
        200,
    )


# ---------- Sales Overview (Bar Graph) ----------
@dashboard_bp.route("/sales-overview", methods=["GET"])
@login_required
@cached_with_user(timeout=120)  # Cache for 2 minutes
def sales_overview():
    """
    Returns last 7 sales totals for bar graph visualization.
    """
    sales = Sale.query.order_by(Sale.date.desc()).limit(7).all()

    result = []
    for sale in sales:
        result.append({"date": sale.date.isoformat(), "total": sale.total})

    # Sort chronologically
    result.reverse()

    return jsonify(result), 200


# ---------- Inventory Distribution (Relative Circle) ----------
@dashboard_bp.route("/inventory-distribution", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache for 60 seconds
def inventory_distribution():
    """
    Returns distribution between in stock, low stock, and out of stock products.
    """
    in_stock = Product.query.filter(Product.stock > Product.alert_threshold).count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()
    low_stock = Product.query.filter(
        Product.stock < Product.alert_threshold, Product.stock > 0
    ).count()

    return (
        jsonify(
            {"in_stock": in_stock, "low_stock": low_stock, "out_of_stock": out_of_stock}
        ),
        200,
    )


# ---------- Recent Sales (Last 5) ----------
@dashboard_bp.route("/recent-sales", methods=["GET"])
@login_required
@cached_with_user(timeout=30)  # Cache for 30 seconds (more dynamic data)
def recent_sales():
    """
    Returns last 5 sales with ID, client name, date, total, items.
    """
    sales = Sale.query.join(Client).order_by(Sale.date.desc()).limit(5).all()

    result = []
    for sale in sales:
        result.append(
            {
                "id": sale.id,
                "client": sale.client.name if sale.client else "Unknown",
                "date": sale.date.isoformat(),
                "total": sale.total,
                "items": sale.items_count,
            }
        )

    return jsonify(result), 200


# ---------- Low Stock Products (Last 5) ----------
@dashboard_bp.route("/low-stock", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache for 60 seconds
def low_stock_products():
    """
    Returns 5 products that are currently low in stock.
    """
    products = (
        Product.query.join(Category)
        .filter(Product.stock < Product.alert_threshold)
        .order_by(Product.stock.asc())
        .limit(5)
        .all()
    )

    result = []
    for product in products:
        result.append(
            {
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "price": product.price,
            }
        )

    return jsonify(result), 200
