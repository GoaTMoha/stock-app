"""
Database transaction utilities for the Stock Manager App.
Provides atomic transaction handling for complex operations.
"""

from contextlib import contextmanager
from typing import Generator, Any
from .extensions import db
from .validation import handle_database_error


@contextmanager
def atomic_transaction() -> Generator[None, None, None]:
    """
    Context manager for atomic database transactions.
    Automatically rolls back on exceptions, commits on success.
    
    Usage:
        with atomic_transaction():
            # Database operations here
            # Will be committed if no exceptions occur
            # Will be rolled back if any exception occurs
    """
    try:
        db.session.begin()
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


def safe_execute(operation_func, *args, **kwargs) -> tuple[bool, Any]:
    """
    Safely execute a database operation with automatic rollback on failure.
    
    Args:
        operation_func: Function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        tuple: (success: bool, result: Any)
    """
    try:
        with atomic_transaction():
            result = operation_func(*args, **kwargs)
        return True, result
    except Exception as e:
        return False, str(e)


def validate_stock_availability(product_id: int, requested_quantity: int) -> tuple[bool, str]:
    """
    Validate if sufficient stock is available for a product.
    
    Args:
        product_id: ID of the product
        requested_quantity: Quantity requested
    
    Returns:
        tuple: (is_available: bool, message: str)
    """
    from .models import Product
    
    product = Product.query.get(product_id)
    if not product:
        return False, f"Product ID {product_id} not found"
    
    if product.stock < requested_quantity:
        return False, f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {requested_quantity}"
    
    return True, "Stock available"


def update_product_stock(product_id: int, quantity_change: int) -> bool:
    """
    Update product stock by a given quantity change.
    Positive values increase stock, negative values decrease stock.
    
    Args:
        product_id: ID of the product
        quantity_change: Change in stock quantity
    
    Returns:
        bool: True if successful, False otherwise
    """
    from .models import Product
    
    try:
        product = Product.query.get(product_id)
        if not product:
            return False
        
        new_stock = product.stock + quantity_change
        if new_stock < 0:
            return False  # Prevent negative stock
        
        product.stock = new_stock
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def create_sale_with_items(client_id: int, sale_items: list) -> tuple[bool, Any]:
    """
    Create a sale with multiple items atomically.
    
    Args:
        client_id: ID of the client
        sale_items: List of sale items with product_id, quantity, price
    
    Returns:
        tuple: (success: bool, result: Any)
    """
    from .models import Sale, SaleItem, Product
    
    def _create_sale():
        # Validate all products and calculate total
        total_price = 0
        total_items = 0
        
        for item in sale_items:
            product_id = item['product_id']
            quantity = item['quantity']
            price = item['price']
            
            # Validate stock availability
            is_available, message = validate_stock_availability(product_id, quantity)
            if not is_available:
                raise ValueError(message)
            
            total_price += price * quantity
            total_items += quantity
        
        # Create sale record
        sale = Sale(
            client_id=client_id,
            total=total_price,
            items_count=total_items
        )
        db.session.add(sale)
        db.session.flush()  # Get the sale ID
        
        # Create sale items and update stock
        for item in sale_items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(sale_item)
            
            # Update product stock
            product = Product.query.get(item['product_id'])
            product.stock -= item['quantity']
        
        return sale
    
    return safe_execute(_create_sale)


def create_purchase_with_items(supplier: str, purchase_items: list) -> tuple[bool, Any]:
    """
    Create a purchase with multiple items atomically.
    
    Args:
        supplier: Name of the supplier
        purchase_items: List of purchase items with product_id, quantity, unit_price
    
    Returns:
        tuple: (success: bool, result: Any)
    """
    from .models import Purchase, PurchaseItem, Product
    
    def _create_purchase():
        # Calculate total cost
        total_cost = 0
        items_count = len(purchase_items)
        
        for item in purchase_items:
            total_cost += item['unit_price'] * item['quantity']
        
        # Create purchase record
        purchase = Purchase(
            supplier=supplier,
            total=total_cost,
            items_count=items_count
        )
        db.session.add(purchase)
        db.session.flush()  # Get the purchase ID
        
        # Create purchase items and update stock
        for item in purchase_items:
            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )
            db.session.add(purchase_item)
            
            # Update product stock
            product = Product.query.get(item['product_id'])
            product.stock += item['quantity']
        
        return purchase
    
    return safe_execute(_create_purchase)
