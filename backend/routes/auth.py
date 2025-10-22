from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..extensions import db, limiter
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate email format
    if "@" not in data["email"]:
        return jsonify({"error": "Invalid email format"}), 400

    # Check if user exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 400

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Login user."""
    data = request.get_json()

    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password_hash, data["password"]):
        login_user(user, remember=data.get("remember", False))
        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            ),
            200,
        )

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout user."""
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Get current user info."""
    return (
        jsonify(
            {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
            }
        ),
        200,
    )


@auth_bp.route("/status", methods=["GET"])
def auth_status():
    """Check authentication status."""
    if current_user.is_authenticated:
        return (
            jsonify(
                {
                    "authenticated": True,
                    "user": {
                        "id": current_user.id,
                        "username": current_user.username,
                        "email": current_user.email,
                    },
                }
            ),
            200,
        )
    else:
        return jsonify({"authenticated": False}), 200
