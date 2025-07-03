"""Microsoft Edge TTS Engine Plugin for Universal TTS System"""

import asyncio
import edge_tts
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import tempfile
import os
import json
import aiohttp
from datetime import datetime

from ..tts_interface import TTSEngineInterface
from utils.exceptions import TTSEngineError
from utils.logger import TTSLogger

class EdgeTTSEngine(TTSEngineInterface):
    """Microsoft Edge TTS Engine implementation with advanced features"""

    def __init__(self) -> None:
        """Initialize the Edge TTS engine."""
        self.voice = "en-US-GuyNeural"
        self.rate = "+0%"
        self.pitch = "+0Hz"
        self.volume = "+0%"
        self._speaking = False
        self._paused = False
        self._voices = []
        self._settings: Dict[str, Any] = {
            "voice": "en-US-GuyNeural",
            "rate": "+0%",
            "volume": "+0%",
            "pitch": "+0Hz",
            "style": "general",
            "style_degree": 1.0,
            "role": "Default",
            "output_format": "audio-24khz-48kbitrate-mono-mp3"
        }
        self._logger = TTSLogger()
        self._current_communication = None
        self._voice_cache: Dict[str, Any] = {}
        self._last_voice_update: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize the Edge TTS engine with required resources."""
        try:
            await self._update_voice_cache()
        except Exception as e:
            raise TTSEngineError(f"Failed to initialize Edge TTS engine: {str(e)}")

    async def _update_voice_cache(self) -> None:
        """Update the voice cache with latest available voices."""
        try:
            voices = await edge_tts.list_voices()
            if voices:
                print(f"[DEBUG] edge_tts.list_voices() first voice keys: {list(voices[0].keys())}")
            self._voices = [
                {
                    "id": voice["ShortName"],
                    "name": voice.get("LocalName", voice.get("DisplayName", voice["ShortName"])),
                    "gender": voice["Gender"],
                    "locale": voice["Locale"]
                }
                for voice in voices
            ]
            self._voice_cache = {v["ShortName"]: v for v in voices}
            self._last_voice_update = datetime.now()
        except Exception as e:
            raise TTSEngineError(f"Failed to update voice cache: {str(e)}")

    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the Edge TTS engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        try:
            # Update settings with validation
            for key, value in settings.items():
                if key in self._settings:
                    if key == "voice" and value not in self._voice_cache:
                        raise TTSEngineError(f"Invalid voice: {value}")
                    if key == "rate" and not isinstance(value, str):
                        raise TTSEngineError("Rate must be a string (e.g., '+0%')")
                    if key == "volume" and not isinstance(value, str):
                        raise TTSEngineError("Volume must be a string (e.g., '+0%')")
                    if key == "pitch" and not isinstance(value, str):
                        raise TTSEngineError("Pitch must be a string (e.g., '+0Hz')")
                    if key == "style_degree" and not isinstance(value, (int, float)):
                        raise TTSEngineError("Style degree must be a number")
                    self._settings[key] = value
        except Exception as e:
            raise TTSEngineError(f"Failed to configure Edge TTS engine: {str(e)}")

    async def speak(self, text: str) -> bytes:
        """
        Convert text to speech using Edge TTS
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes
        """
        self._speaking = True
        try:
            communicate = edge_tts.Communicate(
                text,
                self.voice,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume
            )
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        finally:
            self._speaking = False

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
                    "id": voice_id,
                    "name": voice_data["FriendlyName"],
                    "gender": voice_data["Gender"],
                    "locale": voice_data["Locale"],
                    "styles": voice_data.get("StyleList", []),
                    "roles": voice_data.get("RolePlayList", []),
                    "sample_rate": voice_data.get("SampleRateHertz", 24000)
                }
                for voice_id, voice_data in self._voice_cache.items()
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

            voice_data = self._voice_cache[voice_id]
            return {
                "id": voice_id,
                "name": voice_data["FriendlyName"],
                "gender": voice_data["Gender"],
                "locale": voice_data["Locale"],
                "styles": voice_data.get("StyleList", []),
                "roles": voice_data.get("RolePlayList", []),
                "sample_rate": voice_data.get("SampleRateHertz", 24000),
                "words_per_minute": voice_data.get("WordsPerMinute", 150),
                "status": voice_data.get("Status", "Available")
            }
        except Exception as e:
            raise TTSEngineError(f"Failed to get voice info: {str(e)}")

    async def pause(self) -> None:
        """Pause the current speech output."""
        try:
            if self._speaking and not self._paused and self._current_communication:
                await self._current_communication.pause()
                self._paused = True
        except Exception as e:
            raise TTSEngineError(f"Failed to pause speech: {str(e)}")

    async def resume(self) -> None:
        """Resume the paused speech output."""
        try:
            if self._speaking and self._paused and self._current_communication:
                await self._current_communication.resume()
                self._paused = False
        except Exception as e:
            raise TTSEngineError(f"Failed to resume speech: {str(e)}")

    async def stop(self) -> None:
        """Stop the current speech output."""
        try:
            if self._speaking and self._current_communication:
                await self._current_communication.stop()
                self._speaking = False
                self._paused = False
                self._current_communication = None
        except Exception as e:
            raise TTSEngineError(f"Failed to stop speech: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        try:
            await self.stop()
            self._voice_cache.clear()
            self._voices = []
        except Exception as e:
            raise TTSEngineError(f"Failed to cleanup engine: {str(e)}")

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
        return "Microsoft Edge TTS"

    @property
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        return edge_tts.__version__

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported audio output formats."""
        return [
            "audio-16khz-32kbitrate-mono-mp3",
            "audio-16khz-64kbitrate-mono-mp3",
            "audio-16khz-128kbitrate-mono-mp3",
            "audio-24khz-48kbitrate-mono-mp3",
            "audio-24khz-96kbitrate-mono-mp3",
            "audio-24khz-160kbitrate-mono-mp3",
            "audio-48khz-96kbitrate-mono-mp3",
            "audio-48khz-192kbitrate-mono-mp3"
        ]

    @property
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection."""
        return True

    @property
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine."""
        return 5000  # Edge TTS limit

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        try:
            if not self._voice_cache:
                await self._update_voice_cache()
            return list(set(voice["Locale"] for voice in self._voice_cache.values()))
        except Exception:
            return []

ENGINE_NAME = "edge-tts"
ENGINE_CLASS = EdgeTTSEngine 