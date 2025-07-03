from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class TTSEngineInterface(ABC):
    """Base interface for TTS engines"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the TTS engine"""
        pass
    
    @abstractmethod
    def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the TTS engine with specific settings
        
        Args:
            settings: Dictionary of engine-specific settings
        """
        pass
    
    @abstractmethod
    async def speak(self, text: str) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes
        """
        pass
    
    @abstractmethod
    async def text_to_file(self, text: str, output_path: str) -> None:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
        """
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices
        
        Returns:
            List of voice information dictionaries
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the engine"""
        pass
    
    @property
    @abstractmethod
    def is_speaking(self) -> bool:
        """Check if the engine is currently speaking"""
        pass
    
    @property
    @abstractmethod
    def is_paused(self) -> bool:
        """Check if the engine is paused"""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        pass
    
    @property
    @abstractmethod
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection"""
        pass
    
    @property
    @abstractmethod
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine"""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        pass 