"""ElevenLabs TTS Engine Plugin for Universal TTS System"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import tempfile
import json
import aiohttp
from datetime import datetime
from elevenlabs import Voice, VoiceSettings, generate, play, set_api_key, voices

from ..tts_interface import TTSEngineInterface
from utils.exceptions import TTSEngineError
from utils.logger import TTSLogger

class ElevenLabsEngine(TTSEngineInterface):
    """ElevenLabs TTS Engine implementation with advanced features"""

    def __init__(self) -> None:
        """Initialize the ElevenLabs TTS engine."""
        self._speaking = False
        self._paused = False
        self._settings: Dict[str, Any] = {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Default voice ID
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "model_id": "eleven_monolingual_v1"
        }
        self._logger = TTSLogger()
        self._voice_cache: Dict[str, Any] = {}
        self._last_voice_update: Optional[datetime] = None
        self._api_key: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize the ElevenLabs TTS engine with required resources."""
        try:
            # Get API key from environment
            self._api_key = os.getenv("ELEVENLABS_API_KEY")
            if not self._api_key:
                raise TTSEngineError("ELEVENLABS_API_KEY environment variable not set")
            
            set_api_key(self._api_key)
            await self._update_voice_cache()
        except Exception as e:
            raise TTSEngineError(f"Failed to initialize ElevenLabs TTS engine: {str(e)}")

    async def _update_voice_cache(self) -> None:
        """Update the voice cache with latest available voices."""
        try:
            available_voices = voices()
            self._voice_cache = {voice.voice_id: voice for voice in available_voices}
            self._last_voice_update = datetime.now()
        except Exception as e:
            raise TTSEngineError(f"Failed to update voice cache: {str(e)}")

    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the ElevenLabs TTS engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        try:
            # Update settings with validation
            for key, value in settings.items():
                if key in self._settings:
                    if key == "voice_id" and value not in self._voice_cache:
                        raise TTSEngineError(f"Invalid voice ID: {value}")
                    if key in ["stability", "similarity_boost", "style"] and not 0 <= value <= 1:
                        raise TTSEngineError(f"{key} must be between 0 and 1")
                    if key == "use_speaker_boost" and not isinstance(value, bool):
                        raise TTSEngineError("use_speaker_boost must be a boolean")
                    self._settings[key] = value
        except Exception as e:
            raise TTSEngineError(f"Failed to configure ElevenLabs TTS engine: {str(e)}")

    async def speak(self, text: str) -> bytes:
        """
        Convert text to speech and return audio data.

        Args:
            text: Text to convert to speech

        Returns:
            bytes: Audio data
        """
        try:
            self._speaking = True
            self._paused = False

            # Create voice settings
            voice_settings = VoiceSettings(
                stability=self._settings["stability"],
                similarity_boost=self._settings["similarity_boost"],
                style=self._settings["style"],
                use_speaker_boost=self._settings["use_speaker_boost"]
            )

            # Generate audio
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=self._settings["voice_id"],
                    settings=voice_settings
                ),
                model=self._settings["model_id"]
            )
            
            self._speaking = False
            return audio

        except Exception as e:
            self._speaking = False
            raise TTSEngineError(f"Failed to speak text: {str(e)}")

    async def text_to_file(self, text: str, output_path: Union[str, Path]) -> str:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file

        Returns:
            str: Path to the saved audio file
        """
        try:
            output_path = str(output_path)
            audio_data = await self.speak(text)
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            return output_path
        except Exception as e:
            raise TTSEngineError(f"Failed to save text to file: {str(e)}")

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the engine.

        Returns:
            List of dictionaries containing voice information
        """
        try:
            # Update cache if needed
            if not self._voice_cache or (
                self._last_voice_update and 
                (datetime.now() - self._last_voice_update).total_seconds() > 3600
            ):
                await self._update_voice_cache()

            return [
                {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "description": voice.labels.get("description", ""),
                    "accent": voice.labels.get("accent", ""),
                    "age": voice.labels.get("age", ""),
                    "gender": voice.labels.get("gender", ""),
                    "use_case": voice.labels.get("use case", ""),
                    "preview_url": voice.preview_url
                }
                for voice in self._voice_cache.values()
            ]
        except Exception as e:
            raise TTSEngineError(f"Failed to get available voices: {str(e)}")

    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice.

        Args:
            voice_id: ID of the voice to get information for

        Returns:
            Dictionary containing voice information
        """
        try:
            if not self._voice_cache:
                await self._update_voice_cache()

            if voice_id not in self._voice_cache:
                raise TTSEngineError(f"Voice not found: {voice_id}")

            voice = self._voice_cache[voice_id]
            return {
                "id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "description": voice.labels.get("description", ""),
                "accent": voice.labels.get("accent", ""),
                "age": voice.labels.get("age", ""),
                "gender": voice.labels.get("gender", ""),
                "use_case": voice.labels.get("use case", ""),
                "preview_url": voice.preview_url,
                "settings": {
                    "stability": voice.settings.stability,
                    "similarity_boost": voice.settings.similarity_boost,
                    "style": voice.settings.style,
                    "use_speaker_boost": voice.settings.use_speaker_boost
                }
            }
        except Exception as e:
            raise TTSEngineError(f"Failed to get voice info: {str(e)}")

    async def pause(self) -> None:
        """Pause the current speech output."""
        if self._speaking and not self._paused:
            self._paused = True

    async def resume(self) -> None:
        """Resume the paused speech output."""
        if self._speaking and self._paused:
            self._paused = False

    async def stop(self) -> None:
        """Stop the current speech output."""
        self._speaking = False
        self._paused = False

    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        await self.stop()
        self._voice_cache.clear()

    @property
    def is_speaking(self) -> bool:
        """Check if the engine is currently speaking."""
        return self._speaking

    @property
    def is_paused(self) -> bool:
        """Check if the engine is currently paused."""
        return self._paused

    @property
    def engine_name(self) -> str:
        """Get the name of the TTS engine."""
        return "ElevenLabs"

    @property
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        return "2.1.0"  # Current version of elevenlabs package

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported audio output formats."""
        return ["mp3"]

    @property
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection."""
        return True

    @property
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine."""
        return 5000  # ElevenLabs limit

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ["en-US"]  # ElevenLabs currently only supports English 

ENGINE_NAME = "elevenlabs"
ENGINE_CLASS = ElevenLabsEngine 