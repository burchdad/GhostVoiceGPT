"""
Production Telemetry & Observability System
Real-time monitoring for latency, quality, and performance
"""

import time
import uuid
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import statistics

@dataclass
class TurnTrace:
    """Complete trace for one conversation turn"""
    trace_id: str
    session_id: str
    turn_number: int
    timestamp: datetime
    
    # Timing breakdown (milliseconds)
    stt_start: Optional[float] = None
    stt_duration: Optional[float] = None
    stt_confidence: Optional[float] = None
    
    llm_start: Optional[float] = None
    llm_duration: Optional[float] = None
    llm_tokens_in: Optional[int] = None
    llm_tokens_out: Optional[int] = None
    
    tts_start: Optional[float] = None
    tts_duration: Optional[float] = None
    tts_voice_id: Optional[str] = None
    
    total_duration: Optional[float] = None
    
    # Quality metrics
    barge_in_detected: bool = False
    barge_in_successful: bool = False
    echo_detected: bool = False
    language_detected: Optional[str] = None
    language_switched: bool = False
    
    # Business metrics
    intent_detected: Optional[str] = None
    escalation_triggered: bool = False
    call_successful: bool = False
    
    # Error tracking
    errors: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class ProductionTelemetry:
    """Production-grade telemetry and alerting system"""
    
    def __init__(self):
        self.traces: Dict[str, TurnTrace] = {}
        self.session_metrics: Dict[str, Dict] = {}
        self.alert_thresholds = {
            "p95_total_latency_ms": 500,
            "max_leg_latency_ms": 250,
            "min_stt_confidence": 0.7,
            "max_error_rate_percent": 5.0,
            "min_barge_in_success_rate": 0.8
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup structured logging for production"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | trace_id=%(trace_id)s | %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('ghostvoice_production.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_turn(self, session_id: str, turn_number: int) -> str:
        """Start tracking a new conversation turn"""
        trace_id = str(uuid.uuid4())[:8]
        
        trace = TurnTrace(
            trace_id=trace_id,
            session_id=session_id,
            turn_number=turn_number,
            timestamp=datetime.now()
        )
        
        self.traces[trace_id] = trace
        
        self.logger.info(
            f"Turn started | session={session_id} | turn={turn_number}",
            extra={"trace_id": trace_id}
        )
        
        return trace_id
    
    def log_stt_start(self, trace_id: str):
        """Log STT processing start"""
        if trace_id in self.traces:
            self.traces[trace_id].stt_start = time.time() * 1000
    
    def log_stt_complete(self, trace_id: str, confidence: float, text: str, language: Optional[str] = None):
        """Log STT processing completion"""
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        if trace.stt_start:
            trace.stt_duration = (time.time() * 1000) - trace.stt_start
        trace.stt_confidence = confidence
        trace.language_detected = language
        
        self.logger.info(
            f"STT complete | duration={trace.stt_duration:.1f}ms | confidence={confidence:.3f} | text_length={len(text)}",
            extra={"trace_id": trace_id}
        )
        
        # Alert on low confidence
        if confidence < self.alert_thresholds["min_stt_confidence"]:
            self.alert(f"Low STT confidence: {confidence:.3f}", trace_id)
    
    def log_llm_start(self, trace_id: str):
        """Log LLM processing start"""
        if trace_id in self.traces:
            self.traces[trace_id].llm_start = time.time() * 1000
    
    def log_llm_complete(self, trace_id: str, tokens_in: int, tokens_out: int, intent: Optional[str] = None):
        """Log LLM processing completion"""
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        if trace.llm_start:
            trace.llm_duration = (time.time() * 1000) - trace.llm_start
        trace.llm_tokens_in = tokens_in
        trace.llm_tokens_out = tokens_out
        trace.intent_detected = intent
        
        self.logger.info(
            f"LLM complete | duration={trace.llm_duration:.1f}ms | tokens_in={tokens_in} | tokens_out={tokens_out} | intent={intent}",
            extra={"trace_id": trace_id}
        )
    
    def log_tts_start(self, trace_id: str, voice_id: str):
        """Log TTS processing start"""
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            trace.tts_start = time.time() * 1000
            trace.tts_voice_id = voice_id
    
    def log_tts_complete(self, trace_id: str, audio_duration_ms: int):
        """Log TTS processing completion"""
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        if trace.tts_start:
            trace.tts_duration = (time.time() * 1000) - trace.tts_start
        
        self.logger.info(
            f"TTS complete | duration={trace.tts_duration:.1f}ms | audio_duration={audio_duration_ms}ms | voice={trace.tts_voice_id}",
            extra={"trace_id": trace_id}
        )
    
    def log_barge_in(self, trace_id: str, successful: bool):
        """Log barge-in event"""
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            trace.barge_in_detected = True
            trace.barge_in_successful = successful
            
            self.logger.info(
                f"Barge-in | successful={successful}",
                extra={"trace_id": trace_id}
            )
    
    def log_language_switch(self, trace_id: str, from_lang: str, to_lang: str):
        """Log dynamic language switching"""
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            trace.language_switched = True
            
            self.logger.info(
                f"Language switch | from={from_lang} | to={to_lang}",
                extra={"trace_id": trace_id}
            )
    
    def log_error(self, trace_id: str, error: str, component: str):
        """Log error in processing pipeline"""
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            if trace.errors is None:
                trace.errors = []
            trace.errors.append(f"{component}: {error}")
        
        self.logger.error(
            f"Pipeline error | component={component} | error={error}",
            extra={"trace_id": trace_id}
        )
    
    def complete_turn(self, trace_id: str, successful: bool = True, escalated: bool = False):
        """Complete turn tracking and check alerts"""
        if trace_id not in self.traces:
            return
        
        trace = self.traces[trace_id]
        trace.call_successful = successful
        trace.escalation_triggered = escalated
        
        # Calculate total duration
        if trace.stt_start:
            trace.total_duration = (time.time() * 1000) - trace.stt_start
        
        self.logger.info(
            f"Turn complete | total_duration={trace.total_duration:.1f}ms | successful={successful} | escalated={escalated}",
            extra={"trace_id": trace_id}
        )
        
        # Check latency alerts
        self._check_latency_alerts(trace)
        
        # Update session metrics
        self._update_session_metrics(trace)
    
    def _check_latency_alerts(self, trace: TurnTrace):
        """Check if latency exceeds thresholds"""
        if trace.total_duration and trace.total_duration > self.alert_thresholds["p95_total_latency_ms"]:
            self.alert(f"High total latency: {trace.total_duration:.1f}ms", trace.trace_id)
        
        # Check individual leg latencies
        legs = [
            ("STT", trace.stt_duration),
            ("LLM", trace.llm_duration), 
            ("TTS", trace.tts_duration)
        ]
        
        for leg_name, duration in legs:
            if duration and duration > self.alert_thresholds["max_leg_latency_ms"]:
                self.alert(f"High {leg_name} latency: {duration:.1f}ms", trace.trace_id)
    
    def _update_session_metrics(self, trace: TurnTrace):
        """Update aggregated session metrics"""
        session_id = trace.session_id
        
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = {
                "turns": 0,
                "successful_turns": 0,
                "escalations": 0,
                "barge_ins": 0,
                "successful_barge_ins": 0,
                "latencies": [],
                "errors": []
            }
        
        metrics = self.session_metrics[session_id]
        metrics["turns"] += 1
        
        if trace.call_successful:
            metrics["successful_turns"] += 1
        
        if trace.escalation_triggered:
            metrics["escalations"] += 1
        
        if trace.barge_in_detected:
            metrics["barge_ins"] += 1
            if trace.barge_in_successful:
                metrics["successful_barge_ins"] += 1
        
        if trace.total_duration:
            metrics["latencies"].append(trace.total_duration)
        
        metrics["errors"].extend(trace.errors)
    
    def alert(self, message: str, trace_id: str):
        """Send production alert"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "message": message,
            "severity": "HIGH"
        }
        
        # Log alert
        self.logger.warning(
            f"ALERT | {message}",
            extra={"trace_id": trace_id}
        )
        
        # In production: send to PagerDuty, Slack, etc.
        # For now, just log to alert file
        with open("production_alerts.json", "a") as f:
            f.write(json.dumps(alert_data) + "\n")
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_traces = [
            trace for trace in self.traces.values() 
            if trace.timestamp > cutoff
        ]
        
        if not recent_traces:
            return {"error": "No recent traces found"}
        
        # Calculate metrics
        latencies = [t.total_duration for t in recent_traces if t.total_duration]
        error_count = sum(len(t.errors) if t.errors else 0 for t in recent_traces)
        barge_ins = [t for t in recent_traces if t.barge_in_detected]
        successful_barge_ins = [t for t in barge_ins if t.barge_in_successful]
        
        summary = {
            "time_window": f"Last {hours} hours",
            "total_turns": len(recent_traces),
            "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
            "p95_latency_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0,
            "p99_latency_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0,
            "error_rate_percent": (error_count / len(recent_traces)) * 100,
            "barge_in_success_rate": len(successful_barge_ins) / len(barge_ins) if barge_ins else 0,
            "escalation_rate": len([t for t in recent_traces if t.escalation_triggered]) / len(recent_traces),
            "languages_detected": list(set(t.language_detected for t in recent_traces if t.language_detected))
        }
        
        return summary
    
    def export_traces(self, session_id: Optional[str] = None) -> List[Dict]:
        """Export traces for analysis"""
        traces_to_export = self.traces.values()
        
        if session_id:
            traces_to_export = [t for t in traces_to_export if t.session_id == session_id]
        
        return [asdict(trace) for trace in traces_to_export]

# Global telemetry instance
telemetry = ProductionTelemetry()

# Usage example decorators
def trace_stt(func):
    """Decorator to trace STT operations"""
    async def wrapper(*args, **kwargs):
        trace_id = kwargs.get('trace_id')
        if trace_id:
            telemetry.log_stt_start(trace_id)
        
        try:
            result = await func(*args, **kwargs)
            if trace_id and hasattr(result, 'confidence'):
                telemetry.log_stt_complete(trace_id, result.confidence, result.text)
            return result
        except Exception as e:
            if trace_id:
                telemetry.log_error(trace_id, str(e), "STT")
            raise
    
    return wrapper

def trace_llm(func):
    """Decorator to trace LLM operations"""
    async def wrapper(*args, **kwargs):
        trace_id = kwargs.get('trace_id')
        if trace_id:
            telemetry.log_llm_start(trace_id)
        
        try:
            result = await func(*args, **kwargs)
            if trace_id:
                telemetry.log_llm_complete(
                    trace_id, 
                    kwargs.get('tokens_in', 0),
                    len(result.split()) if isinstance(result, str) else 0
                )
            return result
        except Exception as e:
            if trace_id:
                telemetry.log_error(trace_id, str(e), "LLM")
            raise
    
    return wrapper

def trace_tts(func):
    """Decorator to trace TTS operations"""
    async def wrapper(*args, **kwargs):
        trace_id = kwargs.get('trace_id')
        voice_id = kwargs.get('voice_id', 'unknown')
        
        if trace_id:
            telemetry.log_tts_start(trace_id, voice_id)
        
        try:
            result = await func(*args, **kwargs)
            if trace_id:
                # Estimate audio duration (rough calculation)
                audio_duration = int(len(result) / 16000 * 1000) if result else 0
                telemetry.log_tts_complete(trace_id, audio_duration)
            return result
        except Exception as e:
            if trace_id:
                telemetry.log_error(trace_id, str(e), "TTS")
            raise
    
    return wrapper

if __name__ == "__main__":
    # Demo usage
    print("🔍 Production Telemetry System Demo")
    print("=" * 50)
    
    # Simulate a conversation turn
    trace_id = telemetry.start_turn("session_123", 1)
    
    # Simulate processing pipeline
    time.sleep(0.1)  # STT processing
    telemetry.log_stt_complete(trace_id, 0.95, "Hello, I need help with my account", "en-US")
    
    time.sleep(0.2)  # LLM processing  
    telemetry.log_llm_complete(trace_id, 150, 75, "account_inquiry")
    
    time.sleep(0.15)  # TTS processing
    telemetry.log_tts_complete(trace_id, 2500)
    
    telemetry.complete_turn(trace_id, successful=True)
    
    # Show performance summary
    summary = telemetry.get_performance_summary()
    print("\n📊 Performance Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Telemetry system ready for production!")
    print("   - Real-time latency monitoring")
    print("   - Automatic alerting on thresholds")
    print("   - Trace-based debugging")
    print("   - Performance analytics")