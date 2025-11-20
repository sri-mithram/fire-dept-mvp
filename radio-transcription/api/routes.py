"""
REST API routes for frontend integration

Provides endpoints for querying transcripts, alerts, and system status

"""



from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from typing import List, Optional

from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET



from api.models import (

    TranscriptEntry, AlertEntry, ChannelStatus, 

    SystemStatus, TranscriptQuery, AlertQuery

)

from utils.storage import get_transcripts, get_alerts

from utils.logger import log



# Create router

router = APIRouter()





@router.get("/health")

async def health_check():

    """Health check endpoint"""

    return {

        "status": "healthy",

        "timestamp": datetime.now().isoformat(),

        "service": "radio-transcription-backend"

    }





@router.get("/channels", response_model=dict)

async def get_channels():

    """

    Get all configured channels

    

    Returns:

        Dictionary of channel configurations

    """

    from core.channel_manager import ChannelManager

    

    # Note: In production, you'd get this from a shared instance

    # For now, we'll return config

    import config

    

    channels = {}

    for channel_id, channel_config in config.RADIO_CHANNELS.items():

        channels[channel_id] = {

            "name": channel_config["name"],

            "frequency": channel_config.get("frequency", "Unknown"),

            "color": channel_config.get("color", "⚪"),

            "priority": channel_config.get("priority", "MEDIUM"),

            "enabled": channel_config.get("enabled", True)

        }

    

    return channels





@router.get("/transcripts", response_model=List[dict])

async def get_transcripts_endpoint(

    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),

    channel: Optional[str] = Query(None, description="Filter by channel name"),

    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),

    offset: int = Query(0, ge=0, description="Offset for pagination")

):

    """

    Get transcripts with optional filtering

    

    Args:

        date: Filter by date (YYYY-MM-DD), defaults to today

        channel: Filter by channel name

        limit: Maximum results to return

        offset: Pagination offset

    

    Returns:

        List of transcript entries

    """

    

    try:

        # Get transcripts from storage

        transcripts = await get_transcripts(date=date, channel=channel)

        

        # Apply pagination

        paginated = transcripts[offset:offset + limit]

        

        log.info(f"Retrieved {len(paginated)} transcripts (total: {len(transcripts)})")

        

        return paginated

        

    except Exception as e:

        log.error(f"Error retrieving transcripts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/transcripts/recent", response_model=List[dict])

async def get_recent_transcripts(

    minutes: int = Query(60, ge=1, le=1440, description="Minutes to look back"),

    channel: Optional[str] = Query(None, description="Filter by channel name")

):

    """

    Get recent transcripts from the last N minutes

    

    Args:

        minutes: How many minutes to look back

        channel: Optional channel filter

    

    Returns:

        List of recent transcript entries

    """

    

    try:

        # Get today's transcripts

        transcripts = await get_transcripts(channel=channel)

        

        # Filter by time

        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        recent = [

            t for t in transcripts 

            if datetime.fromisoformat(t["timestamp"]) > cutoff_time

        ]

        

        log.info(f"Retrieved {len(recent)} transcripts from last {minutes} minutes")

        

        return recent

        

    except Exception as e:

        log.error(f"Error retrieving recent transcripts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/alerts", response_model=List[dict])

async def get_alerts_endpoint(

    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),

    priority: Optional[str] = Query(None, description="Filter by priority (LOW/MEDIUM/HIGH/CRITICAL)"),

    limit: int = Query(100, ge=1, le=1000),

    offset: int = Query(0, ge=0)

):

    """

    Get alerts with optional filtering

    

    Args:

        date: Filter by date (YYYY-MM-DD), defaults to today

        priority: Filter by priority level

        limit: Maximum results to return

        offset: Pagination offset

    

    Returns:

        List of alert entries

    """

    

    try:

        # Validate priority if provided

        if priority and priority not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:

            raise HTTPException(

                status_code=400, 

                detail="Priority must be one of: LOW, MEDIUM, HIGH, CRITICAL"

            )

        

        # Get alerts from storage

        alerts = await get_alerts(date=date, priority=priority)

        

        # Apply pagination

        paginated = alerts[offset:offset + limit]

        

        log.info(f"Retrieved {len(paginated)} alerts (total: {len(alerts)})")

        

        return paginated

        

    except HTTPException:

        raise

    except Exception as e:

        log.error(f"Error retrieving alerts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/alerts/critical", response_model=List[dict])

async def get_critical_alerts(

    hours: int = Query(24, ge=1, le=168, description="Hours to look back")

):

    """

    Get all critical alerts from the last N hours

    

    Args:

        hours: How many hours to look back

    

    Returns:

        List of critical alert entries

    """

    

    try:

        # Get alerts

        alerts = await get_alerts(priority="CRITICAL")

        

        # Filter by time

        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_critical = [

            a for a in alerts 

            if datetime.fromisoformat(a["timestamp"]) > cutoff_time

        ]

        

        log.info(f"Retrieved {len(recent_critical)} critical alerts from last {hours} hours")

        

        return recent_critical

        

    except Exception as e:

        log.error(f"Error retrieving critical alerts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/search")

async def search_transcripts(

    query: str = Query(..., min_length=1, description="Search query"),

    date: Optional[str] = Query(None, description="Filter by date"),

    channel: Optional[str] = Query(None, description="Filter by channel"),

    limit: int = Query(50, ge=1, le=500)

):

    """

    Search transcripts by text content

    

    Args:

        query: Text to search for

        date: Optional date filter

        channel: Optional channel filter

        limit: Maximum results

    

    Returns:

        List of matching transcript entries

    """

    

    try:

        # Get transcripts

        transcripts = await get_transcripts(date=date, channel=channel)

        

        # Simple text search (case-insensitive)

        query_lower = query.lower()

        matches = [

            t for t in transcripts 

            if query_lower in t["text"].lower()

        ]

        

        # Limit results

        limited = matches[:limit]

        

        log.info(f"Search for '{query}' found {len(matches)} results (returning {len(limited)})")

        

        return limited

        

    except Exception as e:

        log.error(f"Error searching transcripts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/stats/summary")

async def get_stats_summary():

    """

    Get summary statistics for today

    

    Returns:

        Statistics including total transmissions, alerts, etc.

    """

    

    try:

        # Get today's data

        transcripts = await get_transcripts()

        alerts = await get_alerts()

        

        # Calculate stats

        stats = {

            "date": datetime.now().strftime("%Y-%m-%d"),

            "total_transmissions": len(transcripts),

            "total_alerts": len(alerts),

            "alerts_by_priority": {},

            "transmissions_by_channel": {}

        }

        

        # Count alerts by priority

        for alert in alerts:

            priority = alert.get("priority", "UNKNOWN")

            stats["alerts_by_priority"][priority] = stats["alerts_by_priority"].get(priority, 0) + 1

        

        # Count transmissions by channel

        for transcript in transcripts:

            channel = transcript.get("channel", "UNKNOWN")

            stats["transmissions_by_channel"][channel] = stats["transmissions_by_channel"].get(channel, 0) + 1

        

        log.info("Generated statistics summary")

        

        return stats

        

    except Exception as e:

        log.error(f"Error generating stats: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.get("/stats/timeline")

async def get_timeline_stats(

    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),

    interval_minutes: int = Query(60, ge=5, le=1440, description="Time interval in minutes")

):

    """

    Get timeline statistics showing transmission activity over time

    

    Args:

        date: Date to analyze (defaults to today)

        interval_minutes: Size of time buckets in minutes

    

    Returns:

        Timeline data with transmission counts per interval

    """

    

    try:

        # Get transcripts

        transcripts = await get_transcripts(date=date)

        

        # Group by time intervals

        timeline = {}

        for transcript in transcripts:

            timestamp = datetime.fromisoformat(transcript["timestamp"])

            

            # Round to interval

            minutes_since_midnight = timestamp.hour * 60 + timestamp.minute

            interval_bucket = (minutes_since_midnight // interval_minutes) * interval_minutes

            bucket_time = timestamp.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=interval_bucket)

            bucket_key = bucket_time.strftime("%H:%M")

            

            if bucket_key not in timeline:

                timeline[bucket_key] = {

                    "time": bucket_key,

                    "count": 0,

                    "alerts": 0

                }

            

            timeline[bucket_key]["count"] += 1

            if transcript.get("alert", False):

                timeline[bucket_key]["alerts"] += 1

        

        # Convert to sorted list

        timeline_list = sorted(timeline.values(), key=lambda x: x["time"])

        

        log.info(f"Generated timeline with {len(timeline_list)} intervals")

        

        return timeline_list

        

    except Exception as e:

        log.error(f"Error generating timeline: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))





@router.delete("/transcripts")

async def delete_old_transcripts(

    days_to_keep: int = Query(30, ge=1, le=365, description="Number of days to keep")

):

    """

    Delete transcripts older than specified days

    (Admin endpoint - should be protected in production)

    

    Args:

        days_to_keep: Keep transcripts from last N days

    

    Returns:

        Number of files deleted

    """

    

    try:

        import config

        from pathlib import Path

        

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        deleted_count = 0

        

        # Check transcript directory

        for file in config.TRANSCRIPT_DIR.glob("transcript_*.jsonl"):

            # Extract date from filename

            date_str = file.stem.replace("transcript_", "")

            try:

                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                

                if file_date < cutoff_date:

                    file.unlink()

                    deleted_count += 1

                    log.info(f"Deleted old transcript: {file.name}")

            except ValueError:

                # Skip files with invalid date format

                continue

        

        log.info(f"Deleted {deleted_count} old transcript files")

        

        return {

            "deleted_count": deleted_count,

            "cutoff_date": cutoff_date.strftime("%Y-%m-%d")

        }

        

    except Exception as e:

        log.error(f"Error deleting old transcripts: {str(e)}")

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/transcripts")
async def export_transcripts(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    channel: Optional[str] = Query(None, description="Filter by channel name")
):
    """
    Export transcripts as JSON
    
    Args:
        date: Filter by date (YYYY-MM-DD), defaults to today
        channel: Filter by channel name
    
    Returns:
        JSON file download
    """
    try:
        transcripts = await get_transcripts(date=date, channel=channel)
        
        # Convert to JSON string
        json_data = json.dumps(transcripts, indent=2, default=str)
        
        from fastapi import Response
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=transcripts_{date or datetime.now().strftime('%Y-%m-%d')}.json"
            }
        )
    except Exception as e:
        log.error(f"Error exporting transcripts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/alerts")
async def export_alerts(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Export alerts as JSON
    
    Args:
        date: Filter by date (YYYY-MM-DD), defaults to today
        priority: Filter by priority level
    
    Returns:
        JSON file download
    """
    try:
        alerts = await get_alerts(date=date, priority=priority)
        
        # Convert to JSON string
        json_data = json.dumps(alerts, indent=2, default=str)
        
        from fastapi import Response
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=alerts_{date or datetime.now().strftime('%Y-%m-%d')}.json"
            }
        )
    except Exception as e:
        log.error(f"Error exporting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/all")
async def export_all(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Export all data (transcripts and alerts) as XML in Apple Health format
    
    Args:
        date: Filter by date (YYYY-MM-DD), defaults to today
    
    Returns:
        XML file download
    """
    try:
        transcripts = await get_transcripts(date=date)
        alerts = await get_alerts(date=date)
        
        # Create XML structure similar to Apple Health export
        import xml.etree.ElementTree as ET
        root = ET.Element("HealthData")
        root.set("locale", "en_US")
        
        # Add export date
        export_date = ET.SubElement(root, "ExportDate")
        export_date.set("value", datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"))
        
        # Add transcripts as records
        for transcript in transcripts:
            record = ET.SubElement(root, "Record")
            record.set("type", "HKQuantityTypeIdentifierRadioTranscription")
            record.set("sourceName", transcript.get("channel", "Unknown"))
            record.set("startDate", transcript.get("timestamp", ""))
            record.set("endDate", transcript.get("timestamp", ""))
            record.set("value", transcript.get("text", ""))
            
            # Add metadata
            metadata = ET.SubElement(record, "MetadataEntry")
            metadata.set("key", "confidence")
            metadata.set("value", str(transcript.get("confidence", 0)))
            
            if transcript.get("is_alert"):
                alert_meta = ET.SubElement(record, "MetadataEntry")
                alert_meta.set("key", "is_alert")
                alert_meta.set("value", "true")
        
        # Add alerts as records
        for alert in alerts:
            record = ET.SubElement(root, "Record")
            record.set("type", "HKQuantityTypeIdentifierAlert")
            record.set("sourceName", alert.get("channel", "Unknown"))
            record.set("startDate", alert.get("timestamp", ""))
            record.set("endDate", alert.get("timestamp", ""))
            record.set("value", alert.get("text", ""))
            
            # Add metadata
            priority_meta = ET.SubElement(record, "MetadataEntry")
            priority_meta.set("key", "priority")
            priority_meta.set("value", alert.get("priority", "UNKNOWN"))
        
        # Convert to XML string
        xml_str = ET.tostring(root, encoding='unicode', xml_declaration=True)
        
        from fastapi import Response
        return Response(
            content=xml_str,
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename=fire_dept_export_{date or datetime.now().strftime('%Y-%m-%d')}.xml"
            }
        )
    except Exception as e:
        log.error(f"Error exporting all data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/data")
async def receive_health_data(
    data_type: str = Query(..., description="Type: heart_rate, oxygen, temperature"),
    value: float = Query(..., description="Measurement value"),
    source: str = Query("unknown", description="Source device name"),
    timestamp: Optional[str] = Query(None, description="ISO timestamp")
):
    """
    Receive real-time health data from external sources
    
    This endpoint can be called by:
    - Apple HealthKit apps
    - Fitbit API webhooks
    - Custom health device integrations
    - Manual data entry
    
    Returns:
        Success confirmation
    """
    try:
        from api.server import app_state
        from datetime import datetime
        
        if app_state.get("health_monitor") is None:
            raise HTTPException(status_code=503, detail="Health monitor not initialized")
        
        # Parse timestamp if provided
        ts = None
        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                pass
        
        # Add data point
        app_state["health_monitor"].add_data_point(
            data_type=data_type,
            value=value,
            source=source,
            timestamp=ts
        )
        
        log.info(f"Health data received: {data_type}={value} from {source}")
        
        return {
            "status": "success",
            "message": "Health data received",
            "data_type": data_type,
            "value": value
        }
    except Exception as e:
        log.error(f"Error receiving health data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/stats")
async def get_health_stats():
    """
    Get current health statistics
    
    Returns:
        Current health stats (heart rate, oxygen, etc.)
    """
    try:
        from api.server import app_state
        
        if app_state.get("health_monitor") is None:
            raise HTTPException(status_code=503, detail="Health monitor not initialized")
        
        stats = app_state["health_monitor"].get_current_stats()
        
        return stats
    except Exception as e:
        log.error(f"Error getting health stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/recent")
async def get_recent_health_data(
    data_type: str = Query(..., description="Type: heart_rate, oxygen, temperature"),
    minutes: int = Query(60, ge=1, le=1440, description="Minutes to look back")
):
    """
    Get recent health data points
    
    Args:
        data_type: Type of health data
        minutes: How many minutes to look back
    
    Returns:
        List of recent data points
    """
    try:
        from api.server import app_state
        
        if app_state.get("health_monitor") is None:
            raise HTTPException(status_code=503, detail="Health monitor not initialized")
        
        data = app_state["health_monitor"].get_recent_data(data_type, minutes)
        
        return {
            "data_type": data_type,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        log.error(f"Error getting recent health data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

