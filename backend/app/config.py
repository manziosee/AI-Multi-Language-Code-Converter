from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI Provider Selection: groq | huggingface | openai | openai_compatible
    ai_provider: str = "groq"

    # Groq Configuration
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"  # llama-3.3-70b retired for free tier Aug 2026

    # Hugging Face Inference Providers (OpenAI-compatible router).
    # The old api-inference.huggingface.co endpoint was shut down.
    huggingface_api_key: str = ""
    huggingface_model: str = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    huggingface_base_url: str = "https://router.huggingface.co/v1"

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Generic OpenAI-compatible provider (any /v1/chat/completions endpoint:
    # Together, OpenRouter, Ollama, LM Studio, HF router, DemonRoute, ...)
    openai_compatible_name: str = "OpenAI-compatible"
    openai_compatible_base_url: str = ""
    openai_compatible_api_key: str = ""
    openai_compatible_model: str = ""

    # /execute runs user code on the server. Off by default: only enable it
    # inside an isolated sandbox you control.
    enable_code_execution: bool = False

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
