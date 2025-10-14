"""Simple configuration management for GhostVoiceGPT"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ghostvoice"
    username: str = "ghost"
    password: str = ""
    
    def __post_init__(self):
        self.host = os.getenv("DB_HOST", self.host)
        self.port = int(os.getenv("DB_PORT", str(self.port)))
        self.database = os.getenv("DB_NAME", self.database)
        self.username = os.getenv("DB_USER", self.username)
        self.password = os.getenv("DB_PASSWORD", self.password)
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    
    def __post_init__(self):
        self.host = os.getenv("REDIS_HOST", self.host)
        self.port = int(os.getenv("REDIS_PORT", str(self.port)))
        self.password = os.getenv("REDIS_PASSWORD", self.password)
        self.db = int(os.getenv("REDIS_DB", str(self.db)))
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class TelephonyCarrierConfig:
    """Telephony carrier configuration"""
    # Twilio
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Telnyx
    telnyx_api_key: Optional[str] = None
    telnyx_phone_number: Optional[str] = None
    
    # Vonage
    vonage_api_key: Optional[str] = None
    vonage_api_secret: Optional[str] = None
    vonage_application_id: Optional[str] = None
    vonage_private_key: Optional[str] = None
    
    # SignalWire
    signalwire_project_id: Optional[str] = None
    signalwire_auth_token: Optional[str] = None
    signalwire_space_url: Optional[str] = None
    
    # Bandwidth
    bandwidth_account_id: Optional[str] = None
    bandwidth_username: Optional[str] = None
    bandwidth_password: Optional[str] = None
    
    def __post_init__(self):
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        self.telnyx_api_key = os.getenv("TELNYX_API_KEY")
        self.telnyx_phone_number = os.getenv("TELNYX_PHONE_NUMBER")
        
        self.vonage_api_key = os.getenv("VONAGE_API_KEY")
        self.vonage_api_secret = os.getenv("VONAGE_API_SECRET")
        self.vonage_application_id = os.getenv("VONAGE_APPLICATION_ID")
        self.vonage_private_key = os.getenv("VONAGE_PRIVATE_KEY")
        
        self.signalwire_project_id = os.getenv("SIGNALWIRE_PROJECT_ID")
        self.signalwire_auth_token = os.getenv("SIGNALWIRE_AUTH_TOKEN")
        self.signalwire_space_url = os.getenv("SIGNALWIRE_SPACE_URL")
        
        self.bandwidth_account_id = os.getenv("BANDWIDTH_ACCOUNT_ID")
        self.bandwidth_username = os.getenv("BANDWIDTH_USERNAME")
        self.bandwidth_password = os.getenv("BANDWIDTH_PASSWORD")


@dataclass
class AIConfig:
    """AI service configuration"""
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    
    # ElevenLabs
    elevenlabs_api_key: Optional[str] = None
    
    # Deepgram
    deepgram_api_key: Optional[str] = None
    
    # Voice settings
    default_voice_provider: str = "elevenlabs"
    default_stt_provider: str = "openai"
    
    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.default_voice_provider = os.getenv("DEFAULT_VOICE_PROVIDER", self.default_voice_provider)
        self.default_stt_provider = os.getenv("DEFAULT_STT_PROVIDER", self.default_stt_provider)


@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    webhook_base_url: str = "https://your-domain.com"
    allowed_origins: list = None
    secret_key: str = "your-secret-key-change-this"
    
    def __post_init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", str(self.port)))
        self.webhook_base_url = os.getenv("WEBHOOK_BASE_URL", self.webhook_base_url)
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]


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