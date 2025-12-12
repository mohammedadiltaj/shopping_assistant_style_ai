"""
Checkout Agent - Handles order processing
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from decimal import Decimal

from .base_agent import BaseAgent
from models import Order, OrderLineItem, SKU, Customer


class CheckoutAgent(BaseAgent):
    """Agent specialized in order processing and checkout"""
    
    def __init__(self):
        super().__init__(
            name="checkout",
            system_prompt="""You are a checkout specialist helping customers complete their purchases.
            You assist with order processing, payment questions, shipping options, and order confirmation.
            Always be clear about pricing, shipping costs, and delivery timelines."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process checkout-related request"""
        message_lower = message.lower()
        
        # Determine action type
        if any(word in message_lower for word in ["checkout", "buy", "purchase", "order", "cart"]):
            return await self._handle_checkout(message, context, db)
        elif any(word in message_lower for word in ["shipping", "delivery", "ship"]):
            return await self._handle_shipping_question(message, context, db)
        elif any(word in message_lower for word in ["payment", "pay", "card", "billing"]):
            return await self._handle_payment_question(message, context, db)
        elif any(word in message_lower for word in ["confirm", "confirmation", "status"]):
            return await self._handle_order_status(message, context, db)
        else:
            return await self._handle_general_checkout(message, context, db)
    
    async def _handle_checkout(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle checkout process"""
        cart_items = context.get("cart_items", [])
        customer_id = context.get("customer_id")
        
        if not cart_items:
            return {
                "response": "Your cart is empty. Add some items to your cart first!",
                "actions_taken": [{"action": "checked_cart", "empty": True}],
                "confidence": 1.0,
                "data": {"cart_empty": True}
            }
        
        # Calculate totals
        # Calculate totals
        subtotal = sum(Decimal(str(item.get("price", 0))) * item.get("quantity", 1) for item in cart_items)
        shipping = Decimal('10.0') if subtotal < 50 else Decimal('0.0')
        tax = subtotal * Decimal('0.08')
        total = subtotal + shipping + tax
        
        # Check for confirmation
        is_confirmation = any(word in message.lower() for word in ["confirm", "yes", "proceed", "place order"])
        
        if is_confirmation:
            if not customer_id:
                return {
                     "response": "Please look into logging in to complete the purchase.",
                     "actions_taken": [{"action": "checkout_login_required"}],
                     "confidence": 1.0
                }

            # Create Order
            import uuid
            from models import Order, OrderLineItem
            
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            db_order = Order(
                customer_id=customer_id,
                order_number=order_number,
                subtotal=subtotal,
                tax_amount=tax,
                shipping_amount=shipping,
                total_amount=total,
                order_status="CONFIRMED",
                payment_method="Credit Card" # Default for agent
            )
            db.add(db_order)
            db.commit()
            db.refresh(db_order)
            
            for item in cart_items:
                line_item = OrderLineItem(
                    order_id=db_order.order_id,
                    sku_id=item.get("product_id"), # Using product_id as sku_id for now
                    quantity=item.get("quantity", 1),
                    unit_price=item.get("price", 0),
                    line_total=item.get("price", 0) * item.get("quantity", 1)
                )
                db.add(line_item)
            db.commit()
            
            return {
                "response": f"Order placed successfully! Your order number is {order_number}. You can view it in your Orders page.",
                "actions_taken": [{"action": "created_order", "order_id": db_order.order_id}],
                "confidence": 1.0,
                "data": {"order_placed": True, "clear_cart": True}
            }
        
        response = f"""I can help you checkout! Here's your order summary:

Subtotal: ${subtotal:.2f}
Shipping: ${shipping:.2f}
Tax: ${tax:.2f}
Total: ${total:.2f}

You have {len(cart_items)} item(s) in your cart. Ready to place the order?"""
        
        return {
            "response": response,
            "actions_taken": [
                {"action": "calculated_totals"},
                {"action": "prepared_checkout_summary"}
            ],
            "confidence": 0.95,
            "data": {
                "subtotal": float(subtotal),
                "total": float(total),
                "awaiting_confirmation": True
            }
        }
    
    async def _handle_shipping_question(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle shipping questions"""
        response = """We offer the following shipping options:

• Standard Shipping (5-7 business days): $9.99 (FREE on orders over $50)
• Express Shipping (2-3 business days): $19.99
• Overnight Shipping (next business day): $29.99

All orders are processed within 1-2 business days. You'll receive a tracking number once your order ships."""
        
        return {
            "response": response,
            "actions_taken": [{"action": "provided_shipping_info"}],
            "confidence": 1.0
        }
    
    async def _handle_payment_question(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle payment questions"""
        response = """We accept the following payment methods:

• Credit/Debit Cards (Visa, Mastercard, American Express, Discover)
• PayPal
• Apple Pay
• Google Pay

All payments are processed securely. We never store your full payment information."""
        
        return {
            "response": response,
            "actions_taken": [{"action": "provided_payment_info"}],
            "confidence": 1.0
        }
    
    async def _handle_order_status(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle order status inquiries"""
        order_id = context.get("order_id")
        customer_id = context.get("customer_id")
        
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                response = f"""Order Status: {order.order_status}

Order Number: {order.order_number}
Order Date: {order.order_date.strftime('%B %d, %Y')}
Total: ${order.total_amount:.2f}

Your order is currently {order.order_status.lower()}."""
            else:
                response = "I couldn't find that order. Please check your order number."
        elif customer_id:
            orders = db.query(Order).filter(
                Order.customer_id == customer_id
            ).order_by(Order.order_date.desc()).limit(5).all()
            
            if orders:
                response = f"You have {len(orders)} recent order(s). Your latest order is {orders[0].order_status.lower()}."
            else:
                response = "You don't have any orders yet."
        else:
            response = "Please provide your order number or sign in to check your order status."
        
        return {
            "response": response,
            "actions_taken": [{"action": "checked_order_status"}],
            "confidence": 0.9
        }
    
    async def _handle_general_checkout(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle general checkout questions"""
        response = await self.call_llm([{
            "role": "user",
            "content": f"User question about checkout: {message}. Provide helpful, concise answer."
        }])
        
        return {
            "response": response,
            "actions_taken": [{"action": "answered_general_checkout_question"}],
            "confidence": 0.8
        }

