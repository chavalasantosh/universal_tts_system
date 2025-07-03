from typing import Dict, Type
from .base import TTSEngineInterface
from .plugins.edge_tts_engine import EdgeTTSEngine
from .plugins.elevenlabs_engine import ElevenLabsEngine
from .plugins.azure_tts_engine import AzureTTSEngine

class TTSEngineFactory:
    """Factory class for creating TTS engine instances"""
    
    def __init__(self):
        self._engines: Dict[str, Type[TTSEngineInterface]] = {
            "edge-tts": EdgeTTSEngine,
            "elevenlabs": ElevenLabsEngine,
            "azure-tts": AzureTTSEngine
        }
    
    def get_engine(self, engine_type: str) -> TTSEngineInterface:
        """
        Get a TTS engine instance.
        
        Args:
            engine_type: Type of engine to create
            
        Returns:
            TTS engine instance
            
        Raises:
            ValueError: If engine type is not supported
        """
        engine_class = self._engines.get(engine_type)
        if not engine_class:
            raise ValueError(f"Unsupported engine type: {engine_type}")
        return engine_class()
    
    def register_engine(self, engine_type: str, engine_class: Type[TTSEngineInterface]) -> None:
        """
        Register a new engine type.
        
        Args:
            engine_type: Type identifier for the engine
            engine_class: Engine class to register
        """
        self._engines[engine_type] = engine_class
    
    def list_engines(self) -> list[str]:
        """
        List all available engine types.
        
        Returns:
            List of engine type identifiers
        """
        return list(self._engines.keys()) 