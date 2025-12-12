"""
Post-Purchase Recommender Agent - Suggests related products
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .base_agent import BaseAgent
from models import Product, Order, OrderLineItem, SKU, ProductVariant, Review, Customer


class PostPurchaseRecommenderAgent(BaseAgent):
    """Agent specialized in product recommendations"""
    
    def __init__(self):
        super().__init__(
            name="recommender",
            system_prompt="""You are a product recommendation specialist. You analyze customer 
            purchase history, preferences, and browsing behavior to suggest relevant products 
            they'll love. Focus on complementary items, similar styles, and personalized 
            recommendations based on their taste."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process recommendation request"""
        customer_id = context.get("customer_id")
        product_id = context.get("product_id")
        
        if product_id:
            # Product-based recommendations
            recommendations = self._get_product_recommendations(db, product_id)
        elif customer_id:
            # Customer-based recommendations
            recommendations = self._get_customer_recommendations(db, customer_id)
        else:
            # General recommendations
            recommendations = self._get_trending_recommendations(db)
        
        # Generate natural language response
        response = self._format_recommendations(recommendations, message)
        
        return {
            "response": response,
            "actions_taken": [
                {"action": "generated_recommendations", "count": len(recommendations)},
                {"action": "analyzed_preferences"} if customer_id else {}
            ],
            "confidence": 0.85,
            "reasoning": f"Generated {len(recommendations)} personalized recommendations",
            "data": {
                "recommendations": recommendations,
                "type": "product" if product_id else "customer" if customer_id else "trending"
            }
        }
    
    def _get_product_recommendations(self, db: Session, product_id: int, limit: int = 5) -> List[Dict]:
        """Get recommendations based on a specific product"""
        # Get the product
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return []
        
        # Find similar products (same category, brand, or style)
        query = db.query(Product).filter(
            Product.product_id != product_id,
            Product.status == "ACTIVE"
        )
        
        # Same category/brand
        similar = query.filter(
            (Product.hierarchy_id == product.hierarchy_id) |
            (Product.brand_name == product.brand_name)
        ).limit(limit).all()
        
        # If not enough, add by gender
        if len(similar) < limit:
            additional = query.filter(
                Product.gender == product.gender
            ).limit(limit - len(similar)).all()
            similar.extend(additional)
        
        return self._format_product_list(similar, db)
    
    def _get_customer_recommendations(self, db: Session, customer_id: int, limit: int = 10) -> List[Dict]:
        """Get recommendations based on customer purchase history"""
        # Get customer's past orders
        orders = db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.order_status == "COMPLETED"
        ).order_by(desc(Order.order_date)).limit(10).all()
        
        if not orders:
            return self._get_trending_recommendations(db, limit)
        
        # Get products from orders
        product_ids = set()
        for order in orders:
            line_items = db.query(OrderLineItem).filter(
                OrderLineItem.order_id == order.order_id
            ).all()
            
            for item in line_items:
                sku = db.query(SKU).filter(SKU.sku_id == item.sku_id).first()
                if sku:
                    variant = db.query(ProductVariant).filter(
                        ProductVariant.variant_id == sku.variant_id
                    ).first()
                    if variant:
                        product_ids.add(variant.product_id)
        
        # Get similar products
        if product_ids:
            # Get categories/brands from purchased products
            purchased_products = db.query(Product).filter(
                Product.product_id.in_(list(product_ids))
            ).all()
            
            categories = [p.hierarchy_id for p in purchased_products]
            brands = [p.brand_name for p in purchased_products]
            
            # Recommend similar items
            recommendations = db.query(Product).filter(
                Product.product_id.notin_(list(product_ids)),
                Product.status == "ACTIVE",
                (
                    (Product.hierarchy_id.in_(categories)) |
                    (Product.brand_name.in_(brands))
                )
            ).limit(limit).all()
            return self._format_product_list(recommendations, db)
        else:
            return self._get_trending_recommendations(db, limit)
    
    def _get_trending_recommendations(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get trending/popular products"""
        # Products with most orders
        trending = db.query(
            Product,
            func.count(OrderLineItem.line_item_id).label('order_count')
        ).join(
            ProductVariant
        ).join(
            SKU
        ).join(
            OrderLineItem
        ).filter(
            Product.status == "ACTIVE"
        ).group_by(
            Product.product_id
        ).order_by(
            desc('order_count')
        ).limit(limit).all()
        
        products = [p[0] for p in trending]
        return self._format_product_list(products, db)
    
    def _format_product_list(self, products: List, db: Session = None) -> List[Dict]:
        """Format products for response"""
        results = []
        for product in products:
            # Get price range (need db session)
            lowest_price = None
            avg_rating = None
            if db:
                lowest_price = db.query(func.min(SKU.price)).join(
                    ProductVariant
                ).filter(
                    ProductVariant.product_id == product.product_id,
                    SKU.status == "ACTIVE"
                ).scalar()
                
                avg_rating = db.query(func.avg(Review.rating)).filter(
                    Review.product_id == product.product_id
                ).scalar()
            
            results.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "brand_name": product.brand_name,
                "product_type": product.product_type,
                "price_from": float(lowest_price) if lowest_price else None,
                "rating": round(float(avg_rating), 1) if avg_rating else None
            })
        
        return results
    
    def _format_recommendations(self, recommendations: List[Dict], query: str) -> str:
        """Format recommendations as natural language"""
        if not recommendations:
            return "I couldn't find any recommendations at the moment. Try browsing our catalog!"
        
        response = f"Here are {len(recommendations)} recommendations for you:\n\n"
        
        for i, rec in enumerate(recommendations[:5], 1):
            price_str = f"from ${rec['price_from']:.2f}" if rec['price_from'] else "Price varies"
            rating_str = f"⭐ {rec['rating']}" if rec['rating'] else ""
            response += f"{i}. {rec['product_name']} by {rec['brand_name']} - {price_str} {rating_str}\n"
        
        if len(recommendations) > 5:
            response += f"\n... and {len(recommendations) - 5} more recommendations!"
        
        return response

