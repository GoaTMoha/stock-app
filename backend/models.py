from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .extensions import db

# Use Flask-SQLAlchemy's db.Model instead of declarative_base


# ---------------------------
# USER MODEL
# ---------------------------
class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# ---------------------------
# CLIENT MODEL
# ---------------------------
class Client(db.Model):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="client", cascade="all, delete-orphan")


# ---------------------------
# CATEGORY MODEL
# ---------------------------
class Category(db.Model):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    products = relationship("Product", back_populates="category")


# ---------------------------
# PRODUCT MODEL
# ---------------------------
class Product(db.Model):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    alert_threshold = Column(Integer, default=5)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Add database constraints
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
        CheckConstraint('alert_threshold >= 0', name='check_alert_threshold_non_negative'),
    )

    category = relationship("Category", back_populates="products")
    sales_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")


# ---------------------------
# SALE MODEL
# ---------------------------
class Sale(db.Model):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0.0)
    items_count = Column(Integer, default=0)

    # Add database constraints
    __table_args__ = (
        CheckConstraint('total >= 0', name='check_sale_total_non_negative'),
        CheckConstraint('items_count >= 0', name='check_sale_items_count_non_negative'),
    )

    client = relationship("Client", back_populates="sales")
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )


# ---------------------------
# SALE ITEM MODEL
# ---------------------------
class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Add database constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_sale_item_quantity_positive'),
        CheckConstraint('price > 0', name='check_sale_item_price_positive'),
    )

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sales_items")


# ---------------------------
# PURCHASE MODEL
# ---------------------------
class Purchase(db.Model):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    supplier = Column(String(100), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0.0)
    items_count = Column(Integer, default=0)

    # Add database constraints
    __table_args__ = (
        CheckConstraint('total >= 0', name='check_purchase_total_non_negative'),
        CheckConstraint('items_count >= 0', name='check_purchase_items_count_non_negative'),
    )

    items = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )


# ---------------------------
# PURCHASE ITEM MODEL
# ---------------------------
class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Add database constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_purchase_item_quantity_positive'),
        CheckConstraint('unit_price > 0', name='check_purchase_item_unit_price_positive'),
    )

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")
