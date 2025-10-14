"""
Advanced Production Metrics & Dashboard System
Real-time monitoring with Prometheus-style metrics and alerting
"""

import time
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import threading
import logging

@dataclass
class MetricPoint:
    """Single metric measurement"""
    timestamp: datetime
    value: float
    labels: Dict[str, str]

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    duration_minutes: int
    severity: str
    enabled: bool = True

class MetricsCollector:
    """High-performance metrics collection system"""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque())
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.retention_hours = retention_hours
        self.alert_rules: List[AlertRule] = []
        self.alert_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        
        # Start background cleanup task
        self._start_cleanup_task()
        
        # Initialize standard alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default production alert rules"""
        default_alerts = [
            AlertRule("high_latency", "response_time_ms", "gt", 500, 5, "warning"),
            AlertRule("error_rate", "error_rate_percent", "gt", 5.0, 3, "critical"),
            AlertRule("low_success_rate", "success_rate_percent", "lt", 95.0, 10, "warning"),
            AlertRule("high_memory", "memory_usage_percent", "gt", 80.0, 15, "warning"),
            AlertRule("pii_incidents", "pii_detections_per_hour", "gt", 10, 1, "critical"),
            AlertRule("compliance_violations", "compliance_violations_per_hour", "gt", 1, 1, "critical")
        ]
        
        for alert in default_alerts:
            self.add_alert_rule(alert)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = self._make_key(name, labels or {})
        self.counters[key] += value
        self._record_metric(name, value, labels or {})
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        key = self._make_key(name, labels or {})
        self.gauges[key] = value
        self._record_metric(name, value, labels or {})
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram observation"""
        key = self._make_key(name, labels or {})
        self.histograms[key].append(value)
        self._record_metric(name, value, labels or {})
        
        # Keep histogram buckets manageable
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-500:]
    
    def _record_metric(self, name: str, value: float, labels: Dict[str, str]):
        """Record metric point with timestamp"""
        metric_point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=labels
        )
        
        self.metrics[name].append(metric_point)
        
        # Check alert rules
        self._check_alert_rules(name)
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create unique key for metric with labels"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}" if label_str else name
    
    def get_metric_summary(self, name: str, hours: int = 1) -> Dict[str, Any]:
        """Get comprehensive metric summary"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        if name not in self.metrics:
            return {"error": f"Metric '{name}' not found"}
        
        recent_points = [
            point for point in self.metrics[name]
            if point.timestamp > cutoff
        ]
        
        if not recent_points:
            return {"error": f"No recent data for '{name}'"}
        
        values = [point.value for point in recent_points]
        
        summary = {
            "metric_name": name,
            "time_window_hours": hours,
            "data_points": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
            "latest": values[-1] if values else 0,
            "trend": self._calculate_trend(values)
        }
        
        # Add percentiles if enough data
        if len(values) >= 10:
            summary.update({
                "p50": statistics.quantiles(values, n=2)[0],
                "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
            })
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 5:
            return "insufficient_data"
        
        # Compare first and last quarters
        quarter = len(values) // 4
        first_quarter_avg = statistics.mean(values[:quarter])
        last_quarter_avg = statistics.mean(values[-quarter:])
        
        change_percent = ((last_quarter_avg - first_quarter_avg) / first_quarter_avg) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def add_alert_rule(self, rule: AlertRule):
        """Add new alert rule"""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def _check_alert_rules(self, metric_name: str):
        """Check if any alert rules are triggered"""
        for rule in self.alert_rules:
            if not rule.enabled or rule.metric_name != metric_name:
                continue
            
            # Get recent values for the rule duration
            cutoff = datetime.now() - timedelta(minutes=rule.duration_minutes)
            recent_points = [
                point for point in self.metrics[metric_name]
                if point.timestamp > cutoff
            ]
            
            if not recent_points:
                continue
            
            values = [point.value for point in recent_points]
            avg_value = statistics.mean(values)
            
            # Check condition
            triggered = False
            if rule.condition == "gt" and avg_value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and avg_value < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and abs(avg_value - rule.threshold) < 0.01:
                triggered = True
            
            if triggered:
                self._fire_alert(rule, avg_value, values)
    
    def _fire_alert(self, rule: AlertRule, current_value: float, recent_values: List[float]):
        """Fire an alert"""
        alert = {
            "rule_name": rule.name,
            "metric_name": rule.metric_name,
            "severity": rule.severity,
            "threshold": rule.threshold,
            "current_value": current_value,
            "condition": rule.condition,
            "duration_minutes": rule.duration_minutes,
            "data_points": len(recent_values),
            "timestamp": datetime.now().isoformat(),
            "alert_id": f"{rule.name}_{int(time.time())}"
        }
        
        self.alert_history.append(alert)
        
        # Log alert
        self.logger.warning(
            f"ALERT FIRED: {rule.name} | {rule.metric_name} {rule.condition} {rule.threshold} | current: {current_value:.2f}",
            extra=alert
        )
        
        # In production: send to PagerDuty, Slack, email, etc.
        self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification (placeholder for integrations)"""
        # Placeholder for external alerting integrations
        # - PagerDuty API
        # - Slack webhooks
        # - Email notifications
        # - SMS alerts
        print(f"🚨 ALERT: {alert['rule_name']} - {alert['metric_name']} = {alert['current_value']:.2f}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = datetime.now()
        
        # System overview
        system_metrics = {
            "timestamp": current_time.isoformat(),
            "uptime": "operational",
            "active_metrics": len(self.metrics),
            "total_data_points": sum(len(points) for points in self.metrics.values()),
            "memory_usage": self._estimate_memory_usage()
        }
        
        # Key performance indicators
        kpis = {}
        key_metrics = [
            "response_time_ms", "error_rate_percent", "success_rate_percent",
            "calls_per_minute", "pii_detections_per_hour", "compliance_violations_per_hour"
        ]
        
        for metric in key_metrics:
            summary = self.get_metric_summary(metric, hours=1)
            if "error" not in summary:
                kpis[metric] = summary
        
        # Recent alerts
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > current_time - timedelta(hours=24)
        ]
        
        # Alert statistics
        alert_stats = {
            "total_alerts_24h": len(recent_alerts),
            "critical_alerts": len([a for a in recent_alerts if a["severity"] == "critical"]),
            "warning_alerts": len([a for a in recent_alerts if a["severity"] == "warning"]),
            "active_rules": len([r for r in self.alert_rules if r.enabled])
        }
        
        return {
            "system": system_metrics,
            "kpis": kpis,
            "alerts": {
                "recent": recent_alerts[-10:],  # Last 10 alerts
                "statistics": alert_stats
            },
            "health_status": self._get_health_status()
        }
    
    def _estimate_memory_usage(self) -> str:
        """Estimate memory usage of metrics storage"""
        total_points = sum(len(points) for points in self.metrics.values())
        estimated_mb = (total_points * 100) / (1024 * 1024)  # Rough estimate
        return f"{estimated_mb:.1f}MB"
    
    def _get_health_status(self) -> str:
        """Determine overall system health"""
        # Check for recent critical alerts
        cutoff = datetime.now() - timedelta(minutes=15)
        recent_critical = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
            and alert["severity"] == "critical"
        ]
        
        if recent_critical:
            return "critical"
        
        # Check for warning alerts
        recent_warnings = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
            and alert["severity"] == "warning"
        ]
        
        if len(recent_warnings) > 3:
            return "degraded"
        
        return "healthy"
    
    def _start_cleanup_task(self):
        """Start background task to clean old metrics"""
        def cleanup_worker():
            while True:
                try:
                    cutoff = datetime.now() - timedelta(hours=self.retention_hours)
                    
                    for metric_name in list(self.metrics.keys()):
                        # Remove old points
                        while (self.metrics[metric_name] and 
                               self.metrics[metric_name][0].timestamp < cutoff):
                            self.metrics[metric_name].popleft()
                    
                    # Clean old alerts
                    alert_cutoff = datetime.now() - timedelta(days=7)
                    self.alert_history = [
                        alert for alert in self.alert_history
                        if datetime.fromisoformat(alert["timestamp"]) > alert_cutoff
                    ]
                    
                    time.sleep(300)  # Clean every 5 minutes
                    
                except Exception as e:
                    self.logger.error(f"Metrics cleanup error: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

# Global metrics instance
metrics_collector = MetricsCollector()

# Convenience functions for common metrics
def track_call_latency(duration_ms: float, voice_id: str = "", success: bool = True):
    """Track call processing latency"""
    metrics_collector.observe_histogram("response_time_ms", duration_ms, {
        "voice_id": voice_id,
        "success": str(success)
    })

def track_error(error_type: str, component: str = ""):
    """Track error occurrence"""
    metrics_collector.increment_counter("errors_total", labels={
        "error_type": error_type,
        "component": component
    })

def track_pii_detection():
    """Track PII detection event"""
    metrics_collector.increment_counter("pii_detections_total")

def track_compliance_violation(framework: str):
    """Track compliance violation"""
    metrics_collector.increment_counter("compliance_violations_total", labels={
        "framework": framework
    })

if __name__ == "__main__":
    print("📊 Advanced Metrics & Dashboard System Demo")
    print("=" * 50)
    
    # Simulate some metrics
    import random
    
    for i in range(100):
        # Simulate response times
        latency = random.gauss(300, 100)  # 300ms average
        track_call_latency(latency, voice_id="adam", success=latency < 500)
        
        # Simulate occasional errors
        if random.random() < 0.05:  # 5% error rate
            track_error("timeout", "tts_service")
        
        # Simulate PII detections
        if random.random() < 0.02:  # 2% PII detection rate
            track_pii_detection()
    
    # Get dashboard data
    dashboard = metrics_collector.get_dashboard_data()
    
    print(f"System Status: {dashboard['health_status'].upper()}")
    print(f"Active Metrics: {dashboard['system']['active_metrics']}")
    print(f"Total Data Points: {dashboard['system']['total_data_points']}")
    print(f"Memory Usage: {dashboard['system']['memory_usage']}")
    
    if dashboard['kpis']:
        print("\nKey Performance Indicators:")
        for metric, summary in dashboard['kpis'].items():
            if "error" not in summary:
                print(f"  {metric}: {summary['avg']:.1f} (trend: {summary['trend']})")
    
    print(f"\nAlerts (24h): {dashboard['alerts']['statistics']['total_alerts_24h']}")
    print(f"Critical: {dashboard['alerts']['statistics']['critical_alerts']}")
    print(f"Warning: {dashboard['alerts']['statistics']['warning_alerts']}")
    
    print("\n✅ Advanced monitoring system operational!")
    print("   - Real-time metrics collection")
    print("   - Automated alerting rules")
    print("   - Performance trend analysis") 
    print("   - Production dashboard")
    print("   - Alert history tracking")