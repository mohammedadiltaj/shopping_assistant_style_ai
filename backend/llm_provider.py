"""
Configurable LLM Provider System
Supports OpenAI and Groq (Llama3) with easy switching via environment variables
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import os
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROQ = "groq"


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List] = None
    ) -> str:
        """Generate chat completion"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.default_model = "gpt-4o-mini"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List] = None
    ) -> str:
        """Generate chat completion using OpenAI"""
        # OpenAI client is synchronous, run in executor to avoid blocking
        import asyncio
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=model or self.default_model,
            messages=messages,
            tools=tools,
            temperature=temperature
        )
        return response.choices[0].message.content or ""


class GroqProvider(BaseLLMProvider):
    """Groq provider using Llama3"""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
            # Allow override; default to a currently supported Groq model
            self.default_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        except ImportError:
            raise ImportError(
                "Groq package not installed. Install it with: pip install groq"
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List] = None
    ) -> str:
        """Generate chat completion using Groq"""
        # Groq doesn't support tools parameter, so we ignore it
        # Groq client is synchronous, run in executor to avoid blocking
        import asyncio
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=model or self.default_model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content or ""


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
        """
        Create LLM provider based on configuration
        
        Args:
            provider_name: Provider name from env var LLM_PROVIDER (openai/groq)
                          Defaults to 'groq' if not set
        """
        provider_name = provider_name or os.getenv("LLM_PROVIDER", "groq").lower()
        
        if provider_name == LLMProvider.GROQ:
            return GroqProvider()
        elif provider_name == LLMProvider.OPENAI:
            return OpenAIProvider()
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Supported providers: {[p.value for p in LLMProvider]}"
            )
    
    @staticmethod
    def get_default_model(provider_name: Optional[str] = None) -> str:
        """Get default model for the provider"""
        provider_name = provider_name or os.getenv("LLM_PROVIDER", "groq").lower()
        
        if provider_name == LLMProvider.GROQ:
            return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        elif provider_name == LLMProvider.OPENAI:
            return "gpt-4o-mini"
        else:
            return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Default fallback (Groq)


# Global provider instance (lazy initialization)
_provider_instance: Optional[BaseLLMProvider] = None


def get_llm_provider() -> BaseLLMProvider:
    """Get or create the global LLM provider instance"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = LLMProviderFactory.create_provider()
    return _provider_instance


def reset_provider():
    """Reset the global provider instance (useful for testing or config changes)"""
    global _provider_instance
    _provider_instance = None

