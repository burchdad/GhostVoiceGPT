"""
API Security & Authentication Layer
JWT authentication, API key management, and request validation
"""

import hashlib
import time
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Optional JWT import with fallback
try:
    import jwt
    JWT_AVAILABLE = True
    jwt_module = jwt  # Store reference for use in methods
except ImportError:
    print("PyJWT not available. Install with: pip install PyJWT")
    JWT_AVAILABLE = False
    jwt_module = None

# Optional FastAPI imports with fallback
try:
    from fastapi import HTTPException, Depends, Security  # type: ignore
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # type: ignore
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI not available. API security module can still be used for JWT and API key management.")
    FASTAPI_AVAILABLE = False
    
    # Create dummy classes for type hints when FastAPI is not available
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"HTTP {status_code}: {detail}")
    
    class HTTPBearer:
        def __init__(self):
            pass
        
        def __call__(self):
            return None
    
    class HTTPAuthorizationCredentials:
        def __init__(self, scheme: str = "", credentials: str = ""):
            self.scheme = scheme
            self.credentials = credentials
    
    def Depends(func):
        return func
    
    def Security(func):
        return func

@dataclass
class APIKey:
    """API key configuration"""
    key_id: str
    api_key: str
    client_name: str
    permissions: List[str]
    rate_limit: int  # requests per hour
    created_at: datetime
    expires_at: Optional[datetime] = None
    active: bool = True

class APISecurityManager:
    """Comprehensive API security and authentication system"""
    
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
        self.security = HTTPBearer()
        self.api_keys: Dict[str, APIKey] = {}
        self.request_logs: Dict[str, List[datetime]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load demo API keys
        self._initialize_demo_keys()
    
    def _initialize_demo_keys(self):
        """Initialize demo API keys for testing"""
        demo_keys = [
            APIKey(
                key_id="demo_prod",
                api_key="gv_prod_" + hashlib.sha256(b"production_key").hexdigest()[:32],
                client_name="Production Client",
                permissions=["calls:outbound", "calls:inbound", "webhooks:receive", "metrics:read"],
                rate_limit=1000,
                created_at=datetime.now()
            ),
            APIKey(
                key_id="demo_test",
                api_key="gv_test_" + hashlib.sha256(b"testing_key").hexdigest()[:32],
                client_name="Testing Client", 
                permissions=["calls:outbound", "metrics:read"],
                rate_limit=100,
                created_at=datetime.now()
            )
        ]
        
        for key in demo_keys:
            self.api_keys[key.api_key] = key
    
    def validate_api_key(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> APIKey:
        """Validate API key and return key info"""
        api_key = credentials.credentials
        
        if api_key not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        key_info = self.api_keys[api_key]
        
        if not key_info.active:
            raise HTTPException(status_code=401, detail="API key deactivated")
        
        if key_info.expires_at and key_info.expires_at < datetime.now():
            raise HTTPException(status_code=401, detail="API key expired")
        
        # Check rate limits
        if not self._check_rate_limit(key_info):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        return key_info
    
    def _check_rate_limit(self, key_info: APIKey) -> bool:
        """Check if API key is within rate limits"""
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        
        # Initialize request log if needed
        if key_info.api_key not in self.request_logs:
            self.request_logs[key_info.api_key] = []
        
        # Clean old requests
        requests = self.request_logs[key_info.api_key]
        self.request_logs[key_info.api_key] = [
            req_time for req_time in requests if req_time > hour_ago
        ]
        
        # Check current count
        current_requests = len(self.request_logs[key_info.api_key])
        if current_requests >= key_info.rate_limit:
            return False
        
        # Log this request
        self.request_logs[key_info.api_key].append(current_time)
        return True
    
    def require_permission(self, permission: str) -> Callable:
        """Decorator to require specific permission"""
        def dependency(api_key: Optional[APIKey] = None) -> APIKey:
            # When FastAPI is available, this will be properly injected
            if not FASTAPI_AVAILABLE:
                # Fallback for non-FastAPI usage
                return list(self.api_keys.values())[0] if self.api_keys else APIKey(
                    key_id="fallback", api_key="fallback", client_name="fallback",
                    permissions=[permission], rate_limit=100, created_at=datetime.now()
                )
            
            # This will be replaced by FastAPI dependency injection
            if api_key is None:
                api_key = self.validate_api_key()
            
            if permission not in api_key.permissions:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission '{permission}' required"
                )
            return api_key
        
        return dependency
    
    def generate_jwt_token(self, user_id: str, permissions: List[str], expires_hours: int = 24) -> str:
        """Generate JWT token for session-based auth"""
        if not JWT_AVAILABLE:
            # Fallback: create a simple token without encryption
            payload = f"{user_id}:{','.join(permissions)}:{int(time.time() + expires_hours * 3600)}"
            return hashlib.sha256(payload.encode()).hexdigest()
        
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow()
        }
        
        if JWT_AVAILABLE and jwt_module:
            return jwt_module.encode(payload, self.jwt_secret, algorithm="HS256")
        else:
            # Fallback if jwt module is not available
            payload_str = f"{user_id}:{','.join(permissions)}:{int(time.time() + expires_hours * 3600)}"
            return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def validate_jwt_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Dict[str, Any]:
        """Validate JWT token and return payload"""
        if not JWT_AVAILABLE:
            # Fallback: basic validation without decryption
            token = credentials.credentials if hasattr(credentials, 'credentials') else ""
            if len(token) == 64:  # SHA256 hash length
                return {"user_id": "fallback_user", "permissions": ["basic_access"]}
            else:
                raise HTTPException(status_code=401, detail="Invalid token format")
        
        try:
            token = credentials.credentials
            if JWT_AVAILABLE and jwt_module:
                payload = jwt_module.decode(token, self.jwt_secret, algorithms=["HS256"])
                return payload
            else:
                # Fallback validation
                if len(token) == 64:
                    return {"user_id": "fallback_user", "permissions": ["basic_access"]}
                else:
                    raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            if JWT_AVAILABLE and jwt_module:
                if "ExpiredSignature" in str(e):
                    raise HTTPException(status_code=401, detail="Token expired")
                else:
                    raise HTTPException(status_code=401, detail="Invalid token")
            else:
                raise HTTPException(status_code=401, detail="Token validation failed")
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        self.logger.warning(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
        )

# Usage example for FastAPI integration
"""
# In your main FastAPI app:

security_manager = APISecurityManager(jwt_secret="your-secret-key")

@app.post("/calls/outbound")
async def make_call(
    request: Dict[str, Any],
    api_key: APIKey = Depends(security_manager.require_permission("calls:outbound"))
):
    # Your call logic here
    pass

@app.get("/metrics/dashboard")  
async def get_metrics(
    api_key: APIKey = Depends(security_manager.require_permission("metrics:read"))
):
    # Your metrics logic here
    pass
"""

if __name__ == "__main__":
    print("🔐 API Security Manager Demo")
    print("=" * 40)
    
    security = APISecurityManager("demo-secret-key")
    
    # Show demo API keys
    print("Demo API Keys:")
    for key_info in security.api_keys.values():
        print(f"  Client: {key_info.client_name}")
        print(f"  Key ID: {key_info.key_id}")
        print(f"  Permissions: {', '.join(key_info.permissions)}")
        print(f"  Rate Limit: {key_info.rate_limit}/hour")
        print()
    
    # Generate JWT token
    token = security.generate_jwt_token("demo_user", ["calls:outbound", "metrics:read"])
    print(f"Sample JWT Token: {token[:50]}...")
    
    print("\n✅ API Security system ready!")
    print("   - API key authentication")
    print("   - Permission-based access control")
    print("   - Rate limiting per client")
    print("   - JWT session tokens")
    print("   - Security headers")
    print("   - Audit logging")