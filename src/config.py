from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # File Service Settings
    UPLOAD_DIR: str = Field("data/sample_images", description="Directory for uploaded images")
    AUDIO_DIR: str = Field("data/audio", description="Directory for audio files")
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png"}
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4o-mini", description="OpenAI model to use")
    OPENAI_MAX_TOKENS: int = Field(200, description="Maximum tokens for narrative generation")
    OPENAI_TEMPERATURE: float = Field(0.7, description="Temperature for narrative generation")
    
    # BLIP Settings
    BLIP_MODEL: str = Field("Salesforce/blip-image-captioning-base", description="BLIP model to use")
    DEVICE: str = Field("cuda", description="Device to use for ML models")
    
    # TTS Settings
    TTS_LANGUAGE: str = Field("en", description="Default language for TTS")
    TTS_CLEANUP_AGE: int = Field(24, description="Age in hours after which to clean up audio files")
    
    # API Settings
    API_HOST: str = Field("0.0.0.0", description="API host")
    API_PORT: int = Field(8000, description="API port")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create global settings instance
settings = Settings() 