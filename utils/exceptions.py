"""Custom Exception Classes for the Universal TTS System"""

class TTSBaseException(Exception):
    """Base exception class for all TTS-related errors"""
    pass

class TTSEngineError(TTSBaseException):
    """Raised when there's an error with the TTS engine"""
    pass

class FileReaderError(TTSBaseException):
    """Raised when there's an error reading a file"""
    pass

class ConfigurationError(TTSBaseException):
    """Raised when there's an error with configuration"""
    pass

class VoiceProfileError(TTSBaseException):
    """Raised when there's an error with voice profiles"""
    pass

class FileTypeError(TTSBaseException):
    """Raised when an unsupported file type is encountered"""
    pass

class AudioOutputError(TTSBaseException):
    """Raised when there's an error saving or playing audio"""
    pass

class ValidationError(TTSBaseException):
    """Raised when input validation fails"""
    pass

class AudioCacheError(TTSBaseException):
    """Raised when there's an error with audio cache"""
    pass
