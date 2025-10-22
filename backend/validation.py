"""
Validation utilities for the Stock Manager App.
Provides centralized input validation and error handling.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from flask import jsonify


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validator:
    """Centralized validation class for all input data."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it has 10-15 digits
        return 10 <= len(digits) <= 15
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present."""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 1, max_length: int = 255, field_name: str = "field") -> None:
        """Validate string length."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters long")
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: float = 0, max_val: float = float('inf'), field_name: str = "field") -> None:
        """Validate numeric range."""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a number")
        
        if num_value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        if num_value > max_val:
            raise ValidationError(f"{field_name} must be no more than {max_val}")
    
    @staticmethod
    def validate_positive_integer(value: Any, field_name: str = "field") -> None:
        """Validate positive integer."""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer")
        
        if int_value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer")


def validate_client_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate client data."""
    try:
        Validator.validate_required_fields(data, ['name', 'email', 'phone', 'address'])
        
        # Validate name
        Validator.validate_string_length(data['name'], 1, 100, "Name")
        
        # Validate email
        if not Validator.validate_email(data['email']):
            raise ValidationError("Invalid email format")
        
        # Validate phone
        if not Validator.validate_phone(data['phone']):
            raise ValidationError("Invalid phone number format")
        
        # Validate address
        Validator.validate_string_length(data['address'], 1, 200, "Address")
        
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_product_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate product data."""
    try:
        Validator.validate_required_fields(data, ['name', 'category_id', 'price', 'stock'])
        
        # Validate name
        Validator.validate_string_length(data['name'], 1, 100, "Product name")
        
        # Validate category_id
        Validator.validate_positive_integer(data['category_id'], "Category ID")
        
        # Validate price
        Validator.validate_numeric_range(data['price'], 0.01, 999999.99, "Price")
        
        # Validate stock
        Validator.validate_numeric_range(data['stock'], 0, 999999, "Stock")
        
        # Validate alert_threshold if provided
        if 'alert_threshold' in data:
            Validator.validate_numeric_range(data['alert_threshold'], 0, 999999, "Alert threshold")
        
        # Validate description if provided
        if 'description' in data and data['description']:
            Validator.validate_string_length(data['description'], 0, 500, "Description")
        
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_sale_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate sale data."""
    try:
        Validator.validate_required_fields(data, ['client_search', 'products'])
        
        # Validate client_search
        Validator.validate_string_length(data['client_search'], 1, 200, "Client search")
        
        # Validate products
        products = data['products']
        if not isinstance(products, list) or len(products) == 0:
            raise ValidationError("At least one product is required")
        
        for i, product in enumerate(products):
            if not isinstance(product, dict):
                raise ValidationError(f"Product {i+1} must be an object")
            
            Validator.validate_required_fields(product, ['product_id', 'quantity'])
            Validator.validate_positive_integer(product['product_id'], f"Product {i+1} ID")
            Validator.validate_positive_integer(product['quantity'], f"Product {i+1} quantity")
        
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_purchase_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate purchase data."""
    try:
        Validator.validate_required_fields(data, ['supplier', 'items'])
        
        # Validate supplier
        Validator.validate_string_length(data['supplier'], 1, 100, "Supplier")
        
        # Validate items
        items = data['items']
        if not isinstance(items, list) or len(items) == 0:
            raise ValidationError("At least one item is required")
        
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValidationError(f"Item {i+1} must be an object")
            
            Validator.validate_required_fields(item, ['product_id', 'quantity', 'unit_price'])
            Validator.validate_positive_integer(item['product_id'], f"Item {i+1} product ID")
            Validator.validate_positive_integer(item['quantity'], f"Item {i+1} quantity")
            Validator.validate_numeric_range(item['unit_price'], 0.01, 999999.99, f"Item {i+1} unit price")
        
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_category_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate category data."""
    try:
        Validator.validate_required_fields(data, ['name'])
        
        # Validate name
        Validator.validate_string_length(data['name'], 1, 50, "Category name")
        
        return True, None
    except ValidationError as e:
        return False, str(e)


def handle_validation_error(error_message: str, status_code: int = 400):
    """Return a standardized validation error response."""
    return jsonify({"error": error_message}), status_code


def handle_database_error(error_message: str = "Database operation failed", status_code: int = 500):
    """Return a standardized database error response."""
    return jsonify({"error": error_message}), status_code


def handle_not_found_error(resource: str = "Resource"):
    """Return a standardized not found error response."""
    return jsonify({"error": f"{resource} not found"}), 404
