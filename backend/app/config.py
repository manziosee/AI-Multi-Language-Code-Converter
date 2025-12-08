from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AI Provider Selection
    ai_provider: str = "groq"  # groq, huggingface, or openai
    
    # Groq Configuration
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Hugging Face Configuration
    huggingface_api_key: str = ""
    
    # OpenAI Configuration (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    # Server Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
