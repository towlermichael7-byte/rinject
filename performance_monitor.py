"""
Performance monitoring module for Resume Customizer application.
Tracks metrics, system resources, and application performance.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import streamlit as st

# Try to import psutil, fall back to basic monitoring if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from logger import get_logger

logger = get_logger()


@dataclass
class PerformanceMetric:
    """Individual performance metric data."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: datetime
    available: bool = True  # Indicates if metrics are available


class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.system_metrics = deque(maxlen=max_history)
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, unit: str = "", **metadata):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        with self._lock:
            self.metrics[name].append(metric)
        
        logger.debug(f"Recorded metric: {name} = {value} {unit}")
    
    def record_system_metrics(self):
        """Record current system metrics."""
        try:
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_metric = SystemMetrics(
                    cpu_percent=psutil.cpu_percent(interval=0.1),
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    memory_available_mb=memory.available / (1024 * 1024),
                    disk_usage_percent=disk.percent,
                    timestamp=datetime.now(),
                    available=True
                )
            else:
                # Fallback metrics when psutil is not available
                system_metric = SystemMetrics(
                    cpu_percent=0.0,
                    memory_percent=0.0,
                    memory_used_mb=0.0,
                    memory_available_mb=0.0,
                    disk_usage_percent=0.0,
                    timestamp=datetime.now(),
                    available=False
                )
            
            with self._lock:
                self.system_metrics.append(system_metric)
                
        except Exception as e:
            logger.error("Failed to collect system metrics", exception=e)
    
    def get_metrics(self, name: str, limit: int = 100) -> List[PerformanceMetric]:
        """Get recent metrics for a specific name."""
        with self._lock:
            return list(self.metrics[name])[-limit:]
    
    def get_system_metrics(self, limit: int = 100) -> List[SystemMetrics]:
        """Get recent system metrics."""
        with self._lock:
            return list(self.system_metrics)[-limit:]
    
    def get_metric_summary(self, name: str) -> Dict[str, float]:
        """Get statistical summary of a metric."""
        metrics = self.get_metrics(name)
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1] if values else 0
        }


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, collector: MetricsCollector, **metadata):
        self.operation_name = operation_name
        self.collector = collector
        self.metadata = metadata
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting timer for: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Record the timing metric
        self.collector.record_metric(
            f"{self.operation_name}_duration",
            duration,
            "seconds",
            **self.metadata
        )
        
        # Record success/failure
        success = exc_type is None
        self.collector.record_metric(
            f"{self.operation_name}_success",
            1 if success else 0,
            "boolean",
            **self.metadata
        )
        
        logger.info(f"Operation '{self.operation_name}' completed in {duration:.2f}s (Success: {success})")


class ThroughputTracker:
    """Tracks throughput metrics for operations."""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # seconds
        self.operations = defaultdict(lambda: deque())
        self._lock = threading.Lock()
    
    def record_operation(self, operation_type: str, count: int = 1):
        """Record completed operations."""
        now = datetime.now()
        
        with self._lock:
            self.operations[operation_type].append((now, count))
            self._cleanup_old_entries(operation_type, now)
    
    def get_throughput(self, operation_type: str) -> float:
        """Get current throughput (operations per second)."""
        now = datetime.now()
        
        with self._lock:
            self._cleanup_old_entries(operation_type, now)
            
            if not self.operations[operation_type]:
                return 0.0
            
            total_operations = sum(count for _, count in self.operations[operation_type])
            return total_operations / self.window_size
    
    def _cleanup_old_entries(self, operation_type: str, current_time: datetime):
        """Remove entries older than the window size."""
        cutoff = current_time - timedelta(seconds=self.window_size)
        
        while (self.operations[operation_type] and 
               self.operations[operation_type][0][0] < cutoff):
            self.operations[operation_type].popleft()


class PerformanceMonitor:
    """Main performance monitoring class."""
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.throughput_tracker = ThroughputTracker()
        self.monitoring_active = False
        self.monitor_thread = None
        self._stop_event = threading.Event()
    
    def start_monitoring(self, interval: float = 60.0):  # Increased interval to reduce overhead
        """Start background system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self._stop_event.clear()
        
        def monitor_loop():
            while not self._stop_event.wait(interval):
                try:
                    # Only monitor if memory usage is reasonable
                    if PSUTIL_AVAILABLE:
                        memory = psutil.virtual_memory()
                        if memory.percent < 95:  # Skip monitoring if memory is critically high
                            self.collector.record_system_metrics()
                        else:
                            logger.warning("Skipping system metrics collection due to high memory usage")
                    else:
                        self.collector.record_system_metrics()
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance monitoring started with memory-aware collection")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self._stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Performance monitoring stopped")
    
    def time_operation(self, operation_name: str, **metadata) -> PerformanceTimer:
        """Get a timer context manager for an operation."""
        return PerformanceTimer(operation_name, self.collector, **metadata)
    
    def record_processing_metrics(self, operation: str, files_processed: int, duration: float):
        """Record metrics for file processing operations."""
        self.collector.record_metric(f"{operation}_files_processed", files_processed, "files")
        self.collector.record_metric(f"{operation}_duration", duration, "seconds")
        
        if duration > 0:
            throughput = files_processed / duration
            self.collector.record_metric(f"{operation}_throughput", throughput, "files/second")
        
        self.throughput_tracker.record_operation(operation, files_processed)
    
    def record_email_metrics(self, emails_sent: int, emails_failed: int, duration: float):
        """Record email sending metrics."""
        self.collector.record_metric("emails_sent", emails_sent, "emails")
        self.collector.record_metric("emails_failed", emails_failed, "emails")
        self.collector.record_metric("email_duration", duration, "seconds")
        
        success_rate = emails_sent / (emails_sent + emails_failed) if (emails_sent + emails_failed) > 0 else 0
        self.collector.record_metric("email_success_rate", success_rate, "percentage")
        
        self.throughput_tracker.record_operation("email_sending", emails_sent)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            'system': self._get_system_summary(),
            'operations': self._get_operations_summary(),
            'throughput': self._get_throughput_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def _get_system_summary(self) -> Dict[str, Any]:
        """Get system metrics summary."""
        recent_metrics = self.collector.get_system_metrics(limit=10)
        
        if not recent_metrics or not PSUTIL_AVAILABLE:
            return {}
        
        # Filter out unavailable metrics
        available_metrics = [m for m in recent_metrics if m.available]
        if not available_metrics:
            return {}
        
        latest = available_metrics[-1]
        avg_cpu = sum(m.cpu_percent for m in available_metrics) / len(available_metrics)
        avg_memory = sum(m.memory_percent for m in available_metrics) / len(available_metrics)
        
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_used_mb': latest.memory_used_mb,
            'disk_usage_percent': latest.disk_usage_percent,
            'avg_cpu_percent': avg_cpu,
            'avg_memory_percent': avg_memory
        }
    
    def _get_operations_summary(self) -> Dict[str, Dict[str, float]]:
        """Get operations metrics summary."""
        operations = [
            'resume_processing', 'email_sending', 'file_upload',
            'preview_generation', 'bulk_processing'
        ]
        
        summary = {}
        for op in operations:
            duration_summary = self.collector.get_metric_summary(f"{op}_duration")
            success_summary = self.collector.get_metric_summary(f"{op}_success")
            
            if duration_summary or success_summary:
                summary[op] = {
                    **duration_summary,
                    'success_rate': success_summary.get('avg', 0) * 100 if success_summary else 0
                }
        
        return summary
    
    def _get_throughput_summary(self) -> Dict[str, float]:
        """Get throughput metrics summary."""
        return {
            'resume_processing': self.throughput_tracker.get_throughput('resume_processing'),
            'email_sending': self.throughput_tracker.get_throughput('email_sending'),
            'file_upload': self.throughput_tracker.get_throughput('file_upload')
        }


def performance_decorator(operation_name: str, **metadata):
    """Decorator to automatically time and track function performance."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            
            with monitor.time_operation(operation_name, **metadata):
                result = func(*args, **kwargs)
            
            return result
        
        return wrapper
    return decorator


def display_performance_metrics():
    """Display performance metrics in Streamlit sidebar."""
    try:
        monitor = get_performance_monitor()
        
        with st.sidebar:
            if st.checkbox("Show Performance Metrics", value=False):
                st.subheader("📊 Performance Dashboard")
                
                if not PSUTIL_AVAILABLE:
                    st.info("ℹ️ System metrics unavailable (psutil not installed)")
                
                summary = monitor.get_performance_summary()
                
                # System metrics (only if psutil is available)
                if summary.get('system') and PSUTIL_AVAILABLE:
                    st.markdown("**System Resources:**")
                    sys_metrics = summary['system']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("CPU", f"{sys_metrics.get('cpu_percent', 0):.1f}%")
                        st.metric("Memory", f"{sys_metrics.get('memory_percent', 0):.1f}%")
                    
                    with col2:
                        st.metric("Memory Used", f"{sys_metrics.get('memory_used_mb', 0):.0f}MB")
                        st.metric("Disk Usage", f"{sys_metrics.get('disk_usage_percent', 0):.1f}%")
                
                # Throughput metrics
                if summary.get('throughput'):
                    st.markdown("**Throughput:**")
                    throughput = summary['throughput']
                    
                    for operation, rate in throughput.items():
                        if rate > 0:
                            st.metric(operation.replace('_', ' ').title(), f"{rate:.2f}/s")
                
                # Operations summary
                if summary.get('operations'):
                    st.markdown("**Operations:**")
                    for op_name, metrics in summary['operations'].items():
                        if metrics.get('count', 0) > 0:
                            with st.expander(f"{op_name.replace('_', ' ').title()}"):
                                st.write(f"Average Duration: {metrics.get('avg', 0):.2f}s")
                                st.write(f"Success Rate: {metrics.get('success_rate', 0):.1f}%")
                                st.write(f"Total Operations: {metrics.get('count', 0)}")
                
    except Exception as e:
        logger.error("Failed to display performance metrics", exception=e)


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        _performance_monitor.start_monitoring()
    return _performance_monitor


def cleanup_performance_monitor():
    """Cleanup performance monitor resources."""
    global _performance_monitor
    if _performance_monitor:
        try:
            _performance_monitor.stop_monitoring()
            logger.info("Performance monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping performance monitor: {e}")
        finally:
            _performance_monitor = None
