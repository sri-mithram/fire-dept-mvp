"""
Audio Manager

Handles audio input from multiple devices/channels

"""
import asyncio

import numpy as np

import sounddevice as sd

from typing import Dict, Callable, Optional, List

from queue import Queue

import threading

import config

from utils.logger import log

class AudioManager:

    """

    Manages audio input from multiple devices

    Captures audio and routes to appropriate channels

    """

    

    def __init__(self, callback: Optional[Callable] = None):

        """

        Initialize audio manager

        

        Args:

            callback: Async callback function for audio chunks

                     Signature: async def callback(channel_id: str, audio_chunk: np.ndarray)

        """

        

        self.sample_rate = config.SAMPLE_RATE

        self.channels = config.AUDIO_CHANNELS

        self.chunk_duration = config.CHUNK_DURATION

        self.callback = callback

        

        # Audio streams

        self.streams: Dict[str, sd.InputStream] = {}

        self.audio_queues: Dict[str, Queue] = {}

        

        # Control

        self.is_running = False

        self.processing_tasks = []

        

        log.info("Audio manager initialized")

    

    def list_devices(self) -> List[Dict]:

        """List all available audio input devices"""

        

        devices = sd.query_devices()

        input_devices = []

        

        for i, device in enumerate(devices):

            if device['max_input_channels'] > 0:

                input_devices.append({

                    "index": i,

                    "name": device['name'],

                    "channels": device['max_input_channels'],

                    "sample_rate": device['default_samplerate']

                })

        

        log.info(f"Found {len(input_devices)} audio input devices")

        return input_devices

    

    def start_channel(self, channel_id: str, device_index: Optional[int] = None):

        """

        Start audio capture for a channel

        

        Args:

            channel_id: Channel identifier

            device_index: Audio device index (None = default)

        """

        

        if channel_id in self.streams:

            log.warning(f"Channel {channel_id} already started")

            return

        

        # Create queue for this channel

        self.audio_queues[channel_id] = Queue()

        

        # Audio callback for this channel

        def audio_callback(indata, frames, time_info, status):

            if status:

                log.warning(f"Audio status on {channel_id}: {status}")

            

            # Get mono audio

            audio_chunk = indata[:, 0].copy()

            

            # Put in queue

            self.audio_queues[channel_id].put(audio_chunk)

        

        # Start input stream

        try:

            stream = sd.InputStream(

                device=device_index,

                channels=self.channels,

                samplerate=self.sample_rate,

                callback=audio_callback,

                blocksize=int(self.sample_rate * self.chunk_duration)

            )

            

            stream.start()

            self.streams[channel_id] = stream

            

            log.info(f"Started audio capture for {channel_id} on device {device_index}")

            

        except Exception as e:

            log.error(f"Failed to start audio for {channel_id}: {str(e)}")

            raise

    

    def stop_channel(self, channel_id: str):

        """Stop audio capture for a channel"""

        

        if channel_id in self.streams:

            self.streams[channel_id].stop()

            self.streams[channel_id].close()

            del self.streams[channel_id]

            

            if channel_id in self.audio_queues:

                del self.audio_queues[channel_id]

            

            log.info(f"Stopped audio capture for {channel_id}")

    

    async def process_audio_queue(self, channel_id: str):

        """Process audio from queue and call callback"""

        

        queue = self.audio_queues.get(channel_id)

        if not queue:

            return

        

        log.debug(f"Started processing audio queue for {channel_id}")

        

        while self.is_running:

            try:

                # Get audio chunk (non-blocking with timeout)

                if not queue.empty():

                    audio_chunk = queue.get_nowait()

                    

                    # Call callback if provided

                    if self.callback:

                        await self.callback(channel_id, audio_chunk)

                else:

                    # Sleep briefly if queue empty

                    await asyncio.sleep(0.01)

                    

            except Exception as e:

                log.error(f"Error processing audio for {channel_id}: {str(e)}")

                await asyncio.sleep(0.1)

        

        log.debug(f"Stopped processing audio queue for {channel_id}")

    

    async def start_all(self):

        """Start audio capture for all enabled channels"""

        

        self.is_running = True

        

        # Start each channel

        for channel_id, channel_config in config.RADIO_CHANNELS.items():

            if channel_config.get("enabled", True):

                device_index = channel_config.get("device_index")

                

                try:

                    self.start_channel(channel_id, device_index)

                    

                    # Start processing task

                    task = asyncio.create_task(self.process_audio_queue(channel_id))

                    self.processing_tasks.append(task)

                    

                except Exception as e:

                    log.error(f"Failed to start channel {channel_id}: {str(e)}")

        

        log.info(f"Started audio capture for {len(self.streams)} channels")

    

    async def stop_all(self):

        """Stop audio capture for all channels"""

        

        self.is_running = False

        

        # Wait for processing tasks

        if self.processing_tasks:

            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

            self.processing_tasks = []

        

        # Stop all streams

        for channel_id in list(self.streams.keys()):

            self.stop_channel(channel_id)

        

        log.info("Stopped all audio capture")

    

    def get_status(self) -> Dict:

        """Get status of all audio channels"""

        

        return {

            channel_id: {

                "active": channel_id in self.streams,

                "queue_size": self.audio_queues[channel_id].qsize() if channel_id in self.audio_queues else 0

            }

            for channel_id in config.RADIO_CHANNELS.keys()

        }

