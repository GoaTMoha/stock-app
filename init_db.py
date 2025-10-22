#!/usr/bin/env python3
"""
Database initialization script for Stock Manager App.
This script creates the database tables and optionally seeds with sample data.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app
from backend.extensions import db
from backend.models import User, Client, Product, Category, Sale, SaleItem, Purchase, PurchaseItem
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with tables."""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")
        
        # Check if we already have data
        if User.query.first():
            print("Database already contains data. Skipping seed data.")
            return
        
        # Create sample data
        create_sample_data()
        print("Sample data created successfully.")

def create_sample_data():
    """Create sample data for testing and demonstration."""
    
    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@stockapp.com',
        password_hash=generate_password_hash('admin123')
    )
    db.session.add(admin_user)
    
    # Create categories
    categories = [
        Category(name='Electronics'),
        Category(name='Clothing'),
        Category(name='Books'),
        Category(name='Home & Garden'),
        Category(name='Sports')
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.flush()  # Get category IDs
    
    # Create products
    products = [
        Product(
            name='Laptop Computer',
            category_id=1,
            price=1200.00,
            stock=15,
            alert_threshold=5,
            description='High-performance laptop for business use'
        ),
        Product(
            name='Wireless Mouse',
            category_id=1,
            price=25.99,
            stock=50,
            alert_threshold=10,
            description='Ergonomic wireless mouse'
        ),
        Product(
            name='Cotton T-Shirt',
            category_id=2,
            price=19.99,
            stock=100,
            alert_threshold=20,
            description='Comfortable cotton t-shirt'
        ),
        Product(
            name='Python Programming Book',
            category_id=3,
            price=45.00,
            stock=25,
            alert_threshold=5,
            description='Learn Python programming'
        ),
        Product(
            name='Garden Hose',
            category_id=4,
            price=35.50,
            stock=8,
            alert_threshold=3,
            description='50ft garden hose'
        ),
        Product(
            name='Running Shoes',
            category_id=5,
            price=89.99,
            stock=12,
            alert_threshold=4,
            description='Comfortable running shoes'
        )
    ]
    
    for product in products:
        db.session.add(product)
    
    # Create clients
    clients = [
        Client(
            name='John Smith',
            email='john.smith@email.com',
            phone='555-0101',
            address='123 Main St, Anytown, USA'
        ),
        Client(
            name='Sarah Johnson',
            email='sarah.j@email.com',
            phone='555-0102',
            address='456 Oak Ave, Somewhere, USA'
        ),
        Client(
            name='Mike Wilson',
            email='mike.wilson@email.com',
            phone='555-0103',
            address='789 Pine Rd, Elsewhere, USA'
        ),
        Client(
            name='Lisa Brown',
            email='lisa.brown@email.com',
            phone='555-0104',
            address='321 Elm St, Nowhere, USA'
        )
    ]
    
    for client in clients:
        db.session.add(client)
    
    db.session.commit()
    
    # Create sample sales
    create_sample_sales()
    
    # Create sample purchases
    create_sample_purchases()

def create_sample_sales():
    """Create sample sales data."""
    clients = Client.query.all()
    products = Product.query.all()
    
    if not clients or not products:
        return
    
    # Sale 1
    sale1 = Sale(
        client_id=clients[0].id,
        total=1245.99,
        items_count=2
    )
    db.session.add(sale1)
    db.session.flush()
    
    # Sale 1 items
    sale1_items = [
        SaleItem(sale_id=sale1.id, product_id=products[0].id, quantity=1, price=1200.00),
        SaleItem(sale_id=sale1.id, product_id=products[1].id, quantity=2, price=25.99)
    ]
    
    for item in sale1_items:
        db.session.add(item)
        # Update product stock
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity
    
    # Sale 2
    sale2 = Sale(
        client_id=clients[1].id,
        total=64.99,
        items_count=2
    )
    db.session.add(sale2)
    db.session.flush()
    
    # Sale 2 items
    sale2_items = [
        SaleItem(sale_id=sale2.id, product_id=products[2].id, quantity=2, price=19.99),
        SaleItem(sale_id=sale2.id, product_id=products[3].id, quantity=1, price=45.00)
    ]
    
    for item in sale2_items:
        db.session.add(item)
        # Update product stock
        product = Product.query.get(item.product_id)
        product.stock -= item.quantity

def create_sample_purchases():
    """Create sample purchase data."""
    products = Product.query.all()
    
    if not products:
        return
    
    # Purchase 1
    purchase1 = Purchase(
        supplier='Tech Supply Co',
        total=6000.00,
        items_count=2
    )
    db.session.add(purchase1)
    db.session.flush()
    
    # Purchase 1 items
    purchase1_items = [
        PurchaseItem(purchase_id=purchase1.id, product_id=products[0].id, quantity=5, unit_price=1200.00),
        PurchaseItem(purchase_id=purchase1.id, product_id=products[1].id, quantity=20, unit_price=25.99)
    ]
    
    for item in purchase1_items:
        db.session.add(item)
        # Update product stock
        product = Product.query.get(item.product_id)
        product.stock += item.quantity
    
    # Purchase 2
    purchase2 = Purchase(
        supplier='Fashion Wholesale',
        total=1999.00,
        items_count=1
    )
    db.session.add(purchase2)
    db.session.flush()
    
    # Purchase 2 items
    purchase2_items = [
        PurchaseItem(purchase_id=purchase2.id, product_id=products[2].id, quantity=100, unit_price=19.99)
    ]
    
    for item in purchase2_items:
        db.session.add(item)
        # Update product stock
        product = Product.query.get(item.product_id)
        product.stock += item.quantity

if __name__ == '__main__':
    print("Initializing Stock Manager App Database...")
    init_database()
    print("Database initialization complete!")
    print("\nSample login credentials:")
    print("   Username: admin")
    print("   Email: admin@stockapp.com")
    print("   Password: admin123")
