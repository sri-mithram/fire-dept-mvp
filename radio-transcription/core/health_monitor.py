"""
Health Monitor

Manages real-time health data from wearable devices
Supports multiple data sources and real-time streaming
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import asyncio

from utils.logger import log
import config


class HealthDataPoint:
    """Represents a single health data point"""
    
    def __init__(self, value: float, timestamp: datetime, source: str, data_type: str):
        self.value = value
        self.timestamp = timestamp
        self.source = source
        self.data_type = data_type  # 'heart_rate', 'oxygen', 'temperature', etc.


class HealthMonitor:
    """
    Monitors real-time health data from multiple sources
    """
    
    def __init__(self):
        self.heart_rate_data: deque = deque(maxlen=1000)  # Last 1000 readings
        self.oxygen_data: deque = deque(maxlen=1000)
        self.temperature_data: deque = deque(maxlen=1000)
        
        # Current values
        self.current_heart_rate: Optional[float] = None
        self.current_oxygen: Optional[float] = None
        self.current_temperature: Optional[float] = None
        
        # Statistics
        self.stats_window = timedelta(minutes=30)  # 30-minute window for stats
        
        # Callbacks for real-time updates
        self.update_callbacks: List[callable] = []
        
        log.info("Health monitor initialized")
    
    def add_data_point(self, data_type: str, value: float, source: str = "unknown", timestamp: Optional[datetime] = None):
        """
        Add a new health data point
        
        Args:
            data_type: Type of data ('heart_rate', 'oxygen', 'temperature')
            value: The measurement value
            source: Source device name
            timestamp: When the measurement was taken (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        data_point = HealthDataPoint(value, timestamp, source, data_type)
        
        # Store in appropriate deque
        if data_type == 'heart_rate':
            self.heart_rate_data.append(data_point)
            self.current_heart_rate = value
        elif data_type == 'oxygen':
            self.oxygen_data.append(data_point)
            self.current_oxygen = value
        elif data_type == 'temperature':
            self.temperature_data.append(data_point)
            self.current_temperature = value
        
        # Notify callbacks
        self._notify_callbacks(data_type, value, timestamp, source)
        
        log.debug(f"Health data added: {data_type}={value} from {source}")
    
    def add_callbacks(self, callback: callable):
        """Add callback for real-time updates"""
        self.update_callbacks.append(callback)
    
    def _notify_callbacks(self, data_type: str, value: float, timestamp: datetime, source: str):
        """Notify all registered callbacks"""
        for callback in self.update_callbacks:
            try:
                callback({
                    'type': data_type,
                    'value': value,
                    'timestamp': timestamp.isoformat(),
                    'source': source
                })
            except Exception as e:
                log.error(f"Error in health callback: {e}")
    
    def get_current_stats(self) -> Dict:
        """Get current health statistics"""
        now = datetime.now()
        cutoff = now - self.stats_window
        
        # Filter data within window
        hr_recent = [dp for dp in self.heart_rate_data if dp.timestamp >= cutoff]
        o2_recent = [dp for dp in self.oxygen_data if dp.timestamp >= cutoff]
        
        stats = {
            'heart_rate': {
                'current': self.current_heart_rate,
                'average': None,
                'min': None,
                'max': None,
                'count': len(hr_recent)
            },
            'oxygen': {
                'current': self.current_oxygen,
                'average': None,
                'min': None,
                'max': None,
                'count': len(o2_recent)
            }
        }
        
        if hr_recent:
            values = [dp.value for dp in hr_recent]
            stats['heart_rate']['average'] = sum(values) / len(values)
            stats['heart_rate']['min'] = min(values)
            stats['heart_rate']['max'] = max(values)
        
        if o2_recent:
            values = [dp.value for dp in o2_recent]
            stats['oxygen']['average'] = sum(values) / len(values)
            stats['oxygen']['min'] = min(values)
            stats['oxygen']['max'] = max(values)
        
        return stats
    
    def get_recent_data(self, data_type: str, minutes: int = 60) -> List[Dict]:
        """Get recent data points within specified time window"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        if data_type == 'heart_rate':
            data = self.heart_rate_data
        elif data_type == 'oxygen':
            data = self.oxygen_data
        elif data_type == 'temperature':
            data = self.temperature_data
        else:
            return []
        
        recent = [dp for dp in data if dp.timestamp >= cutoff]
        
        return [{
            'value': dp.value,
            'timestamp': dp.timestamp.isoformat(),
            'source': dp.source
        } for dp in recent]


