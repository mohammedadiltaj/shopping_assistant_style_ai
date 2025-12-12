"""
Stylist Agent - Provides fashion/style recommendations
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from .base_agent import BaseAgent
from models import Product, StyleProfile, Customer, ProductHierarchy


class StylistAgent(BaseAgent):
    """Agent specialized in fashion styling and recommendations"""
    
    def __init__(self):
        super().__init__(
            name="stylist",
            system_prompt="""You are a professional fashion stylist with expertise in personal styling, 
            trend analysis, and outfit coordination. You provide personalized fashion advice based on 
            customer preferences, body type, occasion, and style goals. Always be helpful, encouraging, 
            and provide specific product recommendations when relevant."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process styling request"""
        customer_id = context.get("customer_id")
        style_profile = None
        
        # Get customer style profile if available
        if customer_id:
            style_profile = db.query(StyleProfile).filter(
                StyleProfile.customer_id == customer_id
            ).first()
        
        # Build context for LLM
        style_context = ""
        if style_profile:
            style_context = f"""
Customer Style Profile:
- Favorite Colors: {', '.join(style_profile.favorite_colors or [])}
- Style Preferences: {style_profile.style_preferences}
- Price Range: ${style_profile.price_range_min} - ${style_profile.price_range_max}
- Brand Preferences: {', '.join(style_profile.brand_preferences or [])}
- Occasion Preferences: {', '.join(style_profile.occasion_preferences or [])}
"""
        
        # Get relevant products for context
        products = self._get_styling_products(db, style_profile)
        
        prompt = f"""User request: {message}

{style_context}

Based on this request, provide:
1. Personalized styling advice
2. Specific product recommendations (if applicable)
3. Outfit suggestions
4. Tips for the occasion/style mentioned

Available products context: {len(products)} products available in catalog."""
        
        response_text = await self.call_llm([{"role": "user", "content": prompt}])
        
        # Extract product recommendations if any
        recommended_products = self._extract_product_recommendations(response_text, products)
        
        return {
            "response": response_text,
            "actions_taken": [
                {"action": "analyzed_style_request", "details": message},
                {"action": "retrieved_style_profile", "customer_id": customer_id} if customer_id else {},
                {"action": "generated_styling_advice"},
                {"action": "recommended_products", "count": len(recommended_products)}
            ],
            "confidence": 0.85,
            "reasoning": "Analyzed user request with style profile context",
            "data": {
                "recommended_products": recommended_products[:5],  # Top 5
                "style_profile_used": style_profile is not None
            }
        }
    
    def _get_styling_products(self, db: Session, style_profile: Any = None) -> List[Dict]:
        """Get products relevant for styling"""
        query = db.query(Product).filter(Product.status == "ACTIVE")
        
        if style_profile and style_profile.brand_preferences:
            query = query.filter(Product.brand_name.in_(style_profile.brand_preferences))
        
        products = query.limit(50).all()
        
        return [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "brand_name": p.brand_name,
                "product_type": p.product_type,
                "gender": p.gender
            }
            for p in products
        ]
    
    def _extract_product_recommendations(self, response: str, products: List[Dict]) -> List[Dict]:
        """Extract product recommendations from LLM response"""
        # Simple keyword matching - in production, use more sophisticated extraction
        recommended = []
        response_lower = response.lower()
        
        for product in products:
            if any(keyword in response_lower for keyword in [
                product["product_name"].lower(),
                product["brand_name"].lower(),
                product["product_type"].lower()
            ]):
                recommended.append(product)
        
        return recommended[:5]

