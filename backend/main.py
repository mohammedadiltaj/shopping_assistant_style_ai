
"""
FastAPI Main Application
Multi-agent shopping assistant backend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import os

from database import get_db
from models import (
    Product, ProductVariant, SKU, Customer, Order, OrderLineItem,
    Review, ReturnRequest, StyleProfile, ProductHierarchy
)
from schemas import (
    ProductResponse, ProductSearchRequest, CustomerResponse, CustomerCreate,
    OrderCreate, OrderResponse, ReviewCreate, ReviewResponse,
    ReturnRequestCreate, ReturnRequestResponse, SKUResponse,
    AgentRequest, AgentResponse, Token, LoginRequest
)
from agents.orchestrator import AgentOrchestrator
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from models import Customer, Order, OrderLineItem, ReturnRequest, Product
from decimal import Decimal
from typing import List

app = FastAPI(
    title="Multi-Agent Shopping Assistant API",
    description="Production-ready shopping assistant with AI agents",
    version="1.0.0"
)

# CORS middleware
# CORS middleware
origins = ["*"]
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from database import engine
    from models import Base
    from sqlalchemy import text
    
    # Create schema if not exists
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS retail"))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)



@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Shopping Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "search": "/api/products/search",
            "customers": "/api/customers",
            "orders": "/api/orders",
            "agent": "/api/agent/chat"
        }
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Product Endpoints
@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    gender: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get products with optional filtering"""
    query = db.query(Product).filter(Product.status == "ACTIVE")
    
    if category:
        query = query.join(ProductHierarchy).filter(
            ProductHierarchy.hierarchy_name.ilike(f"%{category}%")
        )
    
    if gender:
        query = query.filter(Product.gender == gender)
    
    products = query.offset(skip).limit(limit).all()
    return products


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/products/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search products by name, description, or brand"""
    search_term = f"%{q}%"
    products = db.query(Product).filter(
        or_(
            Product.product_name.ilike(search_term),
            Product.product_description.ilike(search_term),
            Product.brand_name.ilike(search_term)
        ),
        Product.status == "ACTIVE"
    ).limit(limit).all()
    
    return products


@app.get("/api/products/{product_id}/skus", response_model=List[SKUResponse])
async def get_product_skus(product_id: int, db: Session = Depends(get_db)):
    """Get all SKUs for a product"""
    skus = db.query(SKU).join(ProductVariant).filter(
        ProductVariant.product_id == product_id,
        SKU.status == "ACTIVE"
    ).all()
    return skus


@app.get("/api/products/{product_id}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get reviews for a product"""
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    return reviews


# Auth Endpoints
@app.post("/api/auth/register", response_model=CustomerResponse)
async def register(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Register a new customer"""
    db_user = db.query(Customer).filter(Customer.email == customer.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(customer.password)
    db_customer = Customer(
        email=customer.email,
        password_hash=hashed_password,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        date_of_birth=customer.date_of_birth,
        gender=customer.gender,
        address_line1=customer.address_line1,
        address_line2=customer.address_line2,
        city=customer.city,
        state=customer.state,
        postal_code=customer.postal_code,
        country=customer.country
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.post("/api/auth/login", response_model=Token)
async def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(Customer).filter(Customer.email == login_req.email).first()
    if not user or not user.password_hash or not verify_password(login_req.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.customer_id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Customer Endpoints
@app.post("/api/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer (also supports registration logic)"""
    return await register(customer, db)


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


from fastapi.security import OAuth2PasswordBearer
from auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(Customer).filter(Customer.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Order Endpoints
@app.post("/api/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate, 
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Calculate totals
    subtotal = sum(item.unit_price * item.quantity for item in order.line_items)
    shipping = Decimal('10.0') if subtotal < 50 else Decimal('0.0')
    tax = subtotal * Decimal('0.08')
    total = subtotal + shipping + tax
    
    # Generate order number
    import uuid
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    db_order = Order(
        customer_id=order.customer_id,
        order_number=order_number,
        subtotal=subtotal,
        tax_amount=tax,
        shipping_amount=shipping,
        total_amount=total,
        shipping_address=order.shipping_address,
        billing_address=order.billing_address,
        payment_method=order.payment_method
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create line items
    for item in order.line_items:
        line_item = OrderLineItem(
            order_id=db_order.order_id,
            sku_id=item.sku_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.unit_price * item.quantity
        )
        db.add(line_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(customer_id: int, db: Session = Depends(get_db)):
    """Get orders for a customer"""
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()


# Return Endpoints
@app.post("/api/returns", response_model=ReturnRequestResponse)
async def create_return_request(
    return_req: ReturnRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new return request"""
    # Verify order exists
    order = db.query(Order).filter(Order.order_id == return_req.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    db_return = ReturnRequest(
        order_id=return_req.order_id,
        line_item_id=return_req.line_item_id,
        return_reason=return_req.return_reason,
        notes=return_req.notes,
        return_status="PENDING"
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)
    return db_return


@app.get("/api/returns", response_model=List[ReturnRequestResponse])
async def get_returns(customer_id: int, db: Session = Depends(get_db)):
    """Get return requests for a customer"""
    return db.query(ReturnRequest).join(Order).filter(Order.customer_id == customer_id).order_by(ReturnRequest.requested_date.desc()).all()


@app.get("/api/customers/{customer_id}/style-profile")
async def get_style_profile(customer_id: int, db: Session = Depends(get_db)):
    """Get customer style profile"""
    profile = db.query(StyleProfile).filter(
        StyleProfile.customer_id == customer_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Style profile not found")
    return {
        "profile_id": profile.profile_id,
        "customer_id": profile.customer_id,
        "style_preferences": profile.style_preferences,
        "favorite_colors": profile.favorite_colors,
        "size_preferences": profile.size_preferences,
        "price_range_min": float(profile.price_range_min) if profile.price_range_min else None,
        "price_range_max": float(profile.price_range_max) if profile.price_range_max else None,
        "brand_preferences": profile.brand_preferences,
        "occasion_preferences": profile.occasion_preferences
    }





@app.get("/api/returns/{return_id}", response_model=ReturnRequestResponse)
async def get_return_request(return_id: int, db: Session = Depends(get_db)):
    """Get return request by ID"""
    return_request = db.query(ReturnRequest).filter(
        ReturnRequest.return_id == return_id
    ).first()
    if not return_request:
        raise HTTPException(status_code=404, detail="Return request not found")
    return return_request


# Agent Endpoints
@app.post("/api/agent/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Chat with the multi-agent system"""
    try:
        response = await orchestrator.process_message(
            message=request.message,
            customer_id=request.customer_id,
            context=request.context or {},
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/status")
async def get_agent_status():
    """Get agent system status"""
    from config import Config
    return {
        "status": "active",
        "agents": orchestrator.get_agent_status(),
        "llm_provider": Config.LLM_PROVIDER,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

