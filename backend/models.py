"""
Oracle Retail Reference Data Model (RDM) - SQLAlchemy Models
Following DDD conventions and Oracle RDM standards
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, 
    Date, DateTime, ForeignKey, JSON, ARRAY, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()


class ProductHierarchy(Base):
    """Product hierarchy: Category, Department, Class, Subclass"""
    __tablename__ = "product_hierarchy"
    __table_args__ = {'schema': 'retail'}

    hierarchy_id = Column(Integer, primary_key=True)
    hierarchy_level = Column(String(50), nullable=False)
    hierarchy_name = Column(String(200), nullable=False)
    parent_hierarchy_id = Column(Integer, ForeignKey('retail.product_hierarchy.hierarchy_id'))
    hierarchy_path = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    children = relationship("ProductHierarchy", backref="parent", remote_side=[hierarchy_id])
    products = relationship("Product", back_populates="hierarchy")


class Product(Base):
    """Master Product entity"""
    __tablename__ = "product"
    __table_args__ = {'schema': 'retail'}

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(500), nullable=False)
    product_description = Column(Text)
    brand_name = Column(String(200))
    hierarchy_id = Column(Integer, ForeignKey('retail.product_hierarchy.hierarchy_id'))
    product_type = Column(String(100))
    gender = Column(String(50))
    season = Column(String(50))
    year = Column(Integer)
    status = Column(String(50), default='ACTIVE')
    embedding = Column(Vector(1536))  # OpenAI ada-002
    product_metadata = Column('metadata', JSON)  # Using 'metadata' as column name, 'product_metadata' as attribute
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    hierarchy = relationship("ProductHierarchy", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    """Product variant: Color, Size, Material variations"""
    __tablename__ = "product_variant"
    __table_args__ = {'schema': 'retail'}

    variant_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('retail.product.product_id', ondelete='CASCADE'), nullable=False)
    variant_name = Column(String(200))
    color = Column(String(100))
    size = Column(String(50))
    material = Column(String(200))
    pattern = Column(String(100))
    variant_attributes = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    product = relationship("Product", back_populates="variants")
    skus = relationship("SKU", back_populates="variant", cascade="all, delete-orphan")


class SKU(Base):
    """Stock Keeping Unit"""
    __tablename__ = "sku"
    __table_args__ = {'schema': 'retail'}

    sku_id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey('retail.product_variant.variant_id', ondelete='CASCADE'), nullable=False)
    sku_code = Column(String(100), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    inventory_quantity = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    status = Column(String(50), default='ACTIVE')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    variant = relationship("ProductVariant", back_populates="skus")
    order_line_items = relationship("OrderLineItem", back_populates="sku")


class Customer(Base):
    """Customer entity"""
    __tablename__ = "customer"
    __table_args__ = {'schema': 'retail'}

    customer_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default='USA')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    style_profile = relationship("StyleProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    event_profiles = relationship("EventProfile", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="customer")


class StyleProfile(Base):
    """Customer style preferences"""
    __tablename__ = "style_profile"
    __table_args__ = {'schema': 'retail'}

    profile_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('retail.customer.customer_id', ondelete='CASCADE'), nullable=False)
    style_preferences = Column(JSON)
    favorite_colors = Column(ARRAY(Text))
    size_preferences = Column(JSON)
    price_range_min = Column(Numeric(10, 2))
    price_range_max = Column(Numeric(10, 2))
    brand_preferences = Column(ARRAY(Text))
    occasion_preferences = Column(ARRAY(Text))
    embedding = Column(Vector(1536))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="style_profile")


class EventProfile(Base):
    """Special event/occasion profiles"""
    __tablename__ = "event_profile"
    __table_args__ = {'schema': 'retail'}

    event_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('retail.customer.customer_id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String(100))
    event_date = Column(Date)
    dress_code = Column(String(100))
    venue_type = Column(String(100))
    guest_count = Column(Integer)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="event_profiles")


class Review(Base):
    """Product reviews"""
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        {'schema': 'retail'}
    )

    review_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('retail.product.product_id', ondelete='CASCADE'), nullable=False)
    customer_id = Column(Integer, ForeignKey('retail.customer.customer_id'))
    rating = Column(Integer, nullable=False)
    review_title = Column(String(200))
    review_text = Column(Text)
    verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")


class Order(Base):
    """Order entity"""
    __tablename__ = "order"
    __table_args__ = {'schema': 'retail'}

    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('retail.customer.customer_id'), nullable=False)
    order_number = Column(String(100), unique=True, nullable=False)
    order_date = Column(DateTime, default=func.now())
    order_status = Column(String(50), default='PENDING')
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    shipping_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    payment_method = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    line_items = relationship("OrderLineItem", back_populates="order", cascade="all, delete-orphan")
    return_requests = relationship("ReturnRequest", back_populates="order")


class OrderLineItem(Base):
    """Order line items"""
    __tablename__ = "order_line_item"
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        {'schema': 'retail'}
    )

    line_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('retail.order.order_id', ondelete='CASCADE'), nullable=False)
    sku_id = Column(Integer, ForeignKey('retail.sku.sku_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    order = relationship("Order", back_populates="line_items")
    sku = relationship("SKU", back_populates="order_line_items")
    return_requests = relationship("ReturnRequest", back_populates="line_item")


class ReturnRequest(Base):
    """Return request entity"""
    __tablename__ = "return_request"
    __table_args__ = {'schema': 'retail'}

    return_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('retail.order.order_id'), nullable=False)
    line_item_id = Column(Integer, ForeignKey('retail.order_line_item.line_item_id'))
    return_reason = Column(String(200))
    return_status = Column(String(50), default='PENDING')
    requested_date = Column(DateTime, default=func.now())
    processed_date = Column(DateTime)
    refund_amount = Column(Numeric(10, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="return_requests")
    line_item = relationship("OrderLineItem", back_populates="return_requests")

