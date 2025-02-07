from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # File Service Settings
    UPLOAD_DIR: str = Field("data/sample_images", description="Directory for uploaded images")
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png"}
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4o-mini", description="OpenAI model to use")
    OPENAI_MAX_TOKENS: int = Field(200, description="Maximum tokens for narrative generation")
    OPENAI_TEMPERATURE: float = Field(0.7, description="Temperature for narrative generation")
    
    # BLIP Settings
    BLIP_MODEL: str = Field("Salesforce/blip-image-captioning-base", description="BLIP model to use")
    DEVICE: str = Field("cuda", description="Device to use for ML models")
    
    # API Settings
    API_HOST: str = Field("0.0.0.0", description="API host")
    API_PORT: int = Field(8000, description="API port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create global settings instance
settings = Settings() 