"""Configuration Manager for Universal TTS System"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from utils.exceptions import ConfigurationError

class ConfigManager:
    """Configuration manager for the TTS system"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.yaml"
        self.config: Dict[str, Any] = {}
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            # Create default configuration
            self.config = {
                "logging": {
                    "level": "INFO",
                    "file": "logs/tts.log"
                },
                "cache": {
                    "enabled": True,
                    "max_size_mb": 100,
                    "max_age_days": 7,
                    "cleanup_interval_hours": 24
                },
                "voice_profiles": {
                    "default": {
                        "engine": "edge-tts",
                        "voice_id": "en-US-GuyNeural",
                        "settings": {
                            "rate": "+0%",
                            "pitch": "+0Hz",
                            "volume": "+0%"
                        }
                    }
                },
                "file_processing": {
                    "supported_formats": [".txt", ".docx", ".pdf", ".md"],
                    "max_file_size_mb": 10
                },
                "audio_output": {
                    "default_format": "mp3",
                    "supported_formats": ["mp3", "wav", "ogg"],
                    "sample_rate": 44100,
                    "channels": 2,
                    "bitrate": "192k"
                }
            }
            self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(config_dict)
        self.save_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file and environment variables."""
        try:
            # Load default configuration
            default_config = {
                "system": {
                    "name": "Universal TTS System",
                    "version": "1.0.0",
                    "log_level": "INFO",
                    "max_file_size_mb": 100,
                    "concurrent_workers": 4
                },
                "tts_engines": {
                    "default": "pyttsx3",
                    "pyttsx3": {
                        "rate": 200,
                        "volume": 0.9
                    },
                    "gtts": {
                        "lang": "en",
                        "slow": False
                    },
                    "edge": {
                        "voice": "en-US-AriaNeural",
                        "rate": "+0%"
                    }
                }
            }

            # Try to load from config file
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._merge_configs(default_config, file_config)
                    else:
                        self.config = default_config
            else:
                self.config = default_config

            # Override with environment variables
            self._load_env_vars()

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge two configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_prefix = "TTS_"
        
        # System settings
        if os.getenv(f"{env_prefix}LOG_LEVEL"):
            self.config["system"]["log_level"] = os.getenv(f"{env_prefix}LOG_LEVEL")
        
        if os.getenv(f"{env_prefix}MAX_FILE_SIZE"):
            self.config["system"]["max_file_size_mb"] = int(os.getenv(f"{env_prefix}MAX_FILE_SIZE"))
        
        if os.getenv(f"{env_prefix}WORKERS"):
            self.config["system"]["concurrent_workers"] = int(os.getenv(f"{env_prefix}WORKERS"))

        # API Keys
        if os.getenv("ELEVENLABS_API_KEY"):
            self.config["tts_engines"]["elevenlabs"] = {
                "api_key": os.getenv("ELEVENLABS_API_KEY")
            }
        
        if os.getenv("AZURE_TTS_API_KEY"):
            self.config["tts_engines"]["azure"] = {
                "api_key": os.getenv("AZURE_TTS_API_KEY")
            }

    def validate(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            bool: True if configuration is valid
        """
        required_keys = [
            "system.name",
            "system.version",
            "system.log_level",
            "system.max_file_size_mb",
            "system.concurrent_workers",
            "tts_engines.default"
        ]

        for key in required_keys:
            if self.get(key) is None:
                raise ConfigurationError(f"Missing required configuration key: {key}")

        return True
