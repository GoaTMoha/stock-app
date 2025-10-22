"""
Cache management routes for the Stock Manager App.

This module provides endpoints for managing the cache, including clearing cache
and getting cache information for administrative purposes.
"""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from ..cache_utils import clear_all_cache, get_cache_info, invalidate_cache_pattern
import logging

logger = logging.getLogger(__name__)

cache_bp = Blueprint("cache", __name__, url_prefix="/cache")


@cache_bp.route("/clear", methods=["POST"])
@login_required
def clear_cache():
    """
    Clear all cached data.
    Requires authentication.
    """
    try:
        success = clear_all_cache()
        if success:
            logger.info(f"Cache cleared by user {current_user.id}")
            return jsonify({"message": "Cache cleared successfully"}), 200
        else:
            return jsonify({"error": "Failed to clear cache"}), 500
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"error": "Internal server error"}), 500


@cache_bp.route("/info", methods=["GET"])
@login_required
def cache_info():
    """
    Get information about the current cache configuration.
    """
    try:
        info = get_cache_info()
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return jsonify({"error": "Internal server error"}), 500


@cache_bp.route("/invalidate", methods=["POST"])
@login_required
def invalidate_cache():
    """
    Invalidate cache entries matching a pattern.
    Body: {"pattern": "dashboard:*"}
    """
    from flask import request
    
    data = request.get_json()
    if not data or "pattern" not in data:
        return jsonify({"error": "Pattern required"}), 400
    
    pattern = data["pattern"]
    try:
        invalidate_cache_pattern(pattern)
        logger.info(f"Cache invalidation requested for pattern: {pattern} by user {current_user.id}")
        return jsonify({"message": f"Cache invalidation requested for pattern: {pattern}"}), 200
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return jsonify({"error": "Internal server error"}), 500
