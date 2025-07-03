#!/usr/bin/env python3
"""
Demonstration script for Universal TTS System
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import TTSLogger
from utils.config_manager import ConfigManager
from utils.file_detector import FileDetector
from engines.tts_factory import TTSEngineFactory
from readers.reader_factory import ReaderFactory
from profiles.voice_manager import VoiceManager

async def main():
    """Demo function"""
    print("🎤 Universal TTS System - Demo")
    print("=" * 40)

    try:
        # Test system initialization
        logger = TTSLogger()
        config = ConfigManager()
        detector = FileDetector()
        tts_factory = TTSEngineFactory()
        reader_factory = ReaderFactory()
        voice_manager = VoiceManager()

        print("✅ All components initialized successfully!")
        print(f"✅ Supported file types: {detector.get_supported_types()}")
        print(f"✅ Available engines: {tts_factory.list_engines()}")
        print(f"✅ Available profiles: {voice_manager.list_profiles()}")

        print("\n🎉 System is ready for use!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Try: python main.py your_file.txt")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
