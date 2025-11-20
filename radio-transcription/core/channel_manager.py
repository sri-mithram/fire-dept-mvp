"""
Channel Manager

Manages multiple radio channels, routing, and state

"""



from typing import Dict, List, Optional

import asyncio

from datetime import datetime



import config

from utils.logger import log

from core.vad_detector import VADDetector

from core.transcription_service import TranscriptionService

from core.alert_system import AlertSystem

from utils.storage import save_transcript





class Channel:

    """Represents a single radio channel"""

    

    def __init__(self, channel_id: str, config_data: Dict):

        self.id = channel_id

        self.name = config_data["name"]

        self.device_index = config_data["device_index"]

        self.frequency = config_data.get("frequency", "Unknown")

        self.color = config_data.get("color", "⚪")

        self.priority = config_data.get("priority", "MEDIUM")

        self.enabled = config_data.get("enabled", True)

        

        # State

        self.is_active = False

        self.last_transmission = None

        self.transmission_count = 0

        

        # Components

        self.vad = VADDetector(sample_rate=config.SAMPLE_RATE)

        

        log.info(f"Channel initialized: {self.name} ({self.frequency})")

    

    def get_display_name(self) -> str:

        """Get formatted channel name for display"""

        return f"{self.color} {self.name}"

    

    def update_state(self, is_active: bool):

        """Update channel activity state"""

        self.is_active = is_active

        if is_active:

            self.last_transmission = datetime.now()

            self.transmission_count += 1





class ChannelManager:

    """

    Manages multiple radio channels

    Handles routing, state management, and coordination

    """

    

    def __init__(self):

        """Initialize channel manager"""

        

        self.channels: Dict[str, Channel] = {}

        self.transcription_service = TranscriptionService()

        self.alert_system = AlertSystem()

        

        # Initialize channels from config

        for channel_id, channel_config in config.RADIO_CHANNELS.items():

            if channel_config.get("enabled", True):

                self.channels[channel_id] = Channel(channel_id, channel_config)

        

        log.info(f"Channel manager initialized with {len(self.channels)} channels")

    

    def get_channel(self, channel_id: str) -> Optional[Channel]:

        """Get channel by ID"""

        return self.channels.get(channel_id)

    

    def get_all_channels(self) -> List[Channel]:

        """Get all channels"""

        return list(self.channels.values())

    

    def get_enabled_channels(self) -> List[Channel]:

        """Get only enabled channels"""

        return [ch for ch in self.channels.values() if ch.enabled]

    

    async def process_audio(self, channel_id: str, audio_chunk, sample_rate: int = None) -> Optional[Dict]:

        """

        Process audio chunk for a specific channel

        

        Args:

            channel_id: Channel identifier

            audio_chunk: Audio data as numpy array

            sample_rate: Sample rate of the audio

        

        Returns:

            Transcription result if complete utterance detected, None otherwise

        """

        

        channel = self.get_channel(channel_id)

        if not channel or not channel.enabled:

            return None

        

        # VAD detection (works with any sample rate now!)

        complete_utterance = channel.vad.process_audio(audio_chunk, sample_rate)

        

        if complete_utterance is not None:

            # Complete transmission detected

            channel.update_state(True)

            

            log.info(f"Complete transmission detected on {channel.name}")

            

            # Transcribe (passing the sample rate)

            result = await self.transcription_service.transcribe(

                complete_utterance, 

                channel.name,

                sample_rate

            )

            

            if result:

                # Check for alerts

                is_alert, keywords, priority = self.alert_system.check_for_alerts(

                    result["text"]

                )

                

                # Add channel info and alert data

                result["channel_id"] = channel_id

                result["channel_color"] = channel.color

                result["is_alert"] = is_alert

                result["alert_keywords"] = keywords

                result["alert_priority"] = priority

                

                # Save to storage

                await save_transcript(

                    channel=channel.name,

                    text=result["text"],

                    timestamp=result["timestamp"],

                    confidence=result.get("confidence"),

                    alert=is_alert,

                    alert_keywords=keywords

                )

                

                # Format alert if needed

                if is_alert:

                    result["alert_message"] = self.alert_system.format_alert_message(

                        channel=channel.name,

                        text=result["text"],

                        keywords=keywords,

                        priority=priority,

                        timestamp=result["timestamp"]

                    )

                

                channel.update_state(False)

                

                return result

        

        return None

    

    async def process_multiple_channels(self, audio_data: Dict[str, any]) -> List[Dict]:

        """

        Process audio from multiple channels concurrently

        

        Args:

            audio_data: Dict mapping channel_id to audio chunks

        

        Returns:

            List of transcription results

        """

        

        tasks = [

            self.process_audio(channel_id, audio_chunk)

            for channel_id, audio_chunk in audio_data.items()

        ]

        

        results = await asyncio.gather(*tasks, return_exceptions=True)

        

        # Filter out None and exceptions

        return [

            result for result in results 

            if result is not None and not isinstance(result, Exception)

        ]

    

    def get_channel_status(self) -> Dict:

        """Get status of all channels"""

        

        return {

            channel_id: {

                "name": channel.name,

                "enabled": channel.enabled,

                "is_active": channel.is_active,

                "frequency": channel.frequency,

                "last_transmission": channel.last_transmission.isoformat() if channel.last_transmission else None,

                "transmission_count": channel.transmission_count

            }

            for channel_id, channel in self.channels.items()

        }

