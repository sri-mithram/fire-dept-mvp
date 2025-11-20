"""
Voice Activity Detection (VAD) for radio transmissions
Energy-based detection that works with any sample rate
"""

import numpy as np
from typing import Optional
from collections import deque

import config
from utils.logger import log


class VADDetector:
    """
    Energy-based Voice Activity Detection
    Works with any sample rate - no resampling needed!
    """
    
    def __init__(self, sample_rate: int = None):
        """
        Initialize VAD detector
        
        Args:
            sample_rate: Audio sample rate (can be any value - we don't resample!)
        """
        self.sample_rate = sample_rate or config.SAMPLE_RATE
        
        # State management
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_duration = 0
        
        # Configuration from config.py
        self.energy_threshold = config.ENERGY_THRESHOLD
        self.silence_duration_threshold = config.VAD_SILENCE_DURATION
        self.min_speech_duration = config.VAD_MIN_SPEECH_DURATION
        
        # Chunk tracking
        self.chunk_duration = config.CHUNK_DURATION  # seconds per chunk
        
        log.info(f"Energy-based VAD initialized")
        log.info(f"  Sample rate: {self.sample_rate}Hz (any rate supported)")
        log.info(f"  Energy threshold: {self.energy_threshold}")
        log.info(f"  Silence duration: {self.silence_duration_threshold}s")
        log.info(f"  Min speech duration: {self.min_speech_duration}s")
    
    def calculate_energy(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate RMS (Root Mean Square) energy of audio chunk
        
        This measures the "volume" or "power" of the audio
        
        Args:
            audio_chunk: Audio data as numpy array
        
        Returns:
            Energy value (higher = louder)
        """
        # RMS = sqrt(mean(samples^2))
        return np.sqrt(np.mean(audio_chunk**2))
    
    def process_audio(self, audio_chunk: np.ndarray, sample_rate: int = None) -> Optional[np.ndarray]:
        """
        Process audio chunk and return complete utterance if detected
        
        Works with ANY sample rate!
        
        Args:
            audio_chunk: Audio data as numpy array
            sample_rate: Sample rate of this audio (optional, uses init value)
        
        Returns:
            Complete utterance as numpy array if speech ended, None otherwise
        """
        
        # Update sample rate if provided
        if sample_rate and sample_rate != self.sample_rate:
            self.sample_rate = sample_rate
            self.chunk_duration = len(audio_chunk) / sample_rate
        
        # Calculate energy
        energy = self.calculate_energy(audio_chunk)
        
        # Determine if this is speech based on energy
        is_speech = energy > self.energy_threshold
        
        # Debug logging (optional)
        if config.DEBUG_MODE:
            log.debug(f"Energy: {energy:.4f} | Threshold: {self.energy_threshold} | Speech: {is_speech}")
        
        if is_speech:
            # Speech detected
            if not self.is_speaking:
                # START of new utterance
                self.is_speaking = True
                self.speech_buffer = []
                self.silence_duration = 0
                log.debug(f"🎤 Speech started (energy: {energy:.4f})")
            
            # Add audio to buffer
            self.speech_buffer.extend(audio_chunk)
            self.silence_duration = 0
            
        else:
            # Silence detected
            if self.is_speaking:
                # We're in an utterance, but silence detected
                
                # Still add to buffer (might be brief pause mid-sentence)
                self.speech_buffer.extend(audio_chunk)
                
                # Count silence duration
                self.silence_duration += self.chunk_duration
                
                # Check if silence has lasted long enough to end utterance
                if self.silence_duration >= self.silence_duration_threshold:
                    # END of utterance
                    speech_duration = len(self.speech_buffer) / self.sample_rate
                    
                    log.debug(f"🔇 Speech ended (duration: {speech_duration:.2f}s, silence: {self.silence_duration:.2f}s)")
                    
                    # Check minimum duration
                    if speech_duration >= self.min_speech_duration:
                        # Return complete utterance
                        utterance = np.array(self.speech_buffer, dtype=np.float32)
                        
                        log.info(f"✅ Complete utterance detected: {speech_duration:.2f}s")
                        
                        # Reset state
                        self.is_speaking = False
                        self.speech_buffer = []
                        self.silence_duration = 0
                        
                        return utterance
                    else:
                        log.debug(f"⚠️  Speech too short ({speech_duration:.2f}s < {self.min_speech_duration}s), discarding")
                        self.is_speaking = False
                        self.speech_buffer = []
                        self.silence_duration = 0
        
        return None
    
    def reset(self):
        """Reset detector state"""
        self.is_speaking = False
        self.speech_buffer = []
        self.silence_duration = 0
        log.debug("VAD detector reset")
    
    def get_state(self) -> dict:
        """Get current detector state (for debugging)"""
        return {
            "is_speaking": self.is_speaking,
            "buffer_size": len(self.speech_buffer),
            "buffer_duration": len(self.speech_buffer) / self.sample_rate if self.speech_buffer else 0,
            "silence_duration": self.silence_duration,
            "sample_rate": self.sample_rate
        }