"""
Storage utilities for transcripts and alerts

Handles JSON file operations for daily logs

"""
import json

from pathlib import Path

from datetime import datetime

from typing import Dict, List

import aiofiles

import config

from utils.logger import log

async def save_transcript(channel: str, text: str, timestamp: datetime, 

                         confidence: float = None, alert: bool = False,

                         alert_keywords: List[str] = None):

    """

    Save transcript to daily log file

    

    Args:

        channel: Channel name

        text: Transcribed text

        timestamp: Timestamp of transmission

        confidence: Confidence score

        alert: Whether this is an alert

        alert_keywords: List of detected alert keywords

    """

    

    # Daily transcript file

    date_str = timestamp.strftime("%Y-%m-%d")

    transcript_file = config.TRANSCRIPT_DIR / f"transcript_{date_str}.jsonl"

    

    # Create entry

    entry = {

        "timestamp": timestamp.isoformat(),

        "channel": channel,

        "text": text,

        "confidence": confidence,

        "alert": alert,

        "alert_keywords": alert_keywords or []

    }

    

    # Append to JSONL file (one JSON object per line)

    async with aiofiles.open(transcript_file, mode='a') as f:

        await f.write(json.dumps(entry) + '\n')

    

    # If alert, also save to alerts file

    if alert:

        await save_alert(channel, text, timestamp, alert_keywords)

    

    log.debug(f"Saved transcript: {channel} - {text[:50]}...")

async def save_alert(channel: str, text: str, timestamp: datetime, keywords: List[str]):

    """Save alert to separate alerts file"""

    

    date_str = timestamp.strftime("%Y-%m-%d")

    alert_file = config.ALERT_DIR / f"alerts_{date_str}.jsonl"

    

    entry = {

        "timestamp": timestamp.isoformat(),

        "channel": channel,

        "text": text,

        "keywords": keywords,

        "priority": max([config.ALERT_PRIORITY.get(kw, "LOW") for kw in keywords], 

                       key=lambda x: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(x))

    }

    

    async with aiofiles.open(alert_file, mode='a') as f:

        await f.write(json.dumps(entry) + '\n')

    

    log.warning(f"ALERT saved: {channel} - {text}")

async def get_transcripts(date: str = None, channel: str = None) -> List[Dict]:

    """

    Retrieve transcripts from log files

    

    Args:

        date: Date string (YYYY-MM-DD), defaults to today

        channel: Filter by channel name

    

    Returns:

        List of transcript entries

    """

    

    if date is None:

        date = datetime.now().strftime("%Y-%m-%d")

    

    transcript_file = config.TRANSCRIPT_DIR / f"transcript_{date}.jsonl"

    

    if not transcript_file.exists():

        return []

    

    transcripts = []

    async with aiofiles.open(transcript_file, mode='r') as f:

        async for line in f:

            if line.strip():

                entry = json.loads(line)

                if channel is None or entry['channel'] == channel:

                    transcripts.append(entry)

    

    return transcripts

async def get_alerts(date: str = None, priority: str = None) -> List[Dict]:

    """

    Retrieve alerts from log files

    

    Args:

        date: Date string (YYYY-MM-DD), defaults to today

        priority: Filter by priority (LOW/MEDIUM/HIGH/CRITICAL)

    

    Returns:

        List of alert entries

    """

    

    if date is None:

        date = datetime.now().strftime("%Y-%m-%d")

    

    alert_file = config.ALERT_DIR / f"alerts_{date}.jsonl"

    

    if not alert_file.exists():

        return []

    

    alerts = []

    async with aiofiles.open(alert_file, mode='r') as f:

        async for line in f:

            if line.strip():

                entry = json.loads(line)

                if priority is None or entry['priority'] == priority:

                    alerts.append(entry)

    

    return alerts

