from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..extensions import db
from ..models import Product, Category
from ..validation import (
    validate_product_data,
    validate_category_data,
    handle_validation_error,
    handle_database_error,
    handle_not_found_error,
)
from ..cache_utils import cached_with_user

products_bp = Blueprint("products", __name__, url_prefix="/products")


# ---------- Add New Category ----------
@products_bp.route("/categories/add", methods=["POST"])
@login_required
def add_category():
    """
    Add a new category:
    {
        "name": "Electronics"
    }
    """
    data = request.get_json()

    if not data:
        return handle_validation_error("No data provided")

    # Validate input data
    is_valid, error_message = validate_category_data(data)
    if not is_valid:
        return handle_validation_error(error_message)

    # Check if category already exists
    if Category.query.filter_by(name=data["name"]).first():
        return handle_validation_error("Category already exists")

    try:
        category = Category(name=data["name"])

        db.session.add(category)
        db.session.commit()

        return (
            jsonify(
                {"message": "Category added successfully", "category_id": category.id}
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return handle_database_error(f"Failed to add category: {str(e)}")


# ---------- Add New Product ----------
@products_bp.route("/add", methods=["POST"])
@login_required
def add_product():
    """
    Add a new product:
    {
        "name": "Laptop",
        "category_id": 1,
        "price": 1500.0,
        "stock": 10,
        "alert_threshold": 5,
        "description": "High-performance laptop"
    }
    """
    data = request.get_json()

    if not data:
        return handle_validation_error("No data provided")

    # Validate input data
    is_valid, error_message = validate_product_data(data)
    if not is_valid:
        return handle_validation_error(error_message)

    # Check if product already exists
    if Product.query.filter_by(name=data["name"]).first():
        return handle_validation_error("Product with this name already exists")

    # Validate category exists
    category = Category.query.get(data["category_id"])
    if not category:
        return handle_not_found_error("Category")

    try:
        product = Product(
            name=data["name"],
            category_id=data["category_id"],
            price=float(data["price"]),
            stock=int(data["stock"]),
            alert_threshold=int(data.get("alert_threshold", 5)),
            description=data.get("description", ""),
        )

        db.session.add(product)
        db.session.commit()

        return (
            jsonify(
                {"message": "Product added successfully", "product_id": product.id}
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return handle_database_error(f"Failed to add product: {str(e)}")


# ---------- Search Products ----------
@products_bp.route("/search", methods=["GET"])
@login_required
@cached_with_user(timeout=30)  # Cache search results for 30 seconds
def search_products():
    """
    Search products by name or category.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    products = (
        Product.query.join(Category)
        .filter((Product.name.like(f"%{query}%")) | (Category.name.like(f"%{query}%")))
        .order_by(Product.created_at.desc())
        .limit(7)
        .all()
    )

    result = []
    for product in products:
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "price": product.price,
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "description": product.description,
                "created_at": product.created_at.isoformat(),
            }
        )

    return jsonify(result), 200


# ---------- Get Recent Products ----------
@products_bp.route("/recent", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache recent products for 60 seconds
def recent_products():
    """
    Get 7 most recently added products.
    """
    products = (
        Product.query.join(Category).order_by(Product.created_at.desc()).limit(7).all()
    )

    result = []
    for product in products:
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "price": product.price,
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "description": product.description,
                "created_at": product.created_at.isoformat(),
            }
        )

    return jsonify(result), 200


# ---------- Get All Categories ----------
@products_bp.route("/categories", methods=["GET"])
@login_required
@cached_with_user(timeout=300)  # Cache categories for 5 minutes (rarely change)
def get_categories():
    """
    Get all categories.
    """
    categories = Category.query.order_by(Category.name.asc()).all()

    result = []
    for category in categories:
        result.append(
            {
                "id": category.id,
                "name": category.name,
                "product_count": len(category.products),
            }
        )

    return jsonify(result), 200


# ---------- Get All Products ----------
@products_bp.route("/all", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache all products for 60 seconds
def get_all_products():
    """
    Get all products.
    """
    products = Product.query.join(Category).order_by(Product.name.asc()).all()

    result = []
    for product in products:
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category.name
                if product.category
                else "Uncategorized",
                "price": product.price,
                "stock": product.stock,
                "alert_threshold": product.alert_threshold,
                "description": product.description,
                "created_at": product.created_at.isoformat(),
            }
        )

    return jsonify(result), 200
