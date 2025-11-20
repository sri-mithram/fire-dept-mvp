"""
Live Microphone Transcription Manager

Handles button-controlled live microphone transcription
User clicks button -> starts recording -> transcribes -> streams results
"""

import asyncio
import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from queue import Queue
import threading

import config
from core.transcription_service import TranscriptionService
from core.vad_detector import VADDetector
from utils.logger import log


class LiveTranscriptionManager:
    """
    Manages live microphone transcription with button control
    """
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize live transcription manager
        
        Args:
            callback: Async callback for transcription results
                     Signature: async def callback(result: dict)
        """
        self.callback = callback
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_duration = config.CHUNK_DURATION
        
        # State
        self.is_recording = False
        self.stream: Optional[sd.InputStream] = None
        self.audio_queue = Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Components
        self.transcription_service = TranscriptionService()
        self.vad_detector = VADDetector(sample_rate=self.sample_rate)
        
        # Device
        self.device_index = None  # None = default device
        
        log.info("Live Transcription Manager initialized")
    
    def set_device(self, device_index: Optional[int] = None):
        """Set audio input device (None = default)"""
        self.device_index = device_index
        log.info(f"Set audio device to index: {device_index if device_index is not None else 'default'}")
    
    async def start_recording(self):
        """Start recording from microphone"""
        if self.is_recording:
            log.warning("Already recording")
            return
        
        try:
            self.is_recording = True
            self.vad_detector.reset()
            
            # Audio callback
            def audio_callback(indata, frames, time_info, status):
                if status:
                    log.warning(f"Audio status: {status}")
                
                # Get mono audio
                audio_chunk = indata[:, 0].copy()
                self.audio_queue.put(audio_chunk)
            
            # Start input stream
            self.stream = sd.InputStream(
                device=self.device_index,
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback,
                blocksize=int(self.sample_rate * self.chunk_duration)
            )
            
            self.stream.start()
            
            # Start processing task
            self.processing_task = asyncio.create_task(self._process_audio())
            
            log.info("🎤 Started live microphone recording")
            
        except Exception as e:
            self.is_recording = False
            log.error(f"Failed to start recording: {str(e)}")
            raise
    
    async def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            log.warning("Not recording")
            return
        
        try:
            self.is_recording = False
            
            # Stop stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Wait for processing task
            if self.processing_task:
                await asyncio.sleep(0.5)  # Give time to process any remaining audio
                if not self.processing_task.done():
                    self.processing_task.cancel()
                    try:
                        await self.processing_task
                    except asyncio.CancelledError:
                        pass
                self.processing_task = None
            
            # Reset VAD
            self.vad_detector.reset()
            
            # Clear queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            
            log.info("🛑 Stopped live microphone recording")
            
        except Exception as e:
            log.error(f"Error stopping recording: {str(e)}")
    
    async def _process_audio(self):
        """Process audio from queue"""
        log.debug("Started processing audio queue")
        
        while self.is_recording:
            try:
                # Get audio chunk (non-blocking)
                if not self.audio_queue.empty():
                    audio_chunk = self.audio_queue.get_nowait()
                    
                    # Process with VAD
                    complete_utterance = self.vad_detector.process_audio(
                        audio_chunk, 
                        sample_rate=self.sample_rate
                    )
                    
                    # If complete utterance detected, transcribe
                    if complete_utterance is not None:
                        log.info("Complete utterance detected, transcribing...")
                        
                        # Transcribe
                        result = await self.transcription_service.transcribe(
                            complete_utterance,
                            channel="Live Microphone",
                            sample_rate=self.sample_rate
                        )
                        
                        if result:
                            # Add metadata
                            result["source"] = "live_microphone"
                            result["channel"] = "Live Microphone"
                            result["channel_id"] = "live_mic"
                            
                            # Call callback if provided
                            if self.callback:
                                await self.callback(result)
                else:
                    # Sleep briefly if queue empty
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                log.error(f"Error processing audio: {str(e)}")
                await asyncio.sleep(0.1)
        
        log.debug("Stopped processing audio queue")
    
    def get_status(self) -> dict:
        """Get current status"""
        return {
            "is_recording": self.is_recording,
            "device_index": self.device_index,
            "queue_size": self.audio_queue.qsize(),
            "vad_state": self.vad_detector.get_state()
        }

