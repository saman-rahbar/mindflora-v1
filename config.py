import os
from typing import Optional

class Config:
    """Configuration for MindFlora platform"""
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # LLM Configuration
    LLM_CLIENT_TYPE = os.getenv("LLM_CLIENT_TYPE", "mock")  # "mock", "openai", "anthropic"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # Privacy Configuration
    PRIVACY_EPSILON = float(os.getenv("PRIVACY_EPSILON", "1.0"))
    ENABLE_LDP = os.getenv("ENABLE_LDP", "True").lower() == "true"
    
    # Database Configuration (for future use)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mindflora.db")
    
    # Feature Flags
    ENABLE_GAMIFICATION = os.getenv("ENABLE_GAMIFICATION", "True").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
    ENABLE_JOURNALING = os.getenv("ENABLE_JOURNALING", "True").lower() == "true"
    
    # Therapy Configuration
    AVAILABLE_THERAPY_MODALITIES = [
        "cbt",
        "logotherapy", 
        "act",
        "dbt",
        "somotherapy",
        "positive_psychology"
    ]
    
    # Gamification Configuration
    XP_REWARDS = {
        "therapy_session": 25,
        "journal_entry": 20,
        "mood_tracking": 5,
        "mission_completion": 15,
        "achievement_unlock": 50
    }
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration based on environment"""
        if cls.LLM_CLIENT_TYPE == "openai" and cls.OPENAI_API_KEY:
            return {
                "client_type": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL
            }
        elif cls.LLM_CLIENT_TYPE == "anthropic" and cls.ANTHROPIC_API_KEY:
            return {
                "client_type": "anthropic", 
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": cls.ANTHROPIC_MODEL
            }
        else:
            return {
                "client_type": "mock"
            }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return not cls.DEBUG and cls.SECRET_KEY != "your-secret-key-change-in-production"
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return any issues"""
        issues = []
        
        if cls.is_production():
            if cls.LLM_CLIENT_TYPE == "openai" and not cls.OPENAI_API_KEY:
                issues.append("OpenAI API key required for production")
            elif cls.LLM_CLIENT_TYPE == "anthropic" and not cls.ANTHROPIC_API_KEY:
                issues.append("Anthropic API key required for production")
        
        if cls.PRIVACY_EPSILON < 0.1:
            issues.append("Privacy epsilon too low, may affect functionality")
        
        return issues

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LLM_CLIENT_TYPE = "mock"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LLM_CLIENT_TYPE = "openai"  # or "anthropic"

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    LLM_CLIENT_TYPE = "mock"
    ENABLE_ANALYTICS = False

# Configuration factory
def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig 