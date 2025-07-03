"""TTS Engine Plugins Package"""

from pathlib import Path
import importlib
import pkgutil
from typing import Dict, Type

from ..tts_interface import TTSEngineInterface

# Dictionary to store loaded engine plugins
ENGINE_PLUGINS: Dict[str, Type[TTSEngineInterface]] = {}

def load_plugins() -> None:
    """Load all TTS engine plugins in this package."""
    package_dir = Path(__file__).parent
    for _, name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if not is_pkg and name != "__init__":
            try:
                module = importlib.import_module(f".{name}", package=__package__)
                if hasattr(module, "ENGINE_CLASS") and hasattr(module, "ENGINE_NAME"):
                    engine_class = getattr(module, "ENGINE_CLASS")
                    engine_name = getattr(module, "ENGINE_NAME")
                    ENGINE_PLUGINS[engine_name] = engine_class
            except Exception as e:
                print(f"Failed to load plugin {name}: {str(e)}")

# Load plugins when the package is imported
load_plugins() 