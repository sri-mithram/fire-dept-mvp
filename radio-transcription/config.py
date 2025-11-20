"""
Radio Transcription Backend Configuration
GPT-4o powered, multi-channel support
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# API CREDENTIALS
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this in .env file

# ============================================================================
# TRANSCRIPTION SETTINGS
# ============================================================================

# Model selection
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-transcribe")  # GPT-4o audio model
TRANSCRIPTION_LANGUAGE = os.getenv("TRANSCRIPTION_LANGUAGE", "en")

# Audio settings
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))  # Hz
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))   # Mono
CHUNK_DURATION = float(os.getenv("CHUNK_DURATION", "0.1"))  # Process audio in 100ms chunks

# ============================================================================
# MULTI-CHANNEL CONFIGURATION
# ============================================================================

# Define your radio channels
RADIO_CHANNELS = {
    "channel_1": {
        "name": "Fire Dispatch",
        "device_index": 0,  # Will be detected when dongle arrives
        "frequency": "154.280 MHz",  # Update with your frequency
        "color": "🔴",
        "priority": "HIGH",
        "enabled": True
    },
    "channel_2": {
        "name": "Fire Operations",
        "device_index": 1,  # Will be detected when dongle arrives
        "frequency": "154.340 MHz",  # Update with your frequency
        "color": "🔵",
        "priority": "MEDIUM",
        "enabled": True
    }
}

# ============================================================================
# VOICE ACTIVITY DETECTION (VAD)
# ============================================================================

VAD_MODE = int(os.getenv("VAD_MODE", "1"))  # 0=Quality, 1=Low Bitrate, 2=Aggressive, 3=Very Aggressive
VAD_SILENCE_THRESHOLD = float(os.getenv("VAD_SILENCE_THRESHOLD", "0.02"))  # Energy threshold
VAD_SILENCE_DURATION = float(os.getenv("VAD_SILENCE_DURATION", "1.2"))    # Seconds of silence before transmission ends
VAD_MIN_SPEECH_DURATION = float(os.getenv("VAD_MIN_SPEECH_DURATION", "0.3"))  # Minimum transmission length

# ============================================================================
# ENERGY-BASED VAD SETTINGS (Replaces WebRTC VAD)
# ============================================================================
# Energy threshold for detecting speech (0.0 to 1.0)
# This is the RMS (Root Mean Square) audio level
# Lower = more sensitive (picks up quieter speech and noise)
# Higher = less sensitive (only loud/clear speech)
#
# Typical values:
#   0.015 - Very sensitive (quiet speech, might pick up background)
#   0.02  - Balanced (recommended for radio)
#   0.03  - Less sensitive (only clear, loud speech)
#   0.05  - Very strict (very loud speech only)
ENERGY_THRESHOLD = float(os.getenv("ENERGY_THRESHOLD", "0.001"))

# Note: VAD_SILENCE_DURATION and VAD_MIN_SPEECH_DURATION 
# are already defined above and still apply

# ============================================================================
# ALERT KEYWORDS
# ============================================================================

ALERT_KEYWORDS = [
    "mayday",
    "emergency",
    "officer down",
    "firefighter down",
    "code red",
    "evacuate",
    "urgent",
    "help",
    "injury",
    "collapse"
]

# Priority levels for alerts
ALERT_PRIORITY = {
    "mayday": "CRITICAL",
    "firefighter down": "CRITICAL",
    "officer down": "CRITICAL",
    "emergency": "HIGH",
    "urgent": "HIGH",
    "evacuate": "HIGH",
    "injury": "MEDIUM",
    "help": "MEDIUM"
}

# ============================================================================
# LOGGING & STORAGE
# ============================================================================

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"
ALERT_DIR = DATA_DIR / "alerts"

# Create directories
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
ALERT_DIR.mkdir(parents=True, exist_ok=True)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
LOG_FILE = BASE_DIR / "backend.log"

# ============================================================================
# API SERVER SETTINGS (for frontend)
# ============================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"  # Auto-reload on code changes (dev only)

# CORS settings (allow frontend to connect)
CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://localhost:8000,http://127.0.0.1:8000,file://")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",") if origin.strip()]
# Also allow all origins in development (for file:// protocol)
if os.getenv("DEBUG_MODE", "false").lower() == "true":
    CORS_ORIGINS = ["*"]

# WebSocket settings
WS_HEARTBEAT_INTERVAL = 30  # Seconds
WS_MAX_CONNECTIONS = 10

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Transcription queue
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
TRANSCRIPTION_TIMEOUT = int(os.getenv("TRANSCRIPTION_TIMEOUT", "10"))  # Seconds

# Rate limiting (to avoid OpenAI quota issues)
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "50"))
MAX_AUDIO_DURATION = int(os.getenv("MAX_AUDIO_DURATION", "300"))  # Seconds (5 min max per transmission)

# ============================================================================
# DEVELOPMENT / TESTING
# ============================================================================

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
SAVE_AUDIO_FILES = os.getenv("SAVE_AUDIO_FILES", "false").lower() == "true"  # Save audio chunks for debugging
SIMULATE_AUDIO = os.getenv("SIMULATE_AUDIO", "false").lower() == "true"    # Use test audio instead of real input