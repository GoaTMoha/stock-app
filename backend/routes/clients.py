from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..extensions import db
from ..models import Client
from ..validation import (
    validate_client_data,
    handle_validation_error,
    handle_database_error,
    handle_not_found_error,
)
from ..cache_utils import cached_with_user

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


# ---------- Add New Client ----------
@clients_bp.route("/add", methods=["POST"])
@login_required
def add_client():
    """
    Add a new client:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "address": "123 Main St"
    }
    """
    data = request.get_json()

    if not data:
        return handle_validation_error("No data provided")

    # Validate input data
    is_valid, error_message = validate_client_data(data)
    if not is_valid:
        return handle_validation_error(error_message)

    # Check if client already exists
    if Client.query.filter_by(email=data["email"]).first():
        return handle_validation_error("Client with this email already exists")

    if Client.query.filter_by(phone=data["phone"]).first():
        return handle_validation_error("Client with this phone already exists")

    try:
        client = Client(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
        )

        db.session.add(client)
        db.session.commit()

        return (
            jsonify({"message": "Client added successfully", "client_id": client.id}),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return handle_database_error(f"Failed to add client: {str(e)}")


# ---------- Search Clients ----------
@clients_bp.route("/search", methods=["GET"])
@login_required
@cached_with_user(timeout=30)  # Cache search results for 30 seconds
def search_clients():
    """
    Search clients by name, email, or phone.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    clients = (
        Client.query.filter(
            (Client.name.like(f"%{query}%"))
            | (Client.email.like(f"%{query}%"))
            | (Client.phone.like(f"%{query}%"))
        )
        .order_by(Client.created_at.desc())
        .limit(7)
        .all()
    )

    result = []
    for client in clients:
        result.append(
            {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "phone": client.phone,
                "address": client.address,
                "created_at": client.created_at.isoformat(),
            }
        )

    return jsonify(result), 200


# ---------- Get Recent Clients ----------
@clients_bp.route("/recent", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache recent clients for 60 seconds
def recent_clients():
    """
    Get 7 most recently added clients.
    """
    clients = Client.query.order_by(Client.created_at.desc()).limit(7).all()

    result = []
    for client in clients:
        result.append(
            {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "phone": client.phone,
                "address": client.address,
                "created_at": client.created_at.isoformat(),
            }
        )

    return jsonify(result), 200


# ---------- Get All Clients ----------
@clients_bp.route("/all", methods=["GET"])
@login_required
@cached_with_user(timeout=60)  # Cache all clients for 60 seconds
def get_all_clients():
    """
    Get all clients.
    """
    clients = Client.query.order_by(Client.name.asc()).all()

    result = []
    for client in clients:
        result.append(
            {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "phone": client.phone,
                "address": client.address,
                "created_at": client.created_at.isoformat(),
            }
        )

    return jsonify(result), 200
