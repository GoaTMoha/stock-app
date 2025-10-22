from flask import Blueprint, jsonify, request
from flask_login import login_required
from ..extensions import db
from ..models import Product, Category
from ..cache_utils import cached_with_user

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


# ---------- Inventory Overview ----------
@inventory_bp.route("/overview", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache inventory overview for 60 seconds
def inventory_overview():
    """
    Returns summary stats for dashboard:
    - total products
    - low stock items
    - out of stock items
    - inventory value (sum of stock * price)
    """
    total_products = Product.query.count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()
    low_stock = Product.query.filter(
        Product.stock < Product.alert_threshold, Product.stock > 0
    ).count()

    # Calculate inventory value
    inventory_value = (
        db.session.query(db.func.sum(Product.stock * Product.price)).scalar() or 0
    )

    return (
        jsonify(
            {
                "total_products": total_products,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "inventory_value_dzd": round(inventory_value, 2),
            }
        ),
        200,
    )


# ---------- Filtered Product Search ----------
@inventory_bp.route("/filter", methods=["GET"])
@login_required
@cached_with_user(timeout=30)  # Cache filtered results for 30 seconds
def filter_inventory():
    """
    Query param: ?type=all|low|out
    Returns filtered products accordingly.
    """
    filter_type = request.args.get("type", "all")

    if filter_type == "low":
        products = (
            Product.query.join(Category)
            .filter(Product.stock < Product.alert_threshold, Product.stock > 0)
            .order_by(Product.id.desc())
            .limit(7)
            .all()
        )
    elif filter_type == "out":
        products = (
            Product.query.join(Category)
            .filter(Product.stock == 0)
            .order_by(Product.id.desc())
            .limit(7)
            .all()
        )
    else:  # all
        products = (
            Product.query.join(Category).order_by(Product.id.desc()).limit(7).all()
        )

    result = []
    for product in products:
        if product.stock == 0:
            status = "Out of Stock"
        elif product.stock < product.alert_threshold:
            status = "Low Stock"
        else:
            status = "In Stock"

        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "price": product.price,
                "status": status,
            }
        )

    return jsonify(result), 200


# ---------- Search Inventory by Name ----------
@inventory_bp.route("/search", methods=["GET"])
@login_required
@cached_with_user(timeout=30)  # Cache search results for 30 seconds
def search_inventory():
    """
    Search inventory by product name or category name.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    products = (
        Product.query.join(Category)
        .filter((Product.name.like(f"%{query}%")) | (Category.name.like(f"%{query}%")))
        .order_by(Product.id.desc())
        .limit(7)
        .all()
    )

    result = []
    for product in products:
        if product.stock == 0:
            status = "Out of Stock"
        elif product.stock < product.alert_threshold:
            status = "Low Stock"
        else:
            status = "In Stock"

        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "price": product.price,
                "status": status,
            }
        )

    return jsonify(result), 200
