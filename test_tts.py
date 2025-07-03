#!/usr/bin/env python3
"""Test script for Universal TTS System"""

import asyncio
import os
from pathlib import Path

from utils.logger import TTSLogger
from utils.config_manager import ConfigManager
from engines.factory import TTSEngineFactory
from profiles.voice_manager import VoiceManager
from utils.audio_cache import AudioCache

async def main():
    # Initialize logger
    logger = TTSLogger()
    logger.info("Starting TTS system test...")

    # Initialize configuration
    config = ConfigManager()
    config.load_config()

    # Create a test voice profile
    voice_manager = VoiceManager()
    test_profile = {
        "name": "test_voice",
        "engine": "edge-tts",
        "voice_id": "en-US-GuyNeural",
        "settings": {
            "rate": "+0%",
            "pitch": "+0Hz",
            "volume": "+0%"
        }
    }
    voice_manager.create_profile(**test_profile)
    logger.info(f"Created test voice profile: {test_profile['name']}")

    # Get TTS engine
    engine_factory = TTSEngineFactory()
    engine = engine_factory.get_engine("edge-tts")
    await engine.initialize()
    engine.configure(test_profile["settings"])
    logger.info("Initialized Edge TTS engine")

    # Test text
    test_text = "Hello! This is a test of the Universal TTS System. We are using the Edge TTS engine for this demonstration."

    # Initialize audio cache
    cache = AudioCache()
    cache.start_cleanup_task()

    try:
        # Try to get cached audio first
        cached_audio = await cache.get_cached_audio(
            test_text,
            "edge-tts",
            test_profile["voice_id"],
            test_profile["settings"]
        )

        if cached_audio:
            # Save cached audio to file
            output_path = Path("test_output_cached.mp3")
            with open(output_path, "wb") as f:
                f.write(cached_audio)
            logger.info(f"Saved cached audio to {output_path}")
        else:
            # Generate new audio
            audio_data = await engine.speak(test_text)
            
            # Save to file
            output_path = Path("test_output.mp3")
            with open(output_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"Saved new audio to {output_path}")

            # Cache the generated audio
            await cache.cache_audio(
                test_text,
                "edge-tts",
                test_profile["voice_id"],
                test_profile["settings"],
                audio_data
            )
            logger.info("Cached the generated audio")

        # Get cache statistics
        stats = cache.get_cache_stats()
        logger.info(f"Cache statistics: {stats}")

        # List available profiles
        profiles = voice_manager.list_profiles()
        logger.info(f"Available profiles: {profiles}")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
    finally:
        # Cleanup
        cache.stop_cleanup_task()
        await engine.cleanup()
        logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(main()) 