"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# Product Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductHierarchyBase(BaseModel):
    hierarchy_level: str
    hierarchy_name: str
    parent_hierarchy_id: Optional[int] = None
    hierarchy_path: Optional[str] = None


class ProductBase(BaseModel):
    product_name: str
    product_description: Optional[str] = None
    brand_name: Optional[str] = None
    hierarchy_id: Optional[int] = None
    product_type: Optional[str] = None
    gender: Optional[str] = None
    season: Optional[str] = None
    year: Optional[int] = None
    status: str = "ACTIVE"
    product_metadata: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    variant_name: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    pattern: Optional[str] = None
    variant_attributes: Optional[Dict[str, Any]] = None


class ProductVariantCreate(ProductVariantBase):
    product_id: int


class SKUBase(BaseModel):
    sku_code: str
    price: Decimal
    cost: Optional[Decimal] = None
    currency: str = "USD"
    inventory_quantity: int = 0
    reorder_point: int = 10
    status: str = "ACTIVE"


class SKUCreate(SKUBase):
    variant_id: int


class SKUResponse(SKUBase):
    sku_id: int
    variant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer Schemas
class CustomerBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "USA"


class CustomerCreate(CustomerBase):
    password: str


class CustomerResponse(CustomerBase):
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StyleProfileBase(BaseModel):
    style_preferences: Optional[Dict[str, Any]] = None
    favorite_colors: Optional[List[str]] = None
    size_preferences: Optional[Dict[str, Any]] = None
    price_range_min: Optional[Decimal] = None
    price_range_max: Optional[Decimal] = None
    brand_preferences: Optional[List[str]] = None
    occasion_preferences: Optional[List[str]] = None


class StyleProfileCreate(StyleProfileBase):
    customer_id: int


# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_title: Optional[str] = None
    review_text: Optional[str] = None
    verified_purchase: bool = False


class ReviewCreate(ReviewBase):
    product_id: int
    customer_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    review_id: int
    product_id: int
    customer_id: Optional[int]
    helpful_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderLineItemCreate(BaseModel):
    sku_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal
    discount_amount: Decimal = 0


class OrderCreate(BaseModel):
    customer_id: int
    line_items: List[OrderLineItemCreate]
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    order_number: str
    order_date: datetime
    order_status: str
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


# Return Schemas
class ReturnRequestCreate(BaseModel):
    order_id: int
    line_item_id: Optional[int] = None
    return_reason: str
    notes: Optional[str] = None


class ReturnRequestResponse(BaseModel):
    return_id: int
    order_id: int
    return_reason: str
    return_status: str
    requested_date: datetime
    refund_amount: Optional[Decimal] = None

    class Config:
        from_attributes = True


# Search Schemas
class ProductSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    offset: int = 0


class VectorSearchRequest(BaseModel):
    query_embedding: List[float]
    limit: int = 20
    threshold: float = 0.7


# Agent Schemas
class AgentRequest(BaseModel):
    message: str
    customer_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    agent_name: str
    response: str
    actions_taken: List[Dict[str, Any]]
    confidence: float
    reasoning: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

