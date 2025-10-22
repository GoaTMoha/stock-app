from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..extensions import db, limiter
from ..models import Purchase, PurchaseItem, Product
from ..validation import (
    validate_purchase_data,
    handle_validation_error,
    handle_database_error,
    handle_not_found_error,
)
from ..transactions import create_purchase_with_items

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


# ---------- Add New Purchase ----------
@purchases_bp.route("/add", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
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

    if not data:
        return handle_validation_error("No data provided")

    # Validate input data
    is_valid, error_message = validate_purchase_data(data)
    if not is_valid:
        return handle_validation_error(error_message)

    supplier = data.get("supplier")
    items = data.get("items", [])

    try:
        # Validate all products exist
        for item in items:
            product_id = item.get("product_id")
            product = Product.query.get(product_id)
            if not product:
                return handle_not_found_error("Product")

        # Create purchase atomically
        success, result = create_purchase_with_items(supplier, items)
        
        if success:
            purchase = result
            return (
                jsonify(
                    {
                        "message": "Purchase added successfully",
                        "purchase_id": purchase.id,
                        "total": purchase.total,
                        "items_count": purchase.items_count,
                    }
                ),
                201,
            )
        else:
            return handle_database_error(f"Failed to add purchase: {result}")

    except Exception as e:
        return handle_database_error(f"Failed to add purchase: {str(e)}")


# ---------- Search Purchases ----------
@purchases_bp.route("/search", methods=["GET"])
@login_required
def search_purchases():
    """
    Search purchases by supplier or date.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    purchases = (
        Purchase.query.filter(
            (Purchase.supplier.like(f"%{query}%")) | (Purchase.date.like(f"%{query}%"))
        )
        .order_by(Purchase.date.desc())
        .limit(7)
        .all()
    )

    result = []
    for purchase in purchases:
        result.append(
            {
                "id": purchase.id,
                "supplier": purchase.supplier,
                "date": purchase.date.isoformat(),
                "total": purchase.total,
                "items_count": purchase.items_count,
            }
        )

    return jsonify(result), 200


# ---------- Get Recent Purchases ----------
@purchases_bp.route("/recent", methods=["GET"])
@login_required
def recent_purchases():
    """
    Get 7 most recent purchases.
    """
    purchases = Purchase.query.order_by(Purchase.date.desc()).limit(7).all()

    result = []
    for purchase in purchases:
        result.append(
            {
                "id": purchase.id,
                "supplier": purchase.supplier,
                "date": purchase.date.isoformat(),
                "total": purchase.total,
                "items_count": purchase.items_count,
            }
        )

    return jsonify(result), 200


# ---------- Get Purchase Details ----------
@purchases_bp.route("/<int:purchase_id>", methods=["GET"])
@login_required
def get_purchase_details(purchase_id):
    """
    Get detailed information about a specific purchase.
    """
    purchase = Purchase.query.get(purchase_id)

    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404

    items = []
    for item in purchase.items:
        items.append(
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "Unknown",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.quantity * item.unit_price,
            }
        )

    return (
        jsonify(
            {
                "id": purchase.id,
                "supplier": purchase.supplier,
                "date": purchase.date.isoformat(),
                "total": purchase.total,
                "items_count": purchase.items_count,
                "items": items,
            }
        ),
        200,
    )
