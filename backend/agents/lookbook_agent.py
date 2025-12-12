"""
Lookbook Composer Agent - Creates styled product collections
"""

from typing import Dict, Any, List
import random
from sqlalchemy.orm import Session
from sqlalchemy import func

from .base_agent import BaseAgent
from models import Product, ProductVariant, SKU, StyleProfile


class LookbookComposerAgent(BaseAgent):
    """Agent specialized in creating styled lookbooks and outfit combinations"""
    
    def __init__(self):
        super().__init__(
            name="lookbook",
            system_prompt="""You are a creative fashion director specializing in creating 
            cohesive lookbooks and styled outfits. You combine products in aesthetically 
            pleasing ways, considering color harmony, style consistency, and occasion 
            appropriateness. Create inspiring collections that tell a fashion story."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process lookbook creation request"""
        # Extract lookbook parameters
        params = self._parse_lookbook_request(message)
        
        # Get products for lookbook
        products = self._get_lookbook_products(db, params)
        
        # Create styled combinations
        lookbook_items = self._create_combinations(products, params)
        
        # Generate description
        description = await self._generate_lookbook_description(lookbook_items, params)
        
        return {
            "response": description,
            "actions_taken": [
                {"action": "parsed_lookbook_request", "params": params},
                {"action": "selected_products", "count": len(products)},
                {"action": "created_combinations", "count": len(lookbook_items)},
                {"action": "generated_description"}
            ],
            "confidence": 0.85,
            "reasoning": f"Created lookbook with {len(lookbook_items)} styled combinations",
            "data": {
                "lookbook": {
                    "title": params.get("title", "Styled Collection"),
                    "theme": params.get("theme"),
                    "items": lookbook_items,
                    "total_products": len(products)
                }
            }
        }
    
    def _parse_lookbook_request(self, message: str) -> Dict[str, Any]:
        """Parse lookbook creation request"""
        message_lower = message.lower()
        params = {}
        
        # Extract theme/occasion
        themes = {
            "casual": ["casual", "everyday", "relaxed"],
            "formal": ["formal", "business", "professional", "office"],
            "party": ["party", "night", "evening", "celebration"],
            "vacation": ["vacation", "travel", "resort", "beach"],
            "wedding": ["wedding", "bridal", "ceremony"]
        }
        
        for theme, keywords in themes.items():
            if any(kw in message_lower for kw in keywords):
                params["theme"] = theme
                break
        
        # Extract color preferences
        colors = ["black", "white", "navy", "beige", "red", "blue", "green", "pink"]
        for color in colors:
            if color in message_lower:
                params["color"] = color
                break
        
        # Extract number of items
        import re
        numbers = re.findall(r'(\d+)\s*(?:items?|pieces?|outfits?)', message_lower)
        if numbers:
            params["item_count"] = int(numbers[0])
        else:
            params["item_count"] = 5  # Default
        
        return params
    
    def _get_lookbook_products(self, db: Session, params: Dict[str, Any]) -> List[Dict]:
        """Get products suitable for lookbook"""
        query = db.query(Product).filter(Product.status == "ACTIVE")
        
        if params.get("theme"):
            # Filter by metadata or product type based on theme
            theme_filters = {
                "casual": ["T-Shirts", "Jeans", "Sneakers"],
                "formal": ["Dress Shirts", "Dress Pants", "Dress Shoes"],
                "party": ["Dresses", "Heels", "Accessories"],
                "vacation": ["Shorts", "Sandals", "Swimwear"],
                "wedding": ["Dresses", "Formal", "Accessories"]
            }
            if params["theme"] in theme_filters:
                query = query.filter(Product.product_type.in_(theme_filters[params["theme"]]))
        
        products = query.limit(50).all()
        
        return [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "brand_name": p.brand_name,
                "product_type": p.product_type,
                "gender": p.gender,
                "metadata": p.product_metadata
            }
            for p in products
        ]
    
    def _create_combinations(self, products: List[Dict], params: Dict[str, Any]) -> List[Dict]:
        """Create styled product combinations"""
        combinations = []
        item_count = params.get("item_count", 5)
        
        # Group products by type
        by_type = {}
        for product in products:
            ptype = product["product_type"]
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(product)
        
        # Create combinations (top + bottom + shoes + accessories)
        for i in range(min(item_count, 10)):
            combination = {
                "outfit_id": i + 1,
                "products": [],
                "description": ""
            }
            
            # Select one product from each category
            categories = ["Tops", "Bottoms", "Shoes", "Accessories"]
            for category in categories:
                matching = [p for p in products if category.lower() in p["product_type"].lower()]
                if matching:
                    combination["products"].append(random.choice(matching))
            
            if combination["products"]:
                combinations.append(combination)
        

        return combinations
    
    async def _generate_lookbook_description(self, items: List[Dict], params: Dict) -> str:
        """Generate natural language description of lookbook"""
        theme = params.get("theme", "styled")
        count = len(items)
        
        prompt = f"""Create a compelling description for a {theme} lookbook with {count} styled outfits.
        Make it inspiring and fashion-forward. Keep it to 2-3 sentences."""
        
        description = await self.call_llm([{"role": "user", "content": prompt}])
        
        return description or f"I've created a {theme} lookbook with {count} beautifully styled combinations for you!"

