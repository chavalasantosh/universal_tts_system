"""Google TTS Engine Plugin for Universal TTS System"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import tempfile
import os
from gtts import gTTS
import pygame

from ..tts_interface import TTSEngineInterface
from utils.exceptions import TTSEngineError

class GTTSEngine(TTSEngineInterface):
    """Google TTS Engine implementation"""

    def __init__(self) -> None:
        """Initialize the Google TTS engine."""
        self._speaking = False
        self._paused = False
        self._settings: Dict[str, Any] = {
            "lang": "en",
            "slow": False
        }
        pygame.mixer.init()

    async def initialize(self) -> None:
        """Initialize the Google TTS engine with required resources."""
        try:
            # Test internet connection
            tts = gTTS(text="Test", lang="en", slow=False)
            with tempfile.NamedTemporaryFile(delete=True) as temp:
                tts.save(temp.name)
        except Exception as e:
            raise TTSEngineError(f"Failed to initialize Google TTS engine: {str(e)}")

    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the Google TTS engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        try:
            if "lang" in settings:
                self._settings["lang"] = settings["lang"]
            if "slow" in settings:
                self._settings["slow"] = settings["slow"]
        except Exception as e:
            raise TTSEngineError(f"Failed to configure Google TTS engine: {str(e)}")

    async def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Args:
            text: Text to convert to speech
        """
        try:
            self._speaking = True
            self._paused = False

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
                temp_path = temp.name

            # Generate speech
            tts = gTTS(
                text=text,
                lang=self._settings["lang"],
                slow=self._settings["slow"]
            )
            tts.save(temp_path)

            # Play audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            # Cleanup
            pygame.mixer.music.unload()
            os.unlink(temp_path)
            self._speaking = False

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
            tts = gTTS(
                text=text,
                lang=self._settings["lang"],
                slow=self._settings["slow"]
            )
            tts.save(output_path)
            return output_path
        except Exception as e:
            raise TTSEngineError(f"Failed to save text to file: {str(e)}")

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the engine.

        Returns:
            List of dictionaries containing voice information
        """
        # Google TTS doesn't provide a way to list available voices
        return []

    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice.

        Args:
            voice_id: ID of the voice to get information for

        Returns:
            Dictionary containing voice information
        """
        raise TTSEngineError("Google TTS doesn't support voice selection")

    async def pause(self) -> None:
        """Pause the current speech output."""
        try:
            if self._speaking and not self._paused:
                pygame.mixer.music.pause()
                self._paused = True
        except Exception as e:
            raise TTSEngineError(f"Failed to pause speech: {str(e)}")

    async def resume(self) -> None:
        """Resume the paused speech output."""
        try:
            if self._speaking and self._paused:
                pygame.mixer.music.unpause()
                self._paused = False
        except Exception as e:
            raise TTSEngineError(f"Failed to resume speech: {str(e)}")

    async def stop(self) -> None:
        """Stop the current speech output."""
        try:
            if self._speaking:
                pygame.mixer.music.stop()
                self._speaking = False
                self._paused = False
        except Exception as e:
            raise TTSEngineError(f"Failed to stop speech: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        try:
            await self.stop()
            pygame.mixer.quit()
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
        return "Google TTS"

    @property
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        return "2.3.2"  # gTTS version

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
        return 5000  # Google TTS limit

    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [
            "af", "ar", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en",
            "eo", "es", "et", "fi", "fr", "gu", "hi", "hr", "hu", "hy", "id",
            "is", "it", "ja", "jw", "km", "kn", "ko", "la", "lv", "mk", "ml",
            "mr", "my", "ne", "nl", "no", "pl", "pt", "ro", "ru", "si", "sk",
            "sq", "sr", "su", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk",
            "ur", "vi", "zh-CN"
        ]

ENGINE_NAME = "gtts"
ENGINE_CLASS = GTTSEngine 