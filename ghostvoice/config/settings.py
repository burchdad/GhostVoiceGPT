"""Configuration management for GhostVoiceGPT"""

import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="ghostvoice", env="DB_NAME")
    username: str = Field(default="ghost", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis configuration settings"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class TelephonyCarrierConfig(BaseSettings):
    """Telephony carrier configuration"""
    # Twilio
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    # Telnyx
    telnyx_api_key: Optional[str] = Field(default=None, env="TELNYX_API_KEY")
    telnyx_phone_number: Optional[str] = Field(default=None, env="TELNYX_PHONE_NUMBER")
    
    # Vonage
    vonage_api_key: Optional[str] = Field(default=None, env="VONAGE_API_KEY")
    vonage_api_secret: Optional[str] = Field(default=None, env="VONAGE_API_SECRET")
    vonage_application_id: Optional[str] = Field(default=None, env="VONAGE_APPLICATION_ID")
    vonage_private_key: Optional[str] = Field(default=None, env="VONAGE_PRIVATE_KEY")
    
    # SignalWire
    signalwire_project_id: Optional[str] = Field(default=None, env="SIGNALWIRE_PROJECT_ID")
    signalwire_auth_token: Optional[str] = Field(default=None, env="SIGNALWIRE_AUTH_TOKEN")
    signalwire_space_url: Optional[str] = Field(default=None, env="SIGNALWIRE_SPACE_URL")
    
    # Bandwidth
    bandwidth_account_id: Optional[str] = Field(default=None, env="BANDWIDTH_ACCOUNT_ID")
    bandwidth_username: Optional[str] = Field(default=None, env="BANDWIDTH_USERNAME")
    bandwidth_password: Optional[str] = Field(default=None, env="BANDWIDTH_PASSWORD")


class AIConfig(BaseSettings):
    """AI service configuration"""
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    
    # ElevenLabs
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    
    # Deepgram
    deepgram_api_key: Optional[str] = Field(default=None, env="DEEPGRAM_API_KEY")
    
    # Voice settings
    default_voice_provider: Literal["openai", "elevenlabs"] = Field(default="openai", env="DEFAULT_VOICE_PROVIDER")
    default_stt_provider: Literal["openai", "deepgram"] = Field(default="openai", env="DEFAULT_STT_PROVIDER")


class AppConfig(BaseSettings):
    """Main application configuration"""
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    webhook_base_url: str = Field(default="https://your-domain.com", env="WEBHOOK_BASE_URL")
    allowed_origins: list[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    secret_key: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    
    class Config:
        env_file = ".env"


class Settings:
    """Global settings container"""
    
    def __init__(self):
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.telephony = TelephonyCarrierConfig()
        self.ai = AIConfig()


# Global settings instance
settings = Settings()