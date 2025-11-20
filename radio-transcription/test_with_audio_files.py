"""
Test script to simulate live transcription using audio files
This simulates 2 walkie-talkies by playing back audio files
"""

import asyncio
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import datetime

from core.channel_manager import ChannelManager
from core.audio_manager import AudioManager
from api.websocket import manager
from utils.logger import log
import config


class AudioFileSimulator:
    """
    Simulates live audio by reading from files
    Mimics what AudioManager does with real devices
    """
    
    def __init__(self, audio_files: dict, callback=None):
        """
        Args:
            audio_files: Dict mapping channel_id to audio file path
            callback: Async callback for audio chunks
        """
        self.audio_files = audio_files
        self.callback = callback
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_duration = config.CHUNK_DURATION
        self.is_running = False
        
        log.info("Audio file simulator initialized")
    
    async def simulate_channel(self, channel_id: str, audio_file: str):
        """Simulate audio stream from a file for one channel"""
        
        if not Path(audio_file).exists():
            log.error(f"Audio file not found: {audio_file}")
            return
        
        log.info(f"Starting simulation for {channel_id} using {audio_file}")
        
        # Load audio file
        audio_data, original_sr = sf.read(audio_file)
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]
        
        log.info(f"Audio loaded: sample_rate={original_sr}Hz, duration={len(audio_data)/original_sr:.2f}s")
        
        # NO RESAMPLING NEEDED! Use original sample rate
        sample_rate = original_sr
        
        # Calculate chunk size based on original sample rate
        chunk_size = int(sample_rate * self.chunk_duration)
        
        log.info(f"Using ORIGINAL sample rate: {sample_rate}Hz (no resampling!)")
        
        # Stream audio in chunks
        for i in range(0, len(audio_data), chunk_size):
            if not self.is_running:
                break
            
            chunk = audio_data[i:i + chunk_size]
            
            # Pad last chunk if needed
            if len(chunk) < chunk_size:
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)), mode='constant')
            
            # Send to callback with sample rate
            if self.callback:
                await self.callback(channel_id, chunk, sample_rate)
            
            # Wait to simulate real-time streaming
            await asyncio.sleep(self.chunk_duration)
        
        log.info(f"Finished simulation for {channel_id}")
    
    async def start_all(self):
        """Start simulating all channels"""
        
        self.is_running = True
        
        # Start simulation for each channel
        tasks = [
            self.simulate_channel(channel_id, audio_file)
            for channel_id, audio_file in self.audio_files.items()
        ]
        
        # Run all simulations concurrently
        await asyncio.gather(*tasks)
    
    async def stop_all(self):
        """Stop all simulations"""
        self.is_running = False


async def test_transcription(audio_file_1: str, audio_file_2: str):
    """
    Test transcription by sending ENTIRE audio files to OpenAI
    No VAD, no chunking - just raw transcription
    
    Args:
        audio_file_1: Path to first audio file (channel 1)
        audio_file_2: Path to second audio file (channel 2)
    """
    
    log.info("="*70)
    log.info("Starting DIRECT Audio Transcription Test")
    log.info("No VAD - sending entire files to OpenAI")
    log.info("="*70)
    
    # Initialize transcription service only
    from core.transcription_service import TranscriptionService
    from core.alert_system import AlertSystem
    from utils.storage import save_transcript
    
    transcription_service = TranscriptionService()
    alert_system = AlertSystem()
    
    # Process both files
    audio_files = {
        "channel_1": {"file": audio_file_1, "name": "Fire Dispatch"},
        "channel_2": {"file": audio_file_2, "name": "Fire Operations"}
    }
    
    results = []
    
    for channel_id, channel_info in audio_files.items():
        audio_file = channel_info["file"]
        channel_name = channel_info["name"]
        
        if not Path(audio_file).exists():
            log.error(f"File not found: {audio_file}")
            continue
        
        log.info(f"\n{'='*70}")
        log.info(f"Processing: {channel_name}")
        log.info(f"File: {audio_file}")
        log.info(f"{'='*70}")
        
        # Load entire audio file
        audio_data, sample_rate = sf.read(audio_file)
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]
        
        duration = len(audio_data) / sample_rate
        
        log.info(f"Loaded: {duration:.2f}s audio at {sample_rate}Hz")
        
        # Calculate energy to check if file has audio
        energy = np.sqrt(np.mean(audio_data**2))
        log.info(f"Audio energy: {energy:.6f}")
        
        if energy < 0.0001:
            log.warning(f"⚠️  Audio is very quiet or silent (energy: {energy:.6f})")
        
        # Send ENTIRE file to OpenAI
        log.info(f"Sending entire {duration:.2f}s audio to OpenAI...")
        
        result = await transcription_service.transcribe(
            audio_data,
            channel_name,
            sample_rate
        )
        
        if result:
            results.append(result)
            
            # Display result
            text = result["text"]
            timestamp = result["timestamp"].strftime("%H:%M:%S")
            
            # Check for alerts
            is_alert, keywords, priority = alert_system.check_for_alerts(text)
            
            if is_alert:
                print(f"\n{'!'*70}")
                print(f"🚨 ALERT [{priority}] 🔴 [{channel_name}] [{timestamp}]")
                print(f"   Keywords: {', '.join(keywords)}")
                print(f"   {text}")
                print(f"{'!'*70}\n")
            else:
                print(f"\n🔴 [{channel_name}] [{timestamp}]")
                print(f"   {text}\n")
            
            # Save to storage
            await save_transcript(
                channel=channel_name,
                text=text,
                timestamp=result["timestamp"],
                confidence=result.get("confidence"),
                alert=is_alert,
                alert_keywords=keywords if is_alert else []
            )
        else:
            log.warning(f"❌ No transcription returned for {channel_name}")
    
    # Summary
    log.info("")
    log.info("="*70)
    log.info("Test Complete - Summary")
    log.info("="*70)
    log.info(f"Files processed: {len(audio_files)}")
    log.info(f"Successful transcriptions: {len(results)}")
    
    if results:
        log.info("")
        log.info("Transcriptions:")
        for i, result in enumerate(results, 1):
            log.info(f"  {i}. [{result['channel']}] {result['text'][:60]}...")
    
    log.info("")
    log.info("Check data/transcripts/ for saved logs")
    log.info("="*70)
    
    return results


async def main():
    """Main test function"""
    
    import sys
    
    # Get audio file paths from command line
    if len(sys.argv) != 3:
        print("Usage: python test_with_audio_files.py <audio_file_1> <audio_file_2>")
        print("")
        print("Example:")
        print("  python test_with_audio_files.py walkie1.wav walkie2.wav")
        print("")
        sys.exit(1)
    
    audio_file_1 = sys.argv[1]
    audio_file_2 = sys.argv[2]
    
    # Check files exist
    if not Path(audio_file_1).exists():
        log.error(f"File not found: {audio_file_1}")
        sys.exit(1)
    
    if not Path(audio_file_2).exists():
        log.error(f"File not found: {audio_file_2}")
        sys.exit(1)
    
    # Run test
    await test_transcription(audio_file_1, audio_file_2)


if __name__ == "__main__":
    asyncio.run(main())