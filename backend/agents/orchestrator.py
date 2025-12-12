"""
Conversation Orchestrator - Routes requests to specialized agents
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from llm_provider import get_llm_provider, LLMProviderFactory

from .base_agent import BaseAgent
from .stylist_agent import StylistAgent
from .search_agent import CatalogSearchAgent
from .lookbook_agent import LookbookComposerAgent
from .checkout_agent import CheckoutAgent
from .returns_agent import ReturnsAgent
from .recommender_agent import PostPurchaseRecommenderAgent


class AgentOrchestrator:
    """Orchestrates multi-agent conversations"""
    
    def __init__(self):
        self.agents = {
            "stylist": StylistAgent(),
            "search": CatalogSearchAgent(),
            "lookbook": LookbookComposerAgent(),
            "checkout": CheckoutAgent(),
            "returns": ReturnsAgent(),
            "recommender": PostPurchaseRecommenderAgent()
        }
        self.conversation_history: Dict[int, list] = {}
    
    async def process_message(
        self,
        message: str,
        customer_id: Optional[int] = None,
        context: Dict[str, Any] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Process user message and route to appropriate agent"""
        context = context or {}
        
        # Determine which agent to use
        agent_name = await self._route_message(message, context)
        agent = self.agents[agent_name]
        
        # Get conversation history
        history = self.conversation_history.get(customer_id or 0, [])
        history.append({"role": "user", "content": message})
        
        # Process with selected agent
        try:
            response = await agent.process(message, context, db)
            
            # Update history
            history.append({"role": "assistant", "content": response.get("response", "")})
            self.conversation_history[customer_id or 0] = history[-10:]  # Keep last 10 messages
            
            return {
                "agent_name": agent_name,
                "response": response.get("response", ""),
                "actions_taken": response.get("actions_taken", []),
                "confidence": response.get("confidence", 0.8),
                "reasoning": response.get("reasoning"),
                "data": response.get("data")
            }
        except Exception as e:
            return {
                "agent_name": agent_name,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "actions_taken": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _route_message(self, message: str, context: Dict[str, Any]) -> str:
        """Route message to appropriate agent using LLM"""
        routing_prompt = f"""Analyze the following user message and determine which specialized agent should handle it.

Available agents:
- stylist: Fashion advice, style recommendations, outfit suggestions
- search: Product search, catalog queries, finding specific items
- lookbook: Creating styled collections, outfit combinations, lookbooks
- checkout: Order processing, payment, shipping questions
- returns: Return requests, refunds, exchange questions
- recommender: Product recommendations based on purchase history

User message: "{message}"
Context: {context}

Respond with ONLY the agent name (stylist, search, lookbook, checkout, returns, or recommender)."""

        llm_provider = get_llm_provider()
        default_model = LLMProviderFactory.get_default_model()
        
        response = await llm_provider.chat_completion(
            messages=[
                {"role": "system", "content": "You are a routing agent. Respond with only the agent name."},
                {"role": "user", "content": routing_prompt}
            ],
            model=default_model,
            temperature=0.3
        )
        
        agent_name = response.strip().lower()
        
        # Validate agent name
        if agent_name not in self.agents:
            # Default to search if routing fails
            return "search"
        
        return agent_name
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {name: "active" for name in self.agents.keys()}

