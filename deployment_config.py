"""
Production Deployment Configuration & Environment Management
Comprehensive configuration management for different deployment environments
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from pathlib import Path
import logging

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 10
    ssl_mode: str = "require"
    connection_timeout: int = 30

@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 10
    ssl: bool = False

@dataclass
class VoiceServiceConfig:
    """Voice service configuration"""
    elevenlabs_api_key: str
    default_voice: str = "adam"
    max_text_length: int = 5000
    quality_preset: str = "high"
    enable_streaming: bool = True
    rate_limit_per_minute: int = 100

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str
    api_key_encryption_key: str
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    max_request_size_mb: int = 10
    enable_rate_limiting: bool = True
    session_timeout_hours: int = 24

@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_telemetry: bool = True
    log_level: str = "INFO"
    metrics_retention_hours: int = 24
    enable_health_checks: bool = True
    enable_performance_profiling: bool = False
    alert_webhook_url: Optional[str] = None

@dataclass
class CarrierConfig:
    """Telecom carrier configuration"""
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    telnyx_api_key: Optional[str] = None
    vonage_api_key: Optional[str] = None
    vonage_api_secret: Optional[str] = None
    default_carrier: str = "twilio"

@dataclass
class AppConfig:
    """Main application configuration"""
    environment: str  # development, staging, production
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    max_concurrent_calls: int = 100
    enable_websockets: bool = True
    webhook_timeout_seconds: int = 30

@dataclass
class ProductionConfig:
    """Complete production configuration"""
    app: AppConfig
    database: DatabaseConfig
    redis: RedisConfig
    voice_service: VoiceServiceConfig
    security: SecurityConfig
    monitoring: MonitoringConfig
    carriers: CarrierConfig
    
    @classmethod
    def from_environment(cls, env: str = "production") -> "ProductionConfig":
        """Load configuration from environment variables and files"""
        config_loader = ConfigurationManager()
        return config_loader.load_config(env)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def save_to_file(self, filepath: str):
        """Save configuration to file"""
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

class ConfigurationManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self, environment: str) -> ProductionConfig:
        """Load configuration for specific environment"""
        
        # Load base configuration
        base_config = self._load_base_config()
        
        # Load environment-specific overrides
        env_config = self._load_environment_config(environment)
        
        # Merge configurations
        merged_config = self._merge_configs(base_config, env_config)
        
        # Load from environment variables
        env_vars_config = self._load_from_environment_variables()
        
        # Final merge with environment variables taking precedence
        final_config = self._merge_configs(merged_config, env_vars_config)
        
        # Validate configuration
        self._validate_config(final_config, environment)
        
        return self._dict_to_config(final_config, environment)
    
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration"""
        base_file = self.config_dir / "base.yaml"
        
        if base_file.exists():
            with open(base_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Default base configuration
        return {
            "app": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "workers": 1,
                "max_concurrent_calls": 100,
                "enable_websockets": True,
                "webhook_timeout_seconds": 30
            },
            "voice_service": {
                "default_voice": "adam",
                "max_text_length": 5000,
                "quality_preset": "high",
                "enable_streaming": True,
                "rate_limit_per_minute": 100
            },
            "security": {
                "enable_cors": True,
                "allowed_origins": ["*"],
                "max_request_size_mb": 10,
                "enable_rate_limiting": True,
                "session_timeout_hours": 24
            },
            "monitoring": {
                "enable_telemetry": True,
                "log_level": "INFO",
                "metrics_retention_hours": 24,
                "enable_health_checks": True,
                "enable_performance_profiling": False
            },
            "carriers": {
                "default_carrier": "twilio"
            }
        }
    
    def _load_environment_config(self, environment: str) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        env_file = self.config_dir / f"{environment}.yaml"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Environment-specific defaults
        if environment == "development":
            return {
                "app": {"debug": True, "port": 8000},
                "monitoring": {"log_level": "DEBUG"},
                "security": {"allowed_origins": ["http://localhost:*"]}
            }
        elif environment == "staging":
            return {
                "app": {"debug": False, "workers": 2},
                "monitoring": {"enable_performance_profiling": True}
            }
        elif environment == "production":
            return {
                "app": {"debug": False, "workers": 4, "max_concurrent_calls": 500},
                "security": {"allowed_origins": ["https://yourdomain.com"]},
                "monitoring": {"log_level": "WARNING"}
            }
        
        return {}
    
    def _load_from_environment_variables(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # Database configuration
        if os.getenv("DATABASE_URL"):
            db_url = os.getenv("DATABASE_URL")
            # Parse database URL (simplified)
            config["database"] = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "ghostvoice"),
                "username": os.getenv("DB_USER", "ghostvoice"),
                "password": os.getenv("DB_PASSWORD", ""),
                "ssl_mode": os.getenv("DB_SSL_MODE", "require")
            }
        
        # Redis configuration
        if os.getenv("REDIS_URL"):
            config["redis"] = {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "password": os.getenv("REDIS_PASSWORD"),
                "ssl": os.getenv("REDIS_SSL", "false").lower() == "true"
            }
        
        # Voice service configuration
        if os.getenv("ELEVENLABS_API_KEY"):
            config["voice_service"] = {
                "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY")
            }
        
        # Security configuration
        if os.getenv("JWT_SECRET"):
            config["security"] = {
                "jwt_secret": os.getenv("JWT_SECRET"),
                "api_key_encryption_key": os.getenv("API_KEY_ENCRYPTION_KEY", os.getenv("JWT_SECRET"))
            }
        
        # Carrier configuration
        carrier_config = {}
        if os.getenv("TWILIO_ACCOUNT_SID"):
            carrier_config["twilio_account_sid"] = os.getenv("TWILIO_ACCOUNT_SID")
            carrier_config["twilio_auth_token"] = os.getenv("TWILIO_AUTH_TOKEN")
        
        if os.getenv("TELNYX_API_KEY"):
            carrier_config["telnyx_api_key"] = os.getenv("TELNYX_API_KEY")
        
        if carrier_config:
            config["carriers"] = carrier_config
        
        # Monitoring configuration
        monitoring_config = {}
        if os.getenv("LOG_LEVEL"):
            monitoring_config["log_level"] = os.getenv("LOG_LEVEL")
        
        if os.getenv("ALERT_WEBHOOK_URL"):
            monitoring_config["alert_webhook_url"] = os.getenv("ALERT_WEBHOOK_URL")
        
        if monitoring_config:
            config["monitoring"] = monitoring_config
        
        return config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_config(self, config: Dict[str, Any], environment: str):
        """Validate configuration for specific environment"""
        errors = []
        
        # Required fields for production
        if environment == "production":
            required_fields = [
                ("voice_service", "elevenlabs_api_key"),
                ("security", "jwt_secret"),
                ("security", "api_key_encryption_key")
            ]
            
            for section, field in required_fields:
                if section not in config or field not in config[section] or not config[section][field]:
                    errors.append(f"Missing required field: {section}.{field}")
        
        # Validate port ranges
        if "app" in config and "port" in config["app"]:
            port = config["app"]["port"]
            if not (1 <= port <= 65535):
                errors.append(f"Invalid port number: {port}")
        
        # Validate log levels
        if "monitoring" in config and "log_level" in config["monitoring"]:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            level = config["monitoring"]["log_level"].upper()
            if level not in valid_levels:
                errors.append(f"Invalid log level: {level}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _dict_to_config(self, config_dict: Dict[str, Any], environment: str) -> ProductionConfig:
        """Convert dictionary to ProductionConfig object"""
        try:
            return ProductionConfig(
                app=AppConfig(environment=environment, **config_dict.get("app", {})),
                database=DatabaseConfig(**config_dict.get("database", {
                    "host": "localhost", "port": 5432, "database": "ghostvoice",
                    "username": "ghostvoice", "password": ""
                })),
                redis=RedisConfig(**config_dict.get("redis", {
                    "host": "localhost", "port": 6379
                })),
                voice_service=VoiceServiceConfig(**config_dict.get("voice_service", {
                    "elevenlabs_api_key": "your-api-key-here"
                })),
                security=SecurityConfig(**config_dict.get("security", {
                    "jwt_secret": "your-jwt-secret-here",
                    "api_key_encryption_key": "your-encryption-key-here"
                })),
                monitoring=MonitoringConfig(**config_dict.get("monitoring", {})),
                carriers=CarrierConfig(**config_dict.get("carriers", {}))
            )
        except TypeError as e:
            raise ValueError(f"Failed to create configuration object: {e}")
    
    def create_sample_configs(self):
        """Create sample configuration files"""
        
        # Create base.yaml
        base_config = {
            "app": {
                "host": "0.0.0.0",
                "port": 8000,
                "max_concurrent_calls": 100,
                "enable_websockets": True
            },
            "voice_service": {
                "default_voice": "adam",
                "max_text_length": 5000,
                "enable_streaming": True
            },
            "security": {
                "enable_cors": True,
                "max_request_size_mb": 10,
                "session_timeout_hours": 24
            },
            "monitoring": {
                "enable_telemetry": True,
                "metrics_retention_hours": 24,
                "enable_health_checks": True
            }
        }
        
        with open(self.config_dir / "base.yaml", 'w') as f:
            yaml.dump(base_config, f, default_flow_style=False)
        
        # Create production.yaml
        prod_config = {
            "app": {
                "debug": False,
                "workers": 4,
                "max_concurrent_calls": 500
            },
            "security": {
                "allowed_origins": ["https://yourdomain.com"],
                "enable_rate_limiting": True
            },
            "monitoring": {
                "log_level": "WARNING",
                "enable_performance_profiling": False
            }
        }
        
        with open(self.config_dir / "production.yaml", 'w') as f:
            yaml.dump(prod_config, f, default_flow_style=False)
        
        # Create .env.example
        env_example = """# GhostVoiceGPT Environment Configuration

# Voice Service
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Security
JWT_SECRET=your_jwt_secret_here
API_KEY_ENCRYPTION_KEY=your_encryption_key_here

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/ghostvoice
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ghostvoice
DB_USER=ghostvoice
DB_PASSWORD=your_db_password
DB_SSL_MODE=require

# Redis Cache
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Telecom Carriers
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TELNYX_API_KEY=your_telnyx_api_key
VONAGE_API_KEY=your_vonage_api_key
VONAGE_API_SECRET=your_vonage_api_secret

# Monitoring & Alerts
LOG_LEVEL=INFO
ALERT_WEBHOOK_URL=https://hooks.slack.com/your/webhook/url

# Application
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
MAX_CONCURRENT_CALLS=500
"""
        
        with open(self.config_dir / ".env.example", 'w') as f:
            f.write(env_example)
        
        print(f"✅ Sample configuration files created in {self.config_dir}/")

if __name__ == "__main__":
    print("⚙️  Production Configuration Management Demo")
    print("=" * 50)
    
    # Create sample configurations
    config_manager = ConfigurationManager()
    config_manager.create_sample_configs()
    
    # Load development configuration
    try:
        dev_config = config_manager.load_config("development")
        print(f"✅ Development config loaded successfully")
        print(f"   Environment: {dev_config.app.environment}")
        print(f"   Debug: {dev_config.app.debug}")
        print(f"   Port: {dev_config.app.port}")
        print(f"   Log Level: {dev_config.monitoring.log_level}")
    except Exception as e:
        print(f"❌ Error loading development config: {e}")
    
    # Try loading production config (will use defaults if no env vars)
    try:
        prod_config = config_manager.load_config("production")
        print(f"✅ Production config loaded successfully")
        print(f"   Environment: {prod_config.app.environment}")
        print(f"   Workers: {prod_config.app.workers}")
        print(f"   Max Calls: {prod_config.app.max_concurrent_calls}")
        print(f"   CORS Enabled: {prod_config.security.enable_cors}")
    except Exception as e:
        print(f"❌ Error loading production config: {e}")
    
    print("\n📁 Configuration Files Created:")
    print("   - config/base.yaml (base configuration)")
    print("   - config/production.yaml (production overrides)")
    print("   - config/.env.example (environment variables template)")
    
    print("\n✅ Configuration management system ready!")
    print("   - Environment-specific configurations")
    print("   - Environment variable integration")
    print("   - Configuration validation")
    print("   - Sample file generation")
    print("   - Deep configuration merging")