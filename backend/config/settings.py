from typing import Optional
from pydantic_settings import BaseSettings # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: Optional[str] = None
    
    # JWT settings
    JWT_SECRET: Optional[str] = None
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    VECTOR_STORE_TABLE: str = "documents"
    VECTOR_STORE_QUERY: str = "match_documents"
    
    # API Keys
    FRED_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    # Model settings
    MODEL_NAME: str = "gpt-4-turbo-preview"
    TEMPERATURE: float = 0.7
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True  # We need case-sensitive matching for these variables
        extra = "allow"  # Allow extra fields in the settings

# Create settings instance
settings = Settings()