"""
Synthetic Data Generator for Retail Shopping Assistant
Generates realistic retail data following Oracle RDM conventions
"""

import json
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

fake = Faker()
Faker.seed(42)
random.seed(42)

# Output directories
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Product categories and attributes
CATEGORIES = {
    "Women": {
        "Dresses": ["Casual", "Formal", "Cocktail", "Maxi", "Midi", "Mini"],
        "Tops": ["Blouses", "T-Shirts", "Sweaters", "Hoodies", "Tank Tops"],
        "Bottoms": ["Jeans", "Pants", "Skirts", "Shorts", "Leggings"],
        "Outerwear": ["Jackets", "Coats", "Blazers", "Cardigans"],
        "Shoes": ["Sneakers", "Heels", "Boots", "Flats", "Sandals"],
        "Accessories": ["Bags", "Jewelry", "Belts", "Hats", "Scarves"]
    },
    "Men": {
        "Tops": ["T-Shirts", "Dress Shirts", "Polo Shirts", "Sweaters", "Hoodies"],
        "Bottoms": ["Jeans", "Chinos", "Dress Pants", "Shorts", "Sweatpants"],
        "Outerwear": ["Jackets", "Coats", "Blazers", "Vests"],
        "Shoes": ["Sneakers", "Dress Shoes", "Boots", "Loafers", "Sandals"],
        "Accessories": ["Watches", "Belts", "Wallets", "Hats", "Ties"]
    }
}

BRANDS = [
    "StyleCo", "FashionForward", "UrbanWear", "ClassicElegance", "ModernEdge",
    "TrendSetter", "LuxuryLine", "CasualComfort", "SportStyle", "DesignerLabel"
]

COLORS = [
    "Black", "White", "Navy", "Gray", "Beige", "Brown", "Red", "Blue",
    "Green", "Pink", "Purple", "Yellow", "Orange", "Teal", "Maroon", "Olive"
]

SIZES = {
    "Women": {
        "Tops": ["XS", "S", "M", "L", "XL", "XXL"],
        "Bottoms": ["0", "2", "4", "6", "8", "10", "12", "14", "16"],
        "Shoes": ["5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11"]
    },
    "Men": {
        "Tops": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
        "Bottoms": ["28", "30", "32", "34", "36", "38", "40", "42"],
        "Shoes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"]
    }
}

MATERIALS = [
    "Cotton", "Polyester", "Wool", "Silk", "Linen", "Denim", "Leather",
    "Synthetic", "Blend", "Cashmere", "Rayon", "Spandex"
]

SEASONS = ["Spring", "Summer", "Fall", "Winter", "All Season"]
YEARS = [2022, 2023, 2024]

RETURN_REASONS = [
    "Size doesn't fit", "Color not as expected", "Quality issues",
    "Changed mind", "Found better price", "Item damaged", "Wrong item received"
]


def generate_hierarchy() -> List[Dict]:
    """Generate product hierarchy"""
    hierarchy = []
    hierarchy_id = 1
    
    for gender, categories in CATEGORIES.items():
        # Gender level
        gender_id = hierarchy_id
        hierarchy.append({
            "hierarchy_id": gender_id,
            "hierarchy_level": "Gender",
            "hierarchy_name": gender,
            "parent_hierarchy_id": None,
            "hierarchy_path": gender
        })
        hierarchy_id += 1
        
        # Category level
        for category, subcategories in categories.items():
            cat_id = hierarchy_id
            hierarchy.append({
                "hierarchy_id": cat_id,
                "hierarchy_level": "Category",
                "hierarchy_name": category,
                "parent_hierarchy_id": gender_id,
                "hierarchy_path": f"{gender}/{category}"
            })
            hierarchy_id += 1
            
            # Subcategory level
            for subcat in subcategories:
                hierarchy.append({
                    "hierarchy_id": hierarchy_id,
                    "hierarchy_level": "Subcategory",
                    "hierarchy_name": subcat,
                    "parent_hierarchy_id": cat_id,
                    "hierarchy_path": f"{gender}/{category}/{subcat}"
                })
                hierarchy_id += 1
    
    return hierarchy


def generate_products(num_products: int = 1500) -> List[Dict]:
    """Generate products"""
    products = []
    hierarchy = generate_hierarchy()
    subcategory_hierarchies = [h for h in hierarchy if h["hierarchy_level"] == "Subcategory"]
    
    for i in range(num_products):
        hierarchy_item = random.choice(subcategory_hierarchies)
        gender = hierarchy_item["hierarchy_path"].split("/")[0]
        category = hierarchy_item["hierarchy_path"].split("/")[1]
        subcategory = hierarchy_item["hierarchy_path"].split("/")[2]
        
        product_name = f"{random.choice(BRANDS)} {subcategory} - {fake.word().title()}"
        
        products.append({
            "product_id": i + 1,
            "product_name": product_name,
            "product_description": fake.text(max_nb_chars=200),
            "brand_name": random.choice(BRANDS),
            "hierarchy_id": hierarchy_item["hierarchy_id"],
            "product_type": subcategory,
            "gender": gender,
            "season": random.choice(SEASONS),
            "year": random.choice(YEARS),
            "status": random.choices(["ACTIVE", "INACTIVE", "DISCONTINUED"], weights=[85, 10, 5])[0],
            "metadata": {
                "style": random.choice(["Casual", "Formal", "Sporty", "Bohemian", "Classic", "Trendy"]),
                "occasion": random.choice(["Everyday", "Work", "Party", "Wedding", "Vacation", "Gym"]),
                "fabric_care": random.choice(["Machine Wash", "Dry Clean", "Hand Wash"])
            }
        })
    
    return products


def generate_variants_and_skus(products: List[Dict]) -> tuple:
    """Generate variants and SKUs for products"""
    variants = []
    skus = []
    variant_id = 1
    sku_id = 1
    
    for product in products:
        gender = product["gender"]
        category = product["product_type"]
        
        # Determine size type
        if "Shoe" in category or "Shoes" in category:
            size_type = "Shoes"
        elif category in ["Jeans", "Pants", "Chinos", "Shorts", "Sweatpants", "Skirts", "Leggings"]:
            size_type = "Bottoms"
        else:
            size_type = "Tops"
        
        available_sizes = SIZES[gender][size_type]
        available_colors = random.sample(COLORS, random.randint(2, 6))
        
        # Generate 2-5 variants per product
        num_variants = random.randint(2, 5)
        for _ in range(num_variants):
            color = random.choice(available_colors)
            material = random.choice(MATERIALS)
            
            variant = {
                "variant_id": variant_id,
                "product_id": product["product_id"],
                "variant_name": f"{product['product_name']} - {color}",
                "color": color,
                "size": None,  # Size is at SKU level
                "material": material,
                "pattern": random.choice([None, "Solid", "Striped", "Polka Dot", "Floral", "Geometric"]),
                "variant_attributes": {
                    "wash_type": random.choice(["Regular", "Delicate", "Dry Clean"]),
                    "fit": random.choice(["Slim", "Regular", "Relaxed", "Oversized"])
                }
            }
            variants.append(variant)
            
            # Generate SKUs for each size
            base_price = Decimal(str(random.uniform(19.99, 299.99))).quantize(Decimal('0.01'))
            cost = base_price * Decimal('0.4')  # 40% cost
            
            for size in available_sizes:
                # Some sizes may be out of stock
                inventory = random.choices(
                    [0, random.randint(1, 100)],
                    weights=[10, 90]
                )[0]
                
                sku_code = f"{product['brand_name'][:3].upper()}-{product['product_id']:04d}-{sku_id:04d}-{color[:3].upper()}-{size}"
                
                skus.append({
                    "sku_id": sku_id,
                    "variant_id": variant_id,
                    "sku_code": sku_code,
                    "price": float(base_price),
                    "cost": float(cost),
                    "currency": "USD",
                    "inventory_quantity": inventory,
                    "reorder_point": 10,
                    "status": "ACTIVE" if inventory > 0 else "OUT_OF_STOCK"
                })
                sku_id += 1
            
            variant_id += 1
    
    return variants, skus


def generate_customers(num_customers: int = 15000) -> List[Dict]:
    """Generate customers"""
    customers = []
    
    for i in range(num_customers):
        gender = random.choice(["M", "F", "Other"])
        first_name = fake.first_name_male() if gender == "M" else fake.first_name_female()
        
        customers.append({
            "customer_id": i + 1,
            "email": fake.unique.email(),
            "first_name": first_name,
            "last_name": fake.last_name(),
            "phone": fake.phone_number()[:20],
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "gender": gender,
            "address_line1": fake.street_address(),
            "address_line2": random.choice([None, fake.secondary_address()]),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postal_code": fake.zipcode()[:20],
            "country": "USA"
        })
    
    return customers


def generate_reviews(products: List[Dict], customers: List[Dict], num_reviews: int = 6000) -> List[Dict]:
    """Generate product reviews"""
    reviews = []
    
    for i in range(num_reviews):
        product = random.choice(products)
        customer = random.choice(customers) if random.random() > 0.2 else None
        
        # Rating distribution: more positive reviews
        rating = random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 10, 15, 30, 40]
        )[0]
        
        review_titles = {
            5: ["Love it!", "Perfect fit", "Great quality", "Highly recommend", "Exactly as described"],
            4: ["Good product", "Nice quality", "Happy with purchase", "Would buy again"],
            3: ["Okay", "Average", "It's fine", "Could be better"],
            2: ["Not great", "Disappointed", "Poor quality", "Doesn't fit well"],
            1: ["Terrible", "Waste of money", "Poor quality", "Not as described"]
        }
        
        review_texts = {
            5: ["Excellent quality and fit. Very satisfied with my purchase.", 
                "Love this product! Great value for money.", 
                "Perfect! Exactly what I was looking for."],
            4: ["Good quality product. Happy with the purchase.", 
                "Nice item, would recommend.", 
                "Satisfied with the quality and service."],
            3: ["It's okay. Nothing special but does the job.", 
                "Average quality. Expected more for the price."],
            2: ["Not impressed. Quality could be better.", 
                "Disappointed with the product. Doesn't meet expectations."],
            1: ["Poor quality. Would not recommend.", 
                "Very disappointed. Product not as described."]
        }
        
        reviews.append({
            "review_id": i + 1,
            "product_id": product["product_id"],
            "customer_id": customer["customer_id"] if customer else None,
            "rating": rating,
            "review_title": random.choice(review_titles[rating]),
            "review_text": random.choice(review_texts[rating]),
            "verified_purchase": random.random() > 0.3,
            "helpful_count": random.randint(0, 50)
        })
    
    return reviews


def generate_orders(customers: List[Dict], skus: List[Dict], num_orders: int = 20000) -> tuple:
    """Generate orders and order line items"""
    orders = []
    line_items = []
    line_item_id = 1
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    
    for i in range(num_orders):
        customer = random.choice(customers)
        order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        order_number = f"ORD-{order_date.strftime('%Y%m%d')}-{i+1:06d}"
        
        # Generate 1-5 line items per order
        num_items = random.randint(1, 5)
        order_skus = random.sample([s for s in skus if s["inventory_quantity"] > 0], 
                                   min(num_items, len([s for s in skus if s["inventory_quantity"] > 0])))
        
        subtotal = Decimal('0')
        for sku in order_skus:
            quantity = random.randint(1, 3)
            unit_price = Decimal(str(sku["price"]))
            discount = Decimal('0') if random.random() > 0.2 else unit_price * Decimal('0.1')  # 10% discount sometimes
            line_total = (unit_price - discount) * quantity
            subtotal += line_total
            
            line_items.append({
                "line_item_id": line_item_id,
                "order_id": i + 1,
                "sku_id": sku["sku_id"],
                "quantity": quantity,
                "unit_price": float(unit_price),
                "discount_amount": float(discount),
                "line_total": float(line_total)
            })
            line_item_id += 1
        
        tax_amount = subtotal * Decimal('0.08')  # 8% tax
        shipping_amount = Decimal('0') if subtotal > 50 else Decimal('9.99')
        discount_amount = Decimal('0') if random.random() > 0.1 else subtotal * Decimal('0.05')  # 5% order discount
        total_amount = subtotal + tax_amount + shipping_amount - discount_amount
        
        order_status = random.choices(
            ["COMPLETED", "PENDING", "SHIPPED", "CANCELLED"],
            weights=[60, 10, 25, 5]
        )[0]
        
        orders.append({
            "order_id": i + 1,
            "customer_id": customer["customer_id"],
            "order_number": order_number,
            "order_date": order_date.isoformat(),
            "order_status": order_status,
            "subtotal": float(subtotal),
            "tax_amount": float(tax_amount),
            "shipping_amount": float(shipping_amount),
            "discount_amount": float(discount_amount),
            "total_amount": float(total_amount),
            "currency": "USD",
            "shipping_address": {
                "street": customer["address_line1"],
                "city": customer["city"],
                "state": customer["state"],
                "postal_code": customer["postal_code"],
                "country": customer["country"]
            },
            "billing_address": {
                "street": customer["address_line1"],
                "city": customer["city"],
                "state": customer["state"],
                "postal_code": customer["postal_code"],
                "country": customer["country"]
            },
            "payment_method": random.choice(["Credit Card", "Debit Card", "PayPal", "Apple Pay"])
        })
    
    return orders, line_items


def generate_style_profiles(customers: List[Dict]) -> List[Dict]:
    """Generate style profiles for customers"""
    profiles = []
    
    for customer in customers[:int(len(customers) * 0.7)]:  # 70% have style profiles
        profiles.append({
            "profile_id": customer["customer_id"],
            "customer_id": customer["customer_id"],
            "style_preferences": {
                "style": random.choice(["Casual", "Formal", "Sporty", "Bohemian", "Classic", "Trendy"]),
                "fit_preference": random.choice(["Slim", "Regular", "Relaxed", "Oversized"]),
                "color_preference": random.choice(["Neutral", "Bold", "Pastel", "Dark"])
            },
            "favorite_colors": random.sample(COLORS, random.randint(2, 5)),
            "size_preferences": {
                "top_size": random.choice(["XS", "S", "M", "L", "XL"]),
                "bottom_size": random.choice(["28", "30", "32", "34", "36"]),
                "shoe_size": random.choice(["7", "8", "9", "10", "11"])
            },
            "price_range_min": float(random.uniform(20, 50)),
            "price_range_max": float(random.uniform(100, 300)),
            "brand_preferences": random.sample(BRANDS, random.randint(1, 3)),
            "occasion_preferences": random.sample(["Everyday", "Work", "Party", "Wedding", "Vacation"], 
                                                 random.randint(2, 4))
        })
    
    return profiles


def main():
    """Main function to generate all data"""
    print("Generating synthetic retail data...")
    
    print("1. Generating product hierarchy...")
    hierarchy = generate_hierarchy()
    
    print("2. Generating products...")
    products = generate_products(1500)
    
    print("3. Generating variants and SKUs...")
    variants, skus = generate_variants_and_skus(products)
    print(f"   Generated {len(variants)} variants and {len(skus)} SKUs")
    
    print("4. Generating customers...")
    customers = generate_customers(15000)
    
    print("5. Generating reviews...")
    reviews = generate_reviews(products, customers, 6000)
    
    print("6. Generating orders...")
    orders, line_items = generate_orders(customers, skus, 20000)
    print(f"   Generated {len(orders)} orders with {len(line_items)} line items")
    
    print("7. Generating style profiles...")
    style_profiles = generate_style_profiles(customers)
    
    # Save to JSON
    print("\nSaving data to JSON files...")
    data_files = {
        "hierarchy.json": hierarchy,
        "products.json": products,
        "variants.json": variants,
        "skus.json": skus,
        "customers.json": customers,
        "reviews.json": reviews,
        "orders.json": orders,
        "line_items.json": line_items,
        "style_profiles.json": style_profiles
    }
    
    for filename, data in data_files.items():
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"   Saved {filename}: {len(data)} records")
    
    # Save to Parquet
    print("\nSaving data to Parquet files...")
    for filename, data in data_files.items():
        if data:
            df = pd.DataFrame(data)
            parquet_path = OUTPUT_DIR / filename.replace('.json', '.parquet')
            df.to_parquet(parquet_path, index=False)
            print(f"   Saved {parquet_path.name}")
    
    print("\n✅ Data generation complete!")
    print(f"📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

