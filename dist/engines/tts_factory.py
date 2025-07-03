"""TTS Engine Factory for Universal TTS System"""

from typing import Dict, Type, Optional, List
import importlib
import pkg_resources
from pathlib import Path

from .tts_interface import TTSEngineInterface
from .pyttsx3_engine import PyTTSx3Engine
from utils.exceptions import TTSEngineError
from utils.logger import TTSLogger

class TTSEngineFactory:
    """Factory class for creating and managing TTS engines"""

    def __init__(self) -> None:
        """Initialize the TTS engine factory."""
        self.logger = TTSLogger()
        self._engines: Dict[str, TTSEngineInterface] = {}
        self._engine_classes: Dict[str, Type[TTSEngineInterface]] = {
            "pyttsx3": PyTTSx3Engine
        }
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load TTS engine plugins from the plugins directory."""
        try:
            plugins_dir = Path(__file__).parent / "plugins"
            if plugins_dir.exists():
                for plugin_file in plugins_dir.glob("*.py"):
                    if plugin_file.name != "__init__.py":
                        try:
                            module_name = f"engines.plugins.{plugin_file.stem}"
                            module = importlib.import_module(module_name)
                            if hasattr(module, "ENGINE_CLASS"):
                                engine_class = getattr(module, "ENGINE_CLASS")
                                engine_name = getattr(module, "ENGINE_NAME", plugin_file.stem)
                                self._engine_classes[engine_name] = engine_class
                                self.logger.info(f"Loaded TTS engine plugin: {engine_name}")
                        except Exception as e:
                            self.logger.error(f"Failed to load plugin {plugin_file.name}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to load TTS engine plugins: {str(e)}")

    def list_engines(self) -> List[str]:
        """
        Get list of available TTS engines.

        Returns:
            List of engine names
        """
        return list(self._engine_classes.keys())

    def get_engine(self, engine_name: str) -> Optional[TTSEngineInterface]:
        """
        Get or create a TTS engine instance.

        Args:
            engine_name: Name of the TTS engine to get

        Returns:
            TTS engine instance or None if engine not found
        """
        try:
            # Check if engine instance already exists
            if engine_name in self._engines:
                return self._engines[engine_name]

            # Check if engine class exists
            if engine_name not in self._engine_classes:
                self.logger.error(f"TTS engine not found: {engine_name}")
                return None

            # Create new engine instance
            engine_class = self._engine_classes[engine_name]
            engine = engine_class()
            self._engines[engine_name] = engine
            return engine

        except Exception as e:
            self.logger.error(f"Failed to get TTS engine {engine_name}: {str(e)}")
            return None

    def register_engine(self, engine_name: str, engine_class: Type[TTSEngineInterface]) -> None:
        """
        Register a new TTS engine class.

        Args:
            engine_name: Name of the TTS engine
            engine_class: TTS engine class to register
        """
        try:
            if not issubclass(engine_class, TTSEngineInterface):
                raise TTSEngineError(f"Engine class must implement TTSEngineInterface")
            
            self._engine_classes[engine_name] = engine_class
            self.logger.info(f"Registered TTS engine: {engine_name}")
        except Exception as e:
            self.logger.error(f"Failed to register TTS engine {engine_name}: {str(e)}")

    def unregister_engine(self, engine_name: str) -> None:
        """
        Unregister a TTS engine.

        Args:
            engine_name: Name of the TTS engine to unregister
        """
        try:
            if engine_name in self._engine_classes:
                del self._engine_classes[engine_name]
                if engine_name in self._engines:
                    del self._engines[engine_name]
                self.logger.info(f"Unregistered TTS engine: {engine_name}")
        except Exception as e:
            self.logger.error(f"Failed to unregister TTS engine {engine_name}: {str(e)}")

    def get_engine_info(self, engine_name: str) -> Dict:
        """
        Get information about a TTS engine.

        Args:
            engine_name: Name of the TTS engine

        Returns:
            Dictionary containing engine information
        """
        try:
            engine = self.get_engine(engine_name)
            if not engine:
                return {}

            return {
                "name": engine.engine_name,
                "version": engine.engine_version,
                "supported_formats": engine.supported_formats,
                "requires_internet": engine.requires_internet,
                "max_text_length": engine.max_text_length,
                "supported_languages": engine.supported_languages
            }
        except Exception as e:
            self.logger.error(f"Failed to get engine info for {engine_name}: {str(e)}")
            return {}

    def cleanup(self) -> None:
        """Clean up all TTS engine instances."""
        try:
            for engine in self._engines.values():
                if hasattr(engine, "cleanup"):
                    engine.cleanup()
            self._engines.clear()
            self.logger.info("Cleaned up all TTS engine instances")
        except Exception as e:
            self.logger.error(f"Failed to cleanup TTS engines: {str(e)}")
