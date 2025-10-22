"""
Security utilities for the Stock Manager App.
Provides security-related helper functions and configurations.
"""

import re
import hashlib
import secrets
from typing import Optional
from flask import request, current_app
from werkzeug.security import generate_password_hash, check_password_hash


class SecurityValidator:
    """Security validation utilities."""
    
    @staticmethod
    def is_strong_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
        
        Returns:
            tuple: (is_strong: bool, message: str)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize user input to prevent XSS attacks.
        
        Args:
            input_string: Input string to sanitize
        
        Returns:
            str: Sanitized string
        """
        if not isinstance(input_string, str):
            return str(input_string)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', 'script', 'javascript']
        
        sanitized = input_string
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email_security(email: str) -> tuple[bool, str]:
        """
        Validate email for security concerns.
        
        Args:
            email: Email to validate
        
        Returns:
            tuple: (is_safe: bool, message: str)
        """
        if not email or len(email) > 254:
            return False, "Invalid email length"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'@.*@',    # Multiple @ symbols
            r'[<>]',    # HTML tags
            r'javascript:',  # JavaScript protocol
            r'data:',   # Data protocol
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False, "Email contains suspicious content"
        
        return True, "Email is safe"


class PasswordManager:
    """Password management utilities."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using werkzeug's secure hashing.
        
        Args:
            password: Plain text password
        
        Returns:
            str: Hashed password
        """
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
        
        Returns:
            bool: True if password matches hash
        """
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure token.
        
        Args:
            length: Length of token in bytes
        
        Returns:
            str: Secure token
        """
        return secrets.token_urlsafe(length)


class RequestSecurity:
    """Request security utilities."""
    
    @staticmethod
    def get_client_ip() -> str:
        """
        Get the real client IP address, considering proxies.
        
        Returns:
            str: Client IP address
        """
        # Check for forwarded headers first
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or 'unknown'
    
    @staticmethod
    def is_safe_request() -> tuple[bool, str]:
        """
        Check if the request appears to be safe.
        
        Returns:
            tuple: (is_safe: bool, reason: str)
        """
        # Check User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 10:
            return False, "Suspicious User-Agent"
        
        # Check for common attack patterns in URL
        suspicious_patterns = [
            '..',  # Directory traversal
            '<script',  # XSS attempt
            'javascript:',  # JavaScript protocol
            'data:',  # Data protocol
            'eval(',  # Code injection
            'exec(',  # Code injection
        ]
        
        url = request.url.lower()
        for pattern in suspicious_patterns:
            if pattern in url:
                return False, f"Suspicious pattern detected: {pattern}"
        
        return True, "Request appears safe"
    
    @staticmethod
    def validate_content_length(max_length: int = 1024 * 1024) -> tuple[bool, str]:
        """
        Validate request content length.
        
        Args:
            max_length: Maximum allowed content length in bytes
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        content_length = request.content_length
        if content_length and content_length > max_length:
            return False, f"Content too large: {content_length} bytes"
        
        return True, "Content length is acceptable"


def get_security_headers() -> dict:
    """
    Get security headers to add to responses.
    
    Returns:
        dict: Security headers
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }


def apply_security_headers(response):
    """
    Apply security headers to a Flask response.
    
    Args:
        response: Flask response object
    
    Returns:
        Flask response with security headers
    """
    headers = get_security_headers()
    for header, value in headers.items():
        response.headers[header] = value
    
    return response
