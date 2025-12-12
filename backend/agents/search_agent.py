"""
Catalog Search Agent - Product search and filtering
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from .base_agent import BaseAgent
from models import Product, SKU, ProductVariant, ProductHierarchy


class CatalogSearchAgent(BaseAgent):
    """Agent specialized in product search and catalog queries"""
    
    def __init__(self):
        super().__init__(
            name="search",
            system_prompt="""You are a product search specialist. You help customers find exactly 
            what they're looking for by understanding their search queries, applying relevant filters, 
            and presenting results in a clear, organized manner. Always provide specific product 
            details and help narrow down options when there are many results."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process search request"""
        # Extract search parameters from message
        search_params = self._parse_search_query(message)
        
        # Build database query
        query = db.query(Product).filter(Product.status == "ACTIVE")
        
        # Apply filters
        if search_params.get("keywords"):
            keywords = search_params["keywords"]
            query = query.filter(
                or_(
                    Product.product_name.ilike(f"%{keywords}%"),
                    Product.product_description.ilike(f"%{keywords}%"),
                    Product.brand_name.ilike(f"%{keywords}%")
                )
            )
        
        if search_params.get("category"):
            query = query.join(ProductHierarchy).filter(
                ProductHierarchy.hierarchy_name.ilike(f"%{search_params['category']}%")
            )
        
        if search_params.get("gender"):
            query = query.filter(Product.gender == search_params["gender"])
        
        if search_params.get("brand"):
            query = query.filter(Product.brand_name.ilike(f"%{search_params['brand']}%"))
        
        if search_params.get("price_min"):
            query = query.join(ProductVariant).join(SKU).filter(
                SKU.price >= search_params["price_min"]
            )
        
        if search_params.get("price_max"):
            query = query.join(ProductVariant).join(SKU).filter(
                SKU.price <= search_params["price_max"]
            )
        
        # Execute query
        products = query.distinct().limit(20).all()
        
        # Format results
        results = []
        for product in products:
            # Get lowest price SKU
            lowest_price = db.query(func.min(SKU.price)).join(ProductVariant).filter(
                ProductVariant.product_id == product.product_id,
                SKU.status == "ACTIVE"
            ).scalar()
            
            results.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "brand_name": product.brand_name,
                "product_type": product.product_type,
                "price_from": float(lowest_price) if lowest_price else None,
                "description": product.product_description[:100] + "..." if product.product_description else None
            })
        
        # Generate natural language response
        response_text = self._format_search_results(message, results, search_params)
        
        return {
            "response": response_text,
            "actions_taken": [
                {"action": "parsed_search_query", "params": search_params},
                {"action": "executed_database_search"},
                {"action": "formatted_results", "count": len(results)}
            ],
            "confidence": 0.9,
            "reasoning": f"Found {len(results)} products matching search criteria",
            "data": {
                "products": results,
                "search_params": search_params,
                "total_results": len(results)
            }
        }
    
    def _parse_search_query(self, message: str) -> Dict[str, Any]:
        """Parse search query to extract parameters"""
        message_lower = message.lower()
        params = {}
        
        # Extract keywords (remove common words)
        stop_words = {"find", "show", "me", "looking", "for", "want", "need", "search", "get", "i", "am", "a", "an", "the", "please", "can", "you", "help"}
        words = [w for w in message.split() if w.lower() not in stop_words]
        
        # Filter out category names from keywords if they exist in message to avoid redundancy
        # But for now just better stop words should help.
        
        if words:
            params["keywords"] = " ".join(words[:5])  # Limit to 5 keywords
        
        # Extract gender
        if any(word in message_lower for word in ["women", "womens", "female", "ladies"]):
            params["gender"] = "Women"
        elif any(word in message_lower for word in ["men", "mens", "male", "guys"]):
            params["gender"] = "Men"
        
        # Extract price range
        if "under" in message_lower or "less than" in message_lower:
            # Try to extract number
            import re
            numbers = re.findall(r'\$?(\d+)', message)
            if numbers:
                params["price_max"] = float(numbers[0])
        
        # Extract category hints
        categories = ["dress", "shirt", "pants", "shoes", "jacket", "accessories"]
        for cat in categories:
            if cat in message_lower:
                params["category"] = cat.title()
                break
        
        return params
    
    def _format_search_results(self, query: str, results: List[Dict], params: Dict) -> str:
        """Format search results as natural language"""
        if not results:
            return f"I couldn't find any products matching '{query}'. Try adjusting your search terms or filters."
        
        response = f"I found {len(results)} products matching your search:\n\n"
        
        for i, product in enumerate(results[:5], 1):  # Show top 5
            price_str = f"from ${product['price_from']:.2f}" if product['price_from'] else "Price varies"
            response += f"{i}. {product['product_name']} by {product['brand_name']} - {price_str}\n"
        
        if len(results) > 5:
            response += f"\n... and {len(results) - 5} more products. Would you like to see more results or refine your search?"
        
        return response

