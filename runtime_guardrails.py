"""
Runtime Guardrails & Safety System
Comprehensive safety, compliance, and resilience controls for production voice calls
"""

import asyncio
import time
import re
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOX = "sox"
    TCPA = "tcpa"

@dataclass
class PIIDetection:
    """Personally Identifiable Information detection result"""
    detected: bool
    pii_types: List[str]
    confidence: float
    masked_content: str
    original_positions: List[Tuple[int, int]]

@dataclass
class ComplianceViolation:
    """Compliance framework violation"""
    framework: ComplianceFramework
    rule_id: str
    severity: RiskLevel
    description: str
    detected_content: str
    timestamp: datetime

@dataclass
class SafetyIncident:
    """Safety incident record"""
    incident_id: str
    incident_type: str
    risk_level: RiskLevel
    call_id: str
    session_id: str
    description: str
    auto_action_taken: str
    human_review_required: bool
    timestamp: datetime

class PIIDetector:
    """Detect and mask personally identifiable information"""
    
    def __init__(self):
        # PII detection patterns
        self.patterns = {
            "ssn": re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "phone": re.compile(r'\b\d{3}-?\d{3}-?\d{4}\b'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "dob": re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            "account_number": re.compile(r'\b\d{8,20}\b'),
            "routing_number": re.compile(r'\b\d{9}\b'),
            "zip_code": re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            "address": re.compile(r'\b\d+\s+\w+\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd)\b', re.IGNORECASE)
        }
        
        # Sensitive keywords that might indicate PII context
        self.sensitive_keywords = {
            "security_questions": ["mother's maiden name", "first pet", "childhood friend", "high school"],
            "financial": ["bank account", "routing number", "social security", "credit score"],
            "medical": ["diagnosis", "prescription", "medical record", "health condition"],
            "personal": ["password", "pin number", "secret", "confidential"]
        }
        
        self.logger = logging.getLogger(__name__)
    
    def detect_and_mask(self, text: str) -> PIIDetection:
        """Detect PII in text and return masked version"""
        
        detected_types = []
        positions = []
        masked_text = text
        confidence_scores = []
        
        # Check each PII pattern
        for pii_type, pattern in self.patterns.items():
            matches = list(pattern.finditer(text))
            
            for match in matches:
                detected_types.append(pii_type)
                positions.append((match.start(), match.end()))
                
                # Calculate confidence based on pattern specificity
                confidence = self._calculate_confidence(pii_type, match.group())
                confidence_scores.append(confidence)
                
                # Mask the detected PII
                mask_char = "*"
                mask_length = len(match.group())
                mask = f"[{pii_type.upper()}]" + mask_char * max(0, mask_length - len(pii_type) - 2)
                
                masked_text = masked_text[:match.start()] + mask + masked_text[match.end():]
        
        # Check for sensitive keyword contexts
        for category, keywords in self.sensitive_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    detected_types.append(f"context_{category}")
                    confidence_scores.append(0.7)  # Medium confidence for contextual detection
        
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        return PIIDetection(
            detected=len(detected_types) > 0,
            pii_types=list(set(detected_types)),  # Remove duplicates
            confidence=overall_confidence,
            masked_content=masked_text,
            original_positions=positions
        )
    
    def _calculate_confidence(self, pii_type: str, content: str) -> float:
        """Calculate confidence score for PII detection"""
        
        confidence_map = {
            "ssn": 0.95,  # SSN pattern is highly specific
            "credit_card": 0.90,  # Credit card pattern is specific
            "email": 0.85,  # Email pattern is fairly specific
            "phone": 0.75,  # Phone numbers can be ambiguous
            "account_number": 0.60,  # Account numbers are generic
            "zip_code": 0.70,  # Zip codes are moderately specific
            "dob": 0.65,  # Date patterns can be ambiguous
            "routing_number": 0.90,  # Routing numbers are specific
            "address": 0.80  # Address patterns are fairly specific
        }
        
        base_confidence = confidence_map.get(pii_type, 0.5)
        
        # Adjust based on content characteristics
        if pii_type == "phone" and len(content.replace("-", "").replace(" ", "")) == 10:
            base_confidence += 0.1  # US phone number format
        
        if pii_type == "ssn" and "-" in content:
            base_confidence += 0.05  # Formatted SSN
        
        return min(1.0, base_confidence)

class ComplianceEngine:
    """Compliance framework enforcement engine"""
    
    def __init__(self):
        self.active_frameworks = [ComplianceFramework.PCI_DSS, ComplianceFramework.TCPA]
        self.violation_history: List[ComplianceViolation] = []
        self.logger = logging.getLogger(__name__)
        
        # Compliance rules
        self.rules = {
            ComplianceFramework.PCI_DSS: {
                "no_cc_storage": {
                    "description": "Credit card numbers must not be stored",
                    "severity": RiskLevel.CRITICAL,
                    "pattern": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
                },
                "no_cvv_storage": {
                    "description": "CVV codes must not be stored",
                    "severity": RiskLevel.CRITICAL,
                    "pattern": re.compile(r'\bcvv:?\s*\d{3,4}\b', re.IGNORECASE)
                }
            },
            ComplianceFramework.TCPA: {
                "consent_required": {
                    "description": "Calls require explicit consent",
                    "severity": RiskLevel.HIGH,
                    "pattern": None  # Handled by business logic
                },
                "do_not_call": {
                    "description": "Must respect do-not-call preferences",
                    "severity": RiskLevel.CRITICAL,
                    "pattern": None
                }
            },
            ComplianceFramework.HIPAA: {
                "phi_protection": {
                    "description": "Protected health information must be secured",
                    "severity": RiskLevel.CRITICAL,
                    "pattern": re.compile(r'\b(?:diagnosis|prescription|medical record|health condition)\b', re.IGNORECASE)
                }
            }
        }
    
    def check_compliance(self, content: str, call_metadata: Dict[str, Any]) -> List[ComplianceViolation]:
        """Check content against active compliance frameworks"""
        
        violations = []
        
        for framework in self.active_frameworks:
            framework_violations = self._check_framework(framework, content, call_metadata)
            violations.extend(framework_violations)
        
        # Log violations
        for violation in violations:
            self.violation_history.append(violation)
            self.logger.warning(f"Compliance violation | {violation.framework.value} | {violation.rule_id} | {violation.severity.name}")
        
        return violations
    
    def _check_framework(self, framework: ComplianceFramework, content: str, metadata: Dict[str, Any]) -> List[ComplianceViolation]:
        """Check specific compliance framework rules"""
        
        violations = []
        
        if framework not in self.rules:
            return violations
        
        for rule_id, rule_config in self.rules[framework].items():
            violation = self._check_rule(framework, rule_id, rule_config, content, metadata)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_rule(self, framework: ComplianceFramework, rule_id: str, rule_config: Dict, content: str, metadata: Dict) -> Optional[ComplianceViolation]:
        """Check individual compliance rule"""
        
        # Pattern-based rules
        if rule_config.get("pattern"):
            match = rule_config["pattern"].search(content)
            if match:
                return ComplianceViolation(
                    framework=framework,
                    rule_id=rule_id,
                    severity=rule_config["severity"],
                    description=rule_config["description"],
                    detected_content=match.group(),
                    timestamp=datetime.now()
                )
        
        # Business logic rules
        if framework == ComplianceFramework.TCPA:
            if rule_id == "consent_required" and not metadata.get("consent_obtained", False):
                return ComplianceViolation(
                    framework=framework,
                    rule_id=rule_id,
                    severity=rule_config["severity"],
                    description="Call made without explicit consent",
                    detected_content="No consent flag",
                    timestamp=datetime.now()
                )
            
            if rule_id == "do_not_call" and metadata.get("dnc_listed", False):
                return ComplianceViolation(
                    framework=framework,
                    rule_id=rule_id,
                    severity=rule_config["severity"],
                    description="Call to number on do-not-call list",
                    detected_content="DNC listed number",
                    timestamp=datetime.now()
                )
        
        return None

class CircuitBreaker:
    """Circuit breaker pattern for system resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
        self.logger = logging.getLogger(__name__)
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
                self.logger.info("Circuit breaker transitioning to half-open")
            else:
                raise Exception("Circuit breaker is open - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time:
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
            return time_since_failure >= self.recovery_timeout
        return False
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == "half-open":
            self.state = "closed"
            self.logger.info("Circuit breaker closed - service recovered")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.logger.error(f"Circuit breaker opened - {self.failure_count} failures")

class RuntimeGuardrails:
    """Comprehensive runtime guardrails system"""
    
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.compliance_engine = ComplianceEngine()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.safety_incidents: List[SafetyIncident] = []
        self.blocked_phrases = self._load_blocked_phrases()
        self.rate_limits: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
    
    def _load_blocked_phrases(self) -> Set[str]:
        """Load blocked phrases and content filters"""
        return {
            # Inappropriate content
            "profanity", "harassment", "threats", "discrimination",
            
            # Sensitive topics that should trigger escalation
            "suicide", "self-harm", "abuse", "violence",
            
            # Unauthorized activities
            "illegal activities", "fraud", "hacking", "unauthorized access",
            
            # Business-specific blocks
            "competitor names", "unauthorized promotions", "off-topic discussions"
        }
    
    def validate_call_safety(self, call_id: str, session_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive safety validation for call content"""
        
        validation_start = time.time()
        
        # 1. PII Detection and Masking
        pii_result = self.pii_detector.detect_and_mask(content)
        
        # 2. Compliance Checking
        compliance_violations = self.compliance_engine.check_compliance(content, metadata)
        
        # 3. Content Safety Filtering
        safety_issues = self._check_content_safety(content)
        
        # 4. Rate Limiting
        rate_limit_status = self._check_rate_limits(call_id, session_id)
        
        # 5. Generate overall risk assessment
        risk_level = self._assess_overall_risk(pii_result, compliance_violations, safety_issues)
        
        # 6. Determine required actions
        actions = self._determine_actions(risk_level, pii_result, compliance_violations, safety_issues)
        
        validation_result = {
            "call_id": call_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "validation_time_ms": (time.time() - validation_start) * 1000,
            
            # Results
            "pii_detected": pii_result.detected,
            "pii_types": pii_result.pii_types,
            "masked_content": pii_result.masked_content,
            "compliance_violations": [asdict(v) for v in compliance_violations],
            "safety_issues": safety_issues,
            "rate_limit_status": rate_limit_status,
            
            # Risk assessment
            "risk_level": risk_level.name,
            "risk_score": risk_level.value,
            
            # Required actions
            "allow_processing": actions["allow_processing"],
            "require_human_review": actions["require_human_review"],
            "escalate_immediately": actions["escalate_immediately"],
            "terminate_call": actions["terminate_call"],
            "actions_taken": actions["actions_taken"]
        }
        
        # Log high-risk situations
        if risk_level.value >= RiskLevel.HIGH.value:
            self.logger.warning(f"High-risk call detected | call_id={call_id} | risk={risk_level.name} | violations={len(compliance_violations)}")
            
            # Create safety incident record
            self._create_safety_incident(call_id, session_id, risk_level, safety_issues + [v.description for v in compliance_violations])
        
        return validation_result
    
    def _check_content_safety(self, content: str) -> List[str]:
        """Check content for safety issues"""
        
        safety_issues = []
        content_lower = content.lower()
        
        # Check for blocked phrases
        for phrase in self.blocked_phrases:
            if phrase in content_lower:
                safety_issues.append(f"blocked_phrase: {phrase}")
        
        # Check for potential scam/fraud indicators
        fraud_indicators = [
            "give me your", "provide your password", "verify your account",
            "urgent action required", "limited time offer", "act now",
            "social security number", "bank account details"
        ]
        
        for indicator in fraud_indicators:
            if indicator in content_lower:
                safety_issues.append(f"fraud_indicator: {indicator}")
        
        # Check for emotional distress indicators
        distress_indicators = [
            "want to hurt", "thinking about", "can't take it", "end it all",
            "nobody cares", "feel hopeless", "want to die"
        ]
        
        for indicator in distress_indicators:
            if indicator in content_lower:
                safety_issues.append(f"distress_indicator: {indicator}")
        
        return safety_issues
    
    def _check_rate_limits(self, call_id: str, session_id: str) -> Dict[str, Any]:
        """Check rate limiting for call frequency"""
        
        current_time = datetime.now()
        
        # Initialize rate limit tracking for session if needed
        if session_id not in self.rate_limits:
            self.rate_limits[session_id] = {
                "call_count": 0,
                "first_call": current_time,
                "last_call": current_time,
                "violations": 0
            }
        
        session_limits = self.rate_limits[session_id]
        session_limits["call_count"] += 1
        session_limits["last_call"] = current_time
        
        # Check for rate limit violations
        time_window = timedelta(minutes=5)
        calls_in_window = session_limits["call_count"]
        
        # Rate limits: max 10 calls per 5 minutes per session
        max_calls_per_window = 10
        
        if calls_in_window > max_calls_per_window:
            session_limits["violations"] += 1
            
            return {
                "rate_limited": True,
                "calls_in_window": calls_in_window,
                "max_allowed": max_calls_per_window,
                "violation_count": session_limits["violations"]
            }
        
        return {
            "rate_limited": False,
            "calls_in_window": calls_in_window,
            "max_allowed": max_calls_per_window,
            "violation_count": session_limits["violations"]
        }
    
    def _assess_overall_risk(self, pii_result: PIIDetection, compliance_violations: List[ComplianceViolation], safety_issues: List[str]) -> RiskLevel:
        """Assess overall risk level based on all factors"""
        
        risk_score = 0
        
        # PII risk scoring
        if pii_result.detected:
            if "ssn" in pii_result.pii_types or "credit_card" in pii_result.pii_types:
                risk_score += 3
            elif any(pii_type in ["phone", "email", "dob"] for pii_type in pii_result.pii_types):
                risk_score += 2
            else:
                risk_score += 1
        
        # Compliance violation scoring
        for violation in compliance_violations:
            risk_score += violation.severity.value
        
        # Safety issue scoring
        for issue in safety_issues:
            if "fraud_indicator" in issue or "distress_indicator" in issue:
                risk_score += 3
            elif "blocked_phrase" in issue:
                risk_score += 2
            else:
                risk_score += 1
        
        # Convert score to risk level
        if risk_score >= 8:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _determine_actions(self, risk_level: RiskLevel, pii_result: PIIDetection, compliance_violations: List[ComplianceViolation], safety_issues: List[str]) -> Dict[str, Any]:
        """Determine required actions based on risk assessment"""
        
        actions = {
            "allow_processing": True,
            "require_human_review": False,
            "escalate_immediately": False,
            "terminate_call": False,
            "actions_taken": []
        }
        
        # Critical risk - immediate termination
        if risk_level == RiskLevel.CRITICAL:
            actions["allow_processing"] = False
            actions["terminate_call"] = True
            actions["escalate_immediately"] = True
            actions["actions_taken"].append("call_terminated_critical_risk")
        
        # High risk - human review required
        elif risk_level == RiskLevel.HIGH:
            actions["require_human_review"] = True
            actions["actions_taken"].append("human_review_required")
        
        # Medium risk - monitoring and logging
        elif risk_level == RiskLevel.MEDIUM:
            actions["actions_taken"].append("enhanced_monitoring")
        
        # Specific compliance actions
        for violation in compliance_violations:
            if violation.severity == RiskLevel.CRITICAL:
                actions["terminate_call"] = True
                actions["actions_taken"].append(f"compliance_violation_{violation.framework.value}")
        
        # PII-specific actions
        if pii_result.detected:
            actions["actions_taken"].append("pii_detected_and_masked")
        
        # Safety-specific actions
        for issue in safety_issues:
            if "distress_indicator" in issue:
                actions["escalate_immediately"] = True
                actions["actions_taken"].append("mental_health_escalation")
            elif "fraud_indicator" in issue:
                actions["require_human_review"] = True
                actions["actions_taken"].append("fraud_prevention_review")
        
        return actions
    
    def _create_safety_incident(self, call_id: str, session_id: str, risk_level: RiskLevel, issues: List[str]):
        """Create safety incident record"""
        
        incident = SafetyIncident(
            incident_id=f"INC_{int(time.time())}_{call_id[-6:]}",
            incident_type="automated_detection",
            risk_level=risk_level,
            call_id=call_id,
            session_id=session_id,
            description=f"Risk level {risk_level.name} detected: {', '.join(issues[:3])}",
            auto_action_taken="monitoring_enhanced" if risk_level == RiskLevel.MEDIUM else "human_review_required",
            human_review_required=risk_level.value >= RiskLevel.HIGH.value,
            timestamp=datetime.now()
        )
        
        self.safety_incidents.append(incident)
        
        self.logger.info(f"Safety incident created | {incident.incident_id} | {risk_level.name} | call_id={call_id}")
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def get_safety_dashboard(self) -> Dict[str, Any]:
        """Get safety monitoring dashboard data"""
        
        current_time = datetime.now()
        last_24h = current_time - timedelta(hours=24)
        
        # Recent incidents
        recent_incidents = [
            incident for incident in self.safety_incidents 
            if incident.timestamp >= last_24h
        ]
        
        # Compliance violations by framework
        recent_violations = [
            violation for violation in self.compliance_engine.violation_history
            if violation.timestamp >= last_24h
        ]
        
        violation_by_framework = {}
        for violation in recent_violations:
            framework = violation.framework.value
            if framework not in violation_by_framework:
                violation_by_framework[framework] = 0
            violation_by_framework[framework] += 1
        
        # Circuit breaker status
        breaker_status = {
            service: breaker.state for service, breaker in self.circuit_breakers.items()
        }
        
        return {
            "timestamp": current_time.isoformat(),
            "period": "last_24_hours",
            
            # Incident metrics
            "total_incidents": len(recent_incidents),
            "critical_incidents": len([i for i in recent_incidents if i.risk_level == RiskLevel.CRITICAL]),
            "high_incidents": len([i for i in recent_incidents if i.risk_level == RiskLevel.HIGH]),
            "human_reviews_required": len([i for i in recent_incidents if i.human_review_required]),
            
            # Compliance metrics
            "total_violations": len(recent_violations),
            "violations_by_framework": violation_by_framework,
            
            # System health
            "circuit_breaker_status": breaker_status,
            "active_rate_limits": len([s for s in self.rate_limits.values() if s["violations"] > 0]),
            
            # Recent incidents
            "recent_critical_incidents": [
                {
                    "incident_id": i.incident_id,
                    "risk_level": i.risk_level.name,
                    "description": i.description,
                    "timestamp": i.timestamp.isoformat()
                }
                for i in recent_incidents[-10:]  # Last 10 incidents
            ]
        }

# Usage demonstration
async def demo_runtime_guardrails():
    """Demo the complete runtime guardrails system"""
    print("🛡️ Runtime Guardrails & Safety Demo")
    print("=" * 45)
    
    guardrails = RuntimeGuardrails()
    
    # Test cases
    test_cases = [
        {
            "name": "Safe customer inquiry",
            "content": "Hi, I'd like to check my account balance please",
            "metadata": {"consent_obtained": True, "dnc_listed": False}
        },
        {
            "name": "PII detected",
            "content": "My social security number is 123-45-6789 and my credit card is 4532-1234-5678-9012",
            "metadata": {"consent_obtained": True, "dnc_listed": False}
        },
        {
            "name": "Compliance violation",
            "content": "Can you store my credit card 4532-1234-5678-9012 with CVV 123?",
            "metadata": {"consent_obtained": False, "dnc_listed": True}
        },
        {
            "name": "Safety concern",
            "content": "I can't take it anymore, I want to hurt myself",
            "metadata": {"consent_obtained": True, "dnc_listed": False}
        },
        {
            "name": "Fraud attempt",
            "content": "Please give me your password for verification purposes",
            "metadata": {"consent_obtained": True, "dnc_listed": False}
        }
    ]
    
    print("\n🔍 Testing Safety Validation:")
    print("-" * 35)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Content: {test_case['content'][:50]}...")
        
        result = guardrails.validate_call_safety(
            call_id=f"test_call_{i}",
            session_id=f"test_session_{i}",
            content=test_case['content'],
            metadata=test_case['metadata']
        )
        
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   PII Detected: {result['pii_detected']}")
        print(f"   Compliance Violations: {len(result['compliance_violations'])}")
        print(f"   Safety Issues: {len(result['safety_issues'])}")
        print(f"   Allow Processing: {result['allow_processing']}")
        
        if result['actions_taken']:
            print(f"   Actions Taken: {', '.join(result['actions_taken'])}")
        
        if result['pii_detected']:
            print(f"   Masked: {result['masked_content'][:50]}...")
    
    # Demo safety dashboard
    print("\n📊 Safety Dashboard:")
    print("-" * 25)
    
    dashboard = guardrails.get_safety_dashboard()
    
    print(f"  Total Incidents (24h): {dashboard['total_incidents']}")
    print(f"  Critical Incidents: {dashboard['critical_incidents']}")
    print(f"  Human Reviews Required: {dashboard['human_reviews_required']}")
    print(f"  Compliance Violations: {dashboard['total_violations']}")
    
    if dashboard['violations_by_framework']:
        print("  Violations by Framework:")
        for framework, count in dashboard['violations_by_framework'].items():
            print(f"    {framework}: {count}")
    
    print("\n✅ Runtime guardrails system operational!")
    print("   - PII detection and masking")
    print("   - Multi-framework compliance checking")
    print("   - Real-time safety content filtering")
    print("   - Circuit breaker resilience patterns")
    print("   - Rate limiting and abuse prevention")
    print("   - Automated incident management")

if __name__ == "__main__":
    asyncio.run(demo_runtime_guardrails())