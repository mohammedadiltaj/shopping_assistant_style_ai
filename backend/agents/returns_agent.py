"""
Returns Agent - Manages return requests
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from models import ReturnRequest, Order, OrderLineItem, Customer


class ReturnsAgent(BaseAgent):
    """Agent specialized in handling returns and exchanges"""
    
    def __init__(self):
        super().__init__(
            name="returns",
            system_prompt="""You are a returns specialist helping customers with returns, exchanges, 
            and refunds. You process return requests, explain return policies, and help resolve 
            issues. Always be empathetic and solution-oriented."""
        )
    
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process return request"""
        message_lower = message.lower()
        customer_id = context.get("customer_id")
        order_id = context.get("order_id")
        
        # Check if user wants to initiate return
        if any(word in message_lower for word in ["return", "refund", "exchange", "send back"]):
            return await self._initiate_return(message, context, db)
        elif any(word in message_lower for word in ["policy", "return policy", "how long"]):
            return await self._explain_return_policy(message, context, db)
        elif any(word in message_lower for word in ["status", "track", "where is"]):
            return await self._check_return_status(message, context, db)
        else:
            return await self._handle_general_return_question(message, context, db)
    
    async def _initiate_return(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Initiate a return request"""
        order_id = context.get("order_id")
        customer_id = context.get("customer_id")
        
        if not order_id and not customer_id:
            return {
                "response": "To process a return, I'll need your order number. Please provide it or sign in to your account.",
                "actions_taken": [{"action": "requested_order_info"}],
                "confidence": 0.9
            }
        
        # Get order
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
        elif customer_id:
            # Get most recent order
            order = db.query(Order).filter(
                Order.customer_id == customer_id
            ).order_by(Order.order_date.desc()).first()
        else:
            order = None
        
        if not order:
            return {
                "response": "I couldn't find your order. Please check your order number.",
                "actions_taken": [{"action": "order_not_found"}],
                "confidence": 0.9
            }
        
        # Check if order is eligible for return (within 30 days)
        days_since_order = (datetime.now() - order.order_date).days
        if days_since_order > 30:
            return {
                "response": f"Your order is {days_since_order} days old. Our return policy allows returns within 30 days of purchase. Unfortunately, this order is no longer eligible for return.",
                "actions_taken": [{"action": "checked_return_eligibility", "eligible": False}],
                "confidence": 1.0
            }
        
        # Extract return reason
        reasons = [
            "Size doesn't fit", "Color not as expected", "Quality issues",
            "Changed mind", "Found better price", "Item damaged", "Wrong item received"
        ]
        
        reason = None
        for r in reasons:
            if r.lower() in message_lower:
                reason = r
                break
        
        if not reason:
            reason = "Changed mind"  # Default
            
        # Check for confirmation
        is_confirmation = any(word in message_lower for word in ["confirm", "yes", "proceed", "do it"])
        
        if is_confirmation:
            from models import ReturnRequest
            
            # Create Return Request
            db_return = ReturnRequest(
                order_id=order.order_id,
                return_reason=reason,
                return_status="PENDING",
                notes=f"Created by agent. Reason: {reason}"
            )
            db.add(db_return)
            db.commit()
            db.refresh(db_return)
            
            return {
                "response": f"I've submitted your return request for order {order.order_number}. Your return ID is {db_return.return_id}. You'll receive a confirmation email shortly.",
                "actions_taken": [{"action": "created_return_request", "return_id": db_return.return_id}],
                "confidence": 1.0,
                "data": {"return_created": True}
            }
        
        response = f"""I can help you process a return for order {order.order_number}.

Return Reason: {reason}
Order Date: {order.order_date.strftime('%B %d, %Y')}
Eligible for Return: Yes (within 30-day window)

Would you like me to process this return? You'll receive a refund to your original payment method within 5-7 business days after we receive the item."""
        
        return {
            "response": response,
            "actions_taken": [
                {"action": "initiated_return_request"},
                {"action": "checked_eligibility", "eligible": True, "days_since_order": days_since_order}
            ],
            "confidence": 0.9,
            "data": {
                "order_id": order.order_id,
                "order_number": order.order_number,
                "return_reason": reason,
                "eligible": True,
                "awaiting_confirmation": True
            }
        }
    
    async def _explain_return_policy(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Explain return policy"""
        response = """Our Return Policy:

• Returns accepted within 30 days of purchase
• Items must be unworn, unwashed, and in original condition with tags attached
• Free return shipping for orders over $50
• Refunds processed within 5-7 business days after we receive the item
• Original shipping costs are non-refundable
• Sale items are final sale (no returns)

To start a return, just let me know your order number or sign in to your account."""
        
        return {
            "response": response,
            "actions_taken": [{"action": "explained_return_policy"}],
            "confidence": 1.0
        }
    
    async def _check_return_status(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Check return request status"""
        return_id = context.get("return_id")
        customer_id = context.get("customer_id")
        
        if return_id:
            return_request = db.query(ReturnRequest).filter(
                ReturnRequest.return_id == return_id
            ).first()
            
            if return_request:
                response = f"""Return Status: {return_request.return_status}

Return ID: {return_request.return_id}
Requested Date: {return_request.requested_date.strftime('%B %d, %Y')}
Refund Amount: ${return_request.refund_amount:.2f}

Your return is currently {return_request.return_status.lower()}."""
            else:
                response = "I couldn't find that return request. Please check your return ID."
        elif customer_id:
            returns = db.query(ReturnRequest).join(Order).filter(
                Order.customer_id == customer_id
            ).order_by(ReturnRequest.requested_date.desc()).limit(5).all()
            
            if returns:
                response = f"You have {len(returns)} return request(s). Your latest return is {returns[0].return_status.lower()}."
            else:
                response = "You don't have any return requests."
        else:
            response = "Please provide your return ID or sign in to check your return status."
        
        return {
            "response": response,
            "actions_taken": [{"action": "checked_return_status"}],
            "confidence": 0.9
        }
    
    async def _handle_general_return_question(self, message: str, context: Dict, db: Session) -> Dict[str, Any]:
        """Handle general return questions"""
        response = await self.call_llm([{
            "role": "user",
            "content": f"User question about returns: {message}. Provide helpful, concise answer about our return policy."
        }])
        
        return {
            "response": response,
            "actions_taken": [{"action": "answered_general_return_question"}],
            "confidence": 0.8
        }

