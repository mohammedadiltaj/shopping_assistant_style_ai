"""
Configuration management for the shopping assistant
"""

import os
from typing import Optional
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROQ = "groq"


class Config:
    """Application configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://shopping_user:shopping_pass@localhost:5432/shopping_db"
    )
    
    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration"""
        if cls.LLM_PROVIDER == LLMProvider.OPENAI and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )
        
        if cls.LLM_PROVIDER == LLMProvider.GROQ and not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER=groq"
            )
        
        if cls.LLM_PROVIDER not in [p.value for p in LLMProvider]:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. "
                f"Must be one of: {[p.value for p in LLMProvider]}"
            )
    
    @classmethod
    def get_provider_info(cls) -> dict:
        """Get current provider information"""
        return {
            "provider": cls.LLM_PROVIDER,
            "has_api_key": bool(
                cls.OPENAI_API_KEY if cls.LLM_PROVIDER == LLMProvider.OPENAI 
                else cls.GROQ_API_KEY
            )
        }

