"""Universal TTS System Package Initialization"""

__version__ = "1.0.0"
__author__ = "AI Software Architect"
__description__ = "Universal Text-to-Speech System with advanced features"

from utils.logger import TTSLogger
from utils.config_manager import ConfigManager
from utils.exceptions import TTSBaseException
from engines.tts_factory import TTSEngineFactory
from readers.reader_factory import ReaderFactory  
from profiles.voice_manager import VoiceManager

__all__ = [
    'TTSLogger',
    'ConfigManager', 
    'TTSBaseException',
    'TTSEngineFactory',
    'ReaderFactory',
    'VoiceManager'
]
