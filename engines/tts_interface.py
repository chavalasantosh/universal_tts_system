"""TTS Engine Interface for Universal TTS System"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import asyncio

class TTSEngineInterface(ABC):
    """Abstract base class for TTS engines"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the TTS engine with required resources."""
        pass

    @abstractmethod
    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the TTS engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        pass

    @abstractmethod
    async def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Args:
            text: Text to convert to speech
        """
        pass

    @abstractmethod
    async def text_to_file(self, text: str, output_path: Union[str, Path]) -> str:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file

        Returns:
            str: Path to the saved audio file
        """
        pass

    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the engine.

        Returns:
            List of dictionaries containing voice information
        """
        pass

    @abstractmethod
    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice.

        Args:
            voice_id: ID of the voice to get information for

        Returns:
            Dictionary containing voice information
        """
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pause the current speech output."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resume the paused speech output."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the current speech output."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        pass

    @property
    @abstractmethod
    def is_speaking(self) -> bool:
        """Check if the engine is currently speaking."""
        pass

    @property
    @abstractmethod
    def is_paused(self) -> bool:
        """Check if the engine is currently paused."""
        pass

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Get the name of the TTS engine."""
        pass

    @property
    @abstractmethod
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Get list of supported audio output formats."""
        pass

    @property
    @abstractmethod
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection."""
        pass

    @property
    @abstractmethod
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine."""
        pass

    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        pass 