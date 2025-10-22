from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..extensions import db, limiter
from ..models import Sale, SaleItem, Product, Client
from ..validation import (
    validate_sale_data,
    handle_validation_error,
    handle_database_error,
    handle_not_found_error,
)
from ..transactions import create_sale_with_items, validate_stock_availability
from datetime import datetime

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


# ---------- Add a New Sale ----------
@sales_bp.route("/add", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
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

    if not data:
        return handle_validation_error("No data provided")

    # Validate input data
    is_valid, error_message = validate_sale_data(data)
    if not is_valid:
        return handle_validation_error(error_message)

    client_search = data.get("client_search")
    products = data.get("products", [])

    try:
        # Find client by name, email, or phone using ORM
        client = Client.query.filter(
            (Client.name == client_search)
            | (Client.email == client_search)
            | (Client.phone == client_search)
        ).first()

        if not client:
            return handle_not_found_error("Client")

        # Prepare sale items data
        sale_items = []
        for item in products:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)

            # Validate stock availability
            is_available, message = validate_stock_availability(product_id, quantity)
            if not is_available:
                return handle_validation_error(message)

            # Get product price
            product = Product.query.get(product_id)
            if not product:
                return handle_not_found_error("Product")

            sale_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product.price
            })

        # Create sale atomically
        success, result = create_sale_with_items(client.id, sale_items)
        
        if success:
            sale = result
            return (
                jsonify(
                    {
                        "message": "Sale added successfully!",
                        "sale_id": sale.id,
                        "total_items": sale.items_count,
                        "total_price": sale.total,
                    }
                ),
                201,
            )
        else:
            return handle_database_error(f"Failed to add sale: {result}")

    except Exception as e:
        return handle_database_error(f"Failed to add sale: {str(e)}")


# ---------- Search Sales ----------
@sales_bp.route("/search", methods=["GET"])
@login_required
def search_sales():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    sales = (
        db.session.query(Sale)
        .join(Client)
        .filter(
            (Sale.id.like(f"%{query}%"))
            | (Client.name.like(f"%{query}%"))
            | (Client.email.like(f"%{query}%"))
        )
        .order_by(Sale.date.desc())
        .all()
    )

    result = []
    for sale in sales:
        result.append(
            {
                "id": sale.id,
                "client": sale.client.name if sale.client else "Unknown",
                "date": sale.date.isoformat(),
                "total_items": sale.items_count,
                "total_price": sale.total,
            }
        )

    return jsonify(result), 200


# ---------- Get 7 Most Recent Sales ----------
@sales_bp.route("/recent", methods=["GET"])
@login_required
def recent_sales():
    sales = Sale.query.join(Client).order_by(Sale.date.desc()).limit(7).all()

    result = []
    for sale in sales:
        result.append(
            {
                "id": sale.id,
                "client": sale.client.name if sale.client else "Unknown",
                "date": sale.date.isoformat(),
                "total_items": sale.items_count,
                "total_price": sale.total,
            }
        )

    return jsonify(result), 200
