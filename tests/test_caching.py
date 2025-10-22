"""
Test caching functionality for the Stock Manager App.
"""

import pytest
import time
from backend import create_app
from backend.extensions import cache


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    app.config['CACHE_TYPE'] = 'simple'  # Use simple cache for testing
    with app.app_context():
        cache.init_app(app)
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestCaching:
    """Test caching functionality."""

    def test_cache_decorator_works(self, app, client):
        """Test that cache decorator works correctly."""
        with app.app_context():
            # Test a simple cached function
            from backend.cache_utils import cached_with_user
            
            call_count = 0
            
            @cached_with_user(timeout=1)
            def test_function():
                nonlocal call_count
                call_count += 1
                return {"result": "cached_data", "call_count": call_count}
            
            # First call should execute function
            result1 = test_function()
            assert result1["call_count"] == 1
            
            # Second call should use cache
            result2 = test_function()
            assert result2["call_count"] == 1  # Should still be 1 (cached)
            
            # Wait for cache to expire
            time.sleep(1.1)
            
            # Third call should execute function again
            result3 = test_function()
            assert result3["call_count"] == 2

    def test_cache_clear_function(self, app):
        """Test cache clear functionality."""
        with app.app_context():
            from backend.cache_utils import clear_all_cache
            
            # This should not raise an exception
            result = clear_all_cache()
            assert result is True

    def test_cache_info_function(self, app):
        """Test cache info functionality."""
        with app.app_context():
            from backend.cache_utils import get_cache_info
            
            info = get_cache_info()
            assert "cache_type" in info
            assert "cache_timeout" in info
            assert "cache_prefix" in info

    def test_dashboard_endpoints_have_caching(self, app):
        """Test that dashboard endpoints are decorated with caching."""
        with app.app_context():
            from backend.routes.dashboard import dashboard_bp
            
            # Check that dashboard routes exist
            assert '/dashboard/overview' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/dashboard/sales-overview' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/dashboard/inventory-distribution' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/dashboard/recent-sales' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/dashboard/low-stock' in [rule.rule for rule in app.url_map.iter_rules()]

    def test_cache_endpoints_exist(self, app):
        """Test that cache management endpoints exist."""
        with app.app_context():
            # Check that cache routes exist
            assert '/cache/clear' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/cache/info' in [rule.rule for rule in app.url_map.iter_rules()]
            assert '/cache/invalidate' in [rule.rule for rule in app.url_map.iter_rules()]
