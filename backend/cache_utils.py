"""
Cache utility functions for the Stock Manager App.

This module provides caching decorators and utilities for improving performance
of frequently accessed endpoints like dashboard analytics, products, and clients.
"""

from functools import wraps
from flask import current_app, request
from flask_login import current_user
from .extensions import cache
import logging

logger = logging.getLogger(__name__)


def cache_key_with_user(*args, **kwargs):
    """
    Generate a cache key that includes the current user ID.
    This ensures that cached data is user-specific.
    """
    user_id = getattr(current_user, 'id', 'anonymous')
    path = request.path
    query_string = request.query_string.decode('utf-8')
    
    # Create a unique key that includes user, path, and query parameters
    key_parts = [str(user_id), path]
    if query_string:
        key_parts.append(query_string)
    
    return ':'.join(key_parts)


def cached_with_user(timeout=None):
    """
    Decorator to cache function results with user-specific cache keys.
    
    Args:
        timeout: Cache timeout in seconds. If None, uses default timeout.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate user-specific cache key
            cache_key = f"{f.__name__}:{cache_key_with_user()}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache HIT for key: {cache_key}")
                return result
            
            # Cache miss - execute function and cache result
            logger.debug(f"Cache MISS for key: {cache_key}")
            result = f(*args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        return decorated_function
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys (supports wildcards)
    """
    try:
        # For Redis backend, we can use pattern matching
        if current_app.config.get('CACHE_TYPE') == 'redis':
            # This would require Redis-specific implementation
            # For now, we'll log the pattern
            logger.info(f"Cache invalidation requested for pattern: {pattern}")
        else:
            # For simple cache, we can't easily do pattern matching
            logger.info(f"Cache invalidation requested for pattern: {pattern} (simple cache)")
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")


def clear_all_cache():
    """
    Clear all cached data.
    """
    try:
        cache.clear()
        logger.info("All cache cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False


def get_cache_info():
    """
    Get information about the current cache configuration.
    """
    return {
        'cache_type': current_app.config.get('CACHE_TYPE', 'unknown'),
        'cache_timeout': current_app.config.get('CACHE_DEFAULT_TIMEOUT', 60),
        'cache_prefix': current_app.config.get('CACHE_KEY_PREFIX', 'stock_app'),
        'redis_host': current_app.config.get('REDIS_HOST', 'localhost'),
        'redis_port': current_app.config.get('REDIS_PORT', 6379),
    }
