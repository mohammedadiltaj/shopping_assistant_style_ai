"""
Base Agent class with common functionality
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from llm_provider import get_llm_provider, LLMProviderFactory


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm_provider = get_llm_provider()
        self.default_model = LLMProviderFactory.get_default_model()
    
    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process a message and return response"""
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for this agent"""
        return []
    
    async def call_llm(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """Call LLM provider (OpenAI or Groq)"""
        system_message = {"role": "system", "content": self.system_prompt}
        all_messages = [system_message] + messages
        
        response = await self.llm_provider.chat_completion(
            messages=all_messages,
            model=model or self.default_model,
            tools=tools,
            temperature=temperature
        )
        
        return response
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate agent response"""
        required_fields = ["response", "actions_taken", "confidence"]
        return all(field in response for field in required_fields)

