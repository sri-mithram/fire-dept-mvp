"""
Logging utility for radio transcription backend

Handles both file and console logging with JSON format for production

"""



import sys

from pathlib import Path

from loguru import logger

from datetime import datetime

import json



import config





def setup_logger():

    """Configure loguru logger"""

    

    # Remove default handler

    logger.remove()

    

    # Console handler (colored output for development)

    logger.add(

        sys.stderr,

        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",

        level=config.LOG_LEVEL,

        colorize=True

    )

    

    # File handler (JSON format for production)

    if config.LOG_TO_FILE:

        logger.add(

            config.LOG_FILE,

            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} | {message}",

            level=config.LOG_LEVEL,

            rotation="100 MB",

            retention="30 days",

            compression="zip"

        )

    

    return logger





# Initialize logger

log = setup_logger()





def log_transcript(channel: str, text: str, timestamp: datetime, confidence: float = None, alert: bool = False):

    """Log a transcript entry"""

    

    entry = {

        "timestamp": timestamp.isoformat(),

        "channel": channel,

        "text": text,

        "confidence": confidence,

        "alert": alert

    }

    

    if alert:

        log.warning(f"ALERT on {channel}: {text}")

    else:

        log.info(f"[{channel}] {text}")

    

    return entry





def log_error(error: Exception, context: str = None):

    """Log an error with context"""

    

    log.error(f"Error in {context}: {str(error)}", exc_info=True)

