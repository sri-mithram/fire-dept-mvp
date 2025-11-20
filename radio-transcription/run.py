"""
Main entry point for Radio Transcription Backend

Runs the FastAPI server with uvicorn

"""
import sys

import asyncio

from pathlib import Path

# Add project root to path

sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

import config

from utils.logger import log

def main():

    """Main entry point"""

    

    log.info("="*70)

    log.info("Radio Transcription Backend")

    log.info("Multi-channel radio transcription powered by GPT-4o")

    log.info("="*70)

    

    # Check OpenAI API key

    if not config.OPENAI_API_KEY:

        log.error("OPENAI_API_KEY not found in environment variables!")

        log.error("Please set OPENAI_API_KEY in your .env file")

        sys.exit(1)

    

    log.info(f"OpenAI API key configured: {config.OPENAI_API_KEY[:10]}...")

    

    # Display configuration

    log.info("")

    log.info("Configuration:")

    log.info(f"  Host: {config.API_HOST}")

    log.info(f"  Port: {config.API_PORT}")

    log.info(f"  Channels configured: {len(config.RADIO_CHANNELS)}")

    log.info(f"  Log level: {config.LOG_LEVEL}")

    log.info("")

    

    for channel_id, channel_config in config.RADIO_CHANNELS.items():

        if channel_config.get("enabled", True):

            log.info(f"  {channel_config.get('color', '⚪')} {channel_config['name']}: {channel_config.get('frequency', 'Unknown')}")

    

    log.info("")

    log.info("Starting server...")

    log.info("="*70)

    log.info("")

    

    # Run uvicorn server

    uvicorn.run(

        "api.server:app",

        host=config.API_HOST,

        port=config.API_PORT,

        reload=config.API_RELOAD,

        log_level=config.LOG_LEVEL.lower()

    )

if __name__ == "__main__":

    main()

