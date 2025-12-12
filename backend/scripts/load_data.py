"""
Load synthetic data into PostgreSQL database
"""

import json
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Base, ProductHierarchy, Product, ProductVariant, SKU,
    Customer, StyleProfile, Review, Order, OrderLineItem, ReturnRequest
)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_json(filepath: Path):
    """Load JSON data file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def load_hierarchy(db: Session):
    """Load product hierarchy"""
    print("Loading product hierarchy...")
    filepath = DATA_DIR / "hierarchy.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping hierarchy.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if hierarchy already exists
        existing = db.query(ProductHierarchy).filter(ProductHierarchy.hierarchy_id == item['hierarchy_id']).first()
        if existing:
            skipped += 1
            continue
        
        try:
            hierarchy = ProductHierarchy(**item)
            db.add(hierarchy)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading hierarchy {item.get('hierarchy_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} hierarchy items, skipped {skipped} duplicates")


def load_products(db: Session):
    """Load products"""
    print("Loading products...")
    filepath = DATA_DIR / "products.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping products.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if product already exists
        existing = db.query(Product).filter(Product.product_id == item['product_id']).first()
        if existing:
            skipped += 1
            continue
        
        # Map 'metadata' from JSON to 'product_metadata' for SQLAlchemy model
        if 'metadata' in item:
            item['product_metadata'] = item.pop('metadata')
        
        try:
            product = Product(**item)
            db.add(product)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading product {item.get('product_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} products, skipped {skipped} duplicates")


def load_variants(db: Session):
    """Load product variants"""
    print("Loading product variants...")
    filepath = DATA_DIR / "variants.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping variants.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if variant already exists
        existing = db.query(ProductVariant).filter(ProductVariant.variant_id == item['variant_id']).first()
        if existing:
            skipped += 1
            continue
        
        try:
            variant = ProductVariant(**item)
            db.add(variant)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading variant {item.get('variant_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} variants, skipped {skipped} duplicates")


def load_skus(db: Session):
    """Load SKUs"""
    print("Loading SKUs...")
    filepath = DATA_DIR / "skus.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping SKUs.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if SKU already exists
        existing = db.query(SKU).filter(SKU.sku_code == item['sku_code']).first()
        if existing:
            skipped += 1
            continue
        
        # Convert price/cost to Decimal
        item['price'] = Decimal(str(item['price']))
        if item.get('cost'):
            item['cost'] = Decimal(str(item['cost']))
        
        try:
            sku = SKU(**item)
            db.add(sku)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading SKU {item.get('sku_code')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} SKUs, skipped {skipped} duplicates")


def load_customers(db: Session):
    """Load customers"""
    print("Loading customers...")
    filepath = DATA_DIR / "customers.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping customers.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if customer already exists
        existing = db.query(Customer).filter(Customer.customer_id == item['customer_id']).first()
        if existing:
            skipped += 1
            continue
        
        if item.get('date_of_birth'):
            item['date_of_birth'] = datetime.fromisoformat(item['date_of_birth']).date()
        
        try:
            customer = Customer(**item)
            db.add(customer)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading customer {item.get('customer_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} customers, skipped {skipped} duplicates")


def load_style_profiles(db: Session):
    """Load style profiles"""
    print("Loading style profiles...")
    filepath = DATA_DIR / "style_profiles.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping style profiles.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if style profile already exists
        existing = db.query(StyleProfile).filter(StyleProfile.profile_id == item['profile_id']).first()
        if existing:
            skipped += 1
            continue
        
        if item.get('price_range_min'):
            item['price_range_min'] = Decimal(str(item['price_range_min']))
        if item.get('price_range_max'):
            item['price_range_max'] = Decimal(str(item['price_range_max']))
        
        try:
            profile = StyleProfile(**item)
            db.add(profile)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading style profile {item.get('profile_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} style profiles, skipped {skipped} duplicates")


def load_reviews(db: Session):
    """Load reviews"""
    print("Loading reviews...")
    filepath = DATA_DIR / "reviews.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping reviews.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if review already exists
        existing = db.query(Review).filter(Review.review_id == item['review_id']).first()
        if existing:
            skipped += 1
            continue
        
        try:
            review = Review(**item)
            db.add(review)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading review {item.get('review_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} reviews, skipped {skipped} duplicates")


def load_orders(db: Session):
    """Load orders"""
    print("Loading orders...")
    filepath = DATA_DIR / "orders.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping orders.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if order already exists
        existing = db.query(Order).filter(Order.order_id == item['order_id']).first()
        if existing:
            skipped += 1
            continue
        
        if isinstance(item.get('order_date'), str):
            item['order_date'] = datetime.fromisoformat(item['order_date'])
        item['subtotal'] = Decimal(str(item['subtotal']))
        item['tax_amount'] = Decimal(str(item['tax_amount']))
        item['shipping_amount'] = Decimal(str(item['shipping_amount']))
        item['discount_amount'] = Decimal(str(item['discount_amount']))
        item['total_amount'] = Decimal(str(item['total_amount']))
        
        try:
            order = Order(**item)
            db.add(order)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading order {item.get('order_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} orders, skipped {skipped} duplicates")


def load_line_items(db: Session):
    """Load order line items"""
    print("Loading order line items...")
    filepath = DATA_DIR / "line_items.json"
    if not filepath.exists():
        print(f"⚠️  {filepath} not found. Skipping line items.")
        return
    
    data = load_json(filepath)
    loaded = 0
    skipped = 0
    
    for item in data:
        # Check if line item already exists
        existing = db.query(OrderLineItem).filter(OrderLineItem.line_item_id == item['line_item_id']).first()
        if existing:
            skipped += 1
            continue
        
        item['unit_price'] = Decimal(str(item['unit_price']))
        item['discount_amount'] = Decimal(str(item['discount_amount']))
        item['line_total'] = Decimal(str(item['line_total']))
        
        try:
            line_item = OrderLineItem(**item)
            db.add(line_item)
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error loading line item {item.get('line_item_id')}: {e}")
            skipped += 1
            continue
    
    db.commit()
    print(f"✅ Loaded {loaded} line items, skipped {skipped} duplicates")


def main():
    """Main function to load all data"""
    print("=" * 50)
    print("Loading Synthetic Data into Database")
    print("=" * 50)
    
    # Create tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Load data in order (respecting foreign keys)
        load_hierarchy(db)
        load_products(db)
        load_variants(db)
        load_skus(db)
        load_customers(db)
        load_style_profiles(db)
        load_reviews(db)
        load_orders(db)
        load_line_items(db)
        
        print("\n" + "=" * 50)
        print("✅ Data loading complete!")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

