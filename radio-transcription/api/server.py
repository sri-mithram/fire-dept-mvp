"""
FastAPI server configuration and setup

Main API application

"""
from fastapi import FastAPI, WebSocket, Query

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from typing import Optional

import asyncio

import config

from api.routes import router

from api.websocket import websocket_endpoint, manager

from utils.logger import log

# Global state

app_state = {

    "is_running": False,

    "channel_manager": None,

    "audio_manager": None,

    "health_monitor": None,

    "live_transcription_manager": None,

    "start_time": None

}

@asynccontextmanager

async def lifespan(app: FastAPI):

    """

    Lifespan events for startup and shutdown

    """

    # Startup

    log.info("Starting Radio Transcription Backend API")

    log.info(f"API server running on {config.API_HOST}:{config.API_PORT}")

    

    # Import here to avoid circular imports

    from core.channel_manager import ChannelManager

    from core.audio_manager import AudioManager

    from core.health_monitor import HealthMonitor

    from core.live_transcription_manager import LiveTranscriptionManager

    from datetime import datetime

    

    # Initialize managers

    app_state["channel_manager"] = ChannelManager()
    
    app_state["health_monitor"] = HealthMonitor()
    
    # Live transcription callback
    async def live_transcription_callback(result: dict):
        """Called when live transcription completes"""
        # Broadcast transcript to WebSocket clients
        await manager.broadcast_transcript(result)
        
        # Check for alerts (optional - you can enable this)
        # if result.get("is_alert"):
        #     await manager.broadcast_alert(result.get("alert_message"))
    
    app_state["live_transcription_manager"] = LiveTranscriptionManager(
        callback=live_transcription_callback
    )
    
    # Register health monitor callback to broadcast via WebSocket
    async def health_update_callback(data: dict):
        """Broadcast health updates via WebSocket"""
        await manager.broadcast({
            "type": "health_update",
            "data": data
        })
    
    app_state["health_monitor"].add_callbacks(health_update_callback)

    

    # Audio callback

    async def audio_callback(channel_id: str, audio_chunk):

        """Called when audio is captured"""

        result = await app_state["channel_manager"].process_audio(channel_id, audio_chunk)

        

        if result:

            # Broadcast transcript to WebSocket clients

            await manager.broadcast_transcript(result)

            

            # If alert, broadcast alert

            if result.get("is_alert"):

                await manager.broadcast_alert(result.get("alert_message"))

    

    app_state["audio_manager"] = AudioManager(callback=audio_callback)

    app_state["start_time"] = datetime.now()

    

    log.info("Backend initialized successfully")

    

    yield

    

    # Shutdown

    log.info("Shutting down Radio Transcription Backend API")

    

    if app_state["audio_manager"]:

        await app_state["audio_manager"].stop_all()
    
    if app_state["live_transcription_manager"]:
        await app_state["live_transcription_manager"].stop_recording()

    

    log.info("Backend shutdown complete")

# Create FastAPI app

app = FastAPI(

    title="Radio Transcription Backend",

    description="Multi-channel radio transcription system powered by GPT-4o",

    version="1.0.0",

    lifespan=lifespan

)

# CORS middleware

app.add_middleware(

    CORSMiddleware,

    allow_origins=config.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

# Include routes

app.include_router(router, prefix="/api/v1")

# WebSocket endpoint

@app.websocket("/ws")

async def websocket_route(websocket: WebSocket):

    """WebSocket endpoint for real-time streaming"""

    await websocket_endpoint(websocket)

# System control endpoints

@app.post("/api/v1/system/start")

async def start_system():

    """Start audio capture and transcription"""

    

    if app_state["is_running"]:

        return {"status": "already_running", "message": "System is already running"}

    

    try:

        log.info("Starting transcription system...")

        

        # Start audio capture

        await app_state["audio_manager"].start_all()

        

        app_state["is_running"] = True

        

        # Broadcast status to clients

        await manager.broadcast_status({

            "is_running": True,

            "message": "Transcription system started"

        })

        

        log.info("Transcription system started successfully")

        

        return {

            "status": "success",

            "message": "Transcription system started",

            "channels": list(config.RADIO_CHANNELS.keys())

        }

        

    except Exception as e:

        log.error(f"Error starting system: {str(e)}")

        return {

            "status": "error",

            "message": str(e)

        }

@app.post("/api/v1/system/stop")

async def stop_system():

    """Stop audio capture and transcription"""

    

    if not app_state["is_running"]:

        return {"status": "not_running", "message": "System is not running"}

    

    try:

        log.info("Stopping transcription system...")

        

        # Stop audio capture

        await app_state["audio_manager"].stop_all()

        

        app_state["is_running"] = False

        

        # Broadcast status to clients

        await manager.broadcast_status({

            "is_running": False,

            "message": "Transcription system stopped"

        })

        

        log.info("Transcription system stopped successfully")

        

        return {

            "status": "success",

            "message": "Transcription system stopped"

        }

        

    except Exception as e:

        log.error(f"Error stopping system: {str(e)}")

        return {

            "status": "error",

            "message": str(e)

        }

@app.get("/api/v1/system/status")

async def get_system_status():

    """Get current system status"""

    

    from datetime import datetime

    

    status = {

        "is_running": app_state["is_running"],

        "uptime_seconds": (datetime.now() - app_state["start_time"]).total_seconds() if app_state["start_time"] else 0,

        "websocket_connections": manager.get_connection_count(),

        "channels": {}

    }

    

    # Get channel status

    if app_state["channel_manager"]:

        status["channels"] = app_state["channel_manager"].get_channel_status()

    

    # Get audio status

    if app_state["audio_manager"]:

        status["audio"] = app_state["audio_manager"].get_status()

    

    return status

@app.get("/api/v1/devices")

async def list_audio_devices():

    """List available audio input devices"""

    

    if app_state["audio_manager"]:

        devices = app_state["audio_manager"].list_devices()

        return {"devices": devices}

    else:

        return {"devices": []}

# Live Microphone Transcription Endpoints

@app.post("/api/v1/live-transcription/start")

async def start_live_transcription(device_index: Optional[int] = None):

    """Start live microphone transcription"""

    

    if app_state["live_transcription_manager"] is None:

        return {"status": "error", "message": "Live transcription manager not initialized"}

    

    if app_state["live_transcription_manager"].is_recording:

        return {"status": "already_recording", "message": "Already recording"}

    

    try:

        # Set device if provided

        if device_index is not None:

            app_state["live_transcription_manager"].set_device(device_index)

        

        # Start recording

        await app_state["live_transcription_manager"].start_recording()

        

        # Broadcast status

        await manager.broadcast_status({

            "live_transcription_active": True,

            "message": "Live microphone transcription started"

        })

        

        log.info("Live microphone transcription started")

        

        return {

            "status": "success",

            "message": "Live microphone transcription started",

            "device_index": device_index

        }

        

    except Exception as e:

        log.error(f"Error starting live transcription: {str(e)}")

        return {

            "status": "error",

            "message": str(e)

        }

@app.post("/api/v1/live-transcription/stop")

async def stop_live_transcription():

    """Stop live microphone transcription"""

    

    if app_state["live_transcription_manager"] is None:

        return {"status": "error", "message": "Live transcription manager not initialized"}

    

    if not app_state["live_transcription_manager"].is_recording:

        return {"status": "not_recording", "message": "Not currently recording"}

    

    try:

        # Stop recording

        await app_state["live_transcription_manager"].stop_recording()

        

        # Broadcast status

        await manager.broadcast_status({

            "live_transcription_active": False,

            "message": "Live microphone transcription stopped"

        })

        

        log.info("Live microphone transcription stopped")

        

        return {

            "status": "success",

            "message": "Live microphone transcription stopped"

        }

        

    except Exception as e:

        log.error(f"Error stopping live transcription: {str(e)}")

        return {

            "status": "error",

            "message": str(e)

        }

@app.get("/api/v1/live-transcription/status")

async def get_live_transcription_status():

    """Get live transcription status"""

    

    if app_state["live_transcription_manager"] is None:

        return {"status": "not_initialized"}

    

    status = app_state["live_transcription_manager"].get_status()

    

    return {

        "status": "success",

        "is_recording": status["is_recording"],

        "device_index": status["device_index"],

        "queue_size": status["queue_size"],

        "vad_state": status["vad_state"]

    }

# Root endpoint

@app.get("/")

async def root():

    """Root endpoint"""

    return {

        "service": "Radio Transcription Backend",

        "version": "1.0.0",

        "status": "running",

        "docs": "/docs",

        "websocket": "/ws"

    }

