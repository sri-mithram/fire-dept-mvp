"""

Pydantic models for API request/response validation

"""
from pydantic import BaseModel, Field

from typing import List, Optional

from datetime import datetime

class TranscriptEntry(BaseModel):

    """Single transcript entry"""

    timestamp: datetime

    channel: str

    channel_id: str

    text: str

    duration: float

    confidence: Optional[float] = None

    is_alert: bool = False

    alert_keywords: List[str] = []

    alert_priority: str = "NORMAL"

class AlertEntry(BaseModel):

    """Alert entry"""

    timestamp: datetime

    channel: str

    text: str

    keywords: List[str]

    priority: str

    formatted: str

class ChannelStatus(BaseModel):

    """Channel status"""

    name: str

    enabled: bool

    is_active: bool

    frequency: str

    last_transmission: Optional[datetime] = None

    transmission_count: int = 0

class SystemStatus(BaseModel):

    """Overall system status"""

    is_running: bool

    channels: dict

    uptime: float

    total_transmissions: int

class WebSocketMessage(BaseModel):

    """WebSocket message format"""

    type: str  # "transcript", "alert", "status", "error"

    data: dict

    timestamp: datetime = Field(default_factory=datetime.now)

class TranscriptQuery(BaseModel):

    """Query parameters for transcript retrieval"""

    date: Optional[str] = None

    channel: Optional[str] = None

    limit: Optional[int] = 100

    offset: Optional[int] = 0

class AlertQuery(BaseModel):

    """Query parameters for alert retrieval"""

    date: Optional[str] = None

    priority: Optional[str] = None

    limit: Optional[int] = 100

    offset: Optional[int] = 0

