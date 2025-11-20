"""
GPT-4o Transcription Service

Handles audio transcription using OpenAI's API

"""



import asyncio

from datetime import datetime

from typing import Dict, Optional

import numpy as np

import soundfile as sf

from openai import AsyncOpenAI

import io



import config

from utils.logger import log





class TranscriptionService:

    """

    GPT-4o powered transcription service

    Handles audio-to-text conversion via OpenAI API

    """

    

    def __init__(self):

        """Initialize transcription service"""

        

        if not config.OPENAI_API_KEY:

            raise ValueError("OPENAI_API_KEY not found in environment variables")

        

        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

        self.sample_rate = config.SAMPLE_RATE

        

        log.info("GPT-4o Transcription Service initialized")

    

    async def transcribe(self, audio_data: np.ndarray, channel: str, sample_rate: int = None) -> Optional[Dict]:

        """

        Transcribe audio using OpenAI Whisper API

        

        Args:

            audio_data: Audio as numpy array

            channel: Channel name for logging

            sample_rate: Sample rate of the audio (if None, uses config default)

        

        Returns:

            Dictionary with transcription results or None if failed

        """

        

        try:

            # Use provided sample rate or fall back to config

            sr = sample_rate or self.sample_rate

            

            # Convert numpy array to audio file in memory

            audio_bytes = self._numpy_to_audio_bytes(audio_data, sr)

            

            # Calculate duration

            duration = len(audio_data) / sr

            

            # Check if audio is mostly silence (save API costs)

            energy = np.sqrt(np.mean(audio_data**2))

            if energy < 0.001:

                log.debug(f"Audio from {channel} is mostly silence (energy: {energy:.6f}), skipping")

                return None

            

            log.debug(f"Transcribing {duration:.2f}s audio from {channel} (sample_rate: {sr}Hz, energy: {energy:.4f})")

            

            # Call OpenAI API

            response = await self.client.audio.transcriptions.create(

                model="whisper-1",

                file=("audio.wav", audio_bytes),

                language=config.TRANSCRIPTION_LANGUAGE,

                response_format="verbose_json"

            )

            

            # Extract result

            text = response.text.strip()

            

            if not text:

                log.debug(f"No speech detected in audio from {channel}")

                return None

            

            result = {

                "text": text,

                "channel": channel,

                "timestamp": datetime.now(),

                "duration": duration,

                "confidence": getattr(response, 'confidence', None),

                "sample_rate": sr

            }

            

            log.info(f"[{channel}] Transcribed: {text}")

            

            return result

            

        except Exception as e:

            log.error(f"Transcription error for {channel}: {str(e)}")

            return None

    

    def _numpy_to_audio_bytes(self, audio_data: np.ndarray, sample_rate: int) -> bytes:

        """Convert numpy array to WAV bytes at specified sample rate"""

        

        buffer = io.BytesIO()

        sf.write(buffer, audio_data, sample_rate, format='WAV')

        buffer.seek(0)

        

        return buffer.read()

    

    async def transcribe_batch(self, audio_batches: Dict[str, np.ndarray]) -> Dict[str, Dict]:

        """

        Transcribe multiple audio chunks concurrently

        

        Args:

            audio_batches: Dict mapping channel names to audio data

        

        Returns:

            Dict mapping channel names to transcription results

        """

        

        tasks = []

        channels = []

        

        for channel, audio_data in audio_batches.items():

            tasks.append(self.transcribe(audio_data, channel))

            channels.append(channel)

        

        results = await asyncio.gather(*tasks, return_exceptions=True)

        

        return {

            channel: result 

            for channel, result in zip(channels, results)

            if result is not None and not isinstance(result, Exception)

        }

