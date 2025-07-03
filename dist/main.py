#!/usr/bin/env python3
"""
Universal Text-to-Speech System
Main entry point for the CLI interface
"""

import argparse
import asyncio
import sys
import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import TTSLogger
from utils.config_manager import ConfigManager
from utils.file_detector import FileDetector
from engines.tts_factory import TTSEngineFactory
from readers.reader_factory import ReaderFactory
from profiles.voice_manager import VoiceManager
from utils.exceptions import (
    TTSBaseException, TTSEngineError, FileReaderError,
    ConfigurationError, VoiceProfileError, FileTypeError,
    AudioOutputError, ValidationError
)

class UniversalTTSSystem:
    """Main TTS system controller"""

    def __init__(self) -> None:
        """Initialize the TTS system with all required components."""
        try:
            self.logger = TTSLogger()
            self.config = ConfigManager()
            self.file_detector = FileDetector()
            self.tts_factory = TTSEngineFactory()
            self.reader_factory = ReaderFactory()
            self.voice_manager = VoiceManager()
            self.logger.info("Universal TTS System initialized")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize TTS system: {str(e)}")

    async def process_file(
        self,
        file_path: str,
        voice_profile: str = "default",
        output_format: str = "mp3",
        save_audio: bool = False
    ) -> Optional[str]:
        """
        Process a single file with TTS.

        Args:
            file_path: Path to the file to process
            voice_profile: Name of the voice profile to use
            output_format: Format for the output audio file
            save_audio: Whether to save the audio to a file

        Returns:
            Optional[str]: Path to the output file if save_audio is True, None otherwise

        Raises:
            FileTypeError: If the file type is not supported
            FileReaderError: If there's an error reading the file
            VoiceProfileError: If the voice profile is invalid
            TTSEngineError: If there's an error with the TTS engine
            AudioOutputError: If there's an error saving or playing audio
            ValidationError: If input validation fails
        """
        try:
            # Validate inputs
            if not os.path.exists(file_path):
                raise ValidationError(f"File not found: {file_path}")
            if not output_format in ["mp3", "wav", "ogg"]:
                raise ValidationError(f"Unsupported output format: {output_format}")

            self.logger.info(f"Processing file: {file_path}")
            
            # Detect file type and validate
            file_type = self.file_detector.detect_file_type(file_path)
            print(f"[DEBUG] Detected file type: {file_type}")
            if not file_type:
                raise FileTypeError(f"Unsupported file type: {file_path}")

            # Get appropriate reader
            reader = self.reader_factory.get_reader(file_type)
            print(f"[DEBUG] Selected reader: {type(reader).__name__ if reader else None}")
            if not reader:
                raise FileReaderError(f"No reader available for file type: {file_type}")

            # Extract text in chunks
            print("Extracting text from file...")
            text_chunks = reader.extract_text_chunks(file_path, chunk_size=1000)
            if not text_chunks:
                raise FileReaderError(f"No text content found in {file_path}")

            # Get voice profile settings
            profile = self.voice_manager.get_profile(voice_profile)
            
            # Initialize TTS engine (using pyttsx3)
            engine = self.tts_factory.get_engine("pyttsx3")
            if not engine:
                raise TTSEngineError("Failed to initialize TTS engine: pyttsx3")
            
            await engine.initialize()
            await engine.configure(profile)

            # Process text-to-speech
            if save_audio:
                # Create output filename based on the input filename
                input_path = Path(file_path)
                output_path = f"{input_path.stem}.{output_format}"
                print(f"Saving audio to: {output_path}")
                
                # Combine all chunks into one text
                full_text = " ".join(text_chunks)
                print(f"Processing {len(text_chunks)} chunks as a single text...")
                
                # Save to file
                await engine.text_to_file(full_text, output_path)
                
                self.logger.info(f"Audio saved to: {output_path}")
                return output_path
            else:
                # Play audio directly
                for i, chunk in enumerate(text_chunks, 1):
                    print(f"Processing chunk {i}/{len(text_chunks)} ({(i/len(text_chunks))*100:.1f}%)")
                    await engine.speak(chunk)
                return None

        except TTSBaseException as e:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            raise

async def main() -> None:
    """Main entry point for the CLI interface."""
    parser = argparse.ArgumentParser(description="Universal Text-to-Speech System")
    parser.add_argument("files", nargs="+", help="File(s) to process")
    parser.add_argument("--voice", "-v", default="default", help="Voice profile to use")
    parser.add_argument("--save", "-s", action="store_true", help="Save audio to file")
    parser.add_argument("--format", "-f", default="mp3", choices=["mp3", "wav", "ogg"],
                       help="Output audio format (default: mp3)")

    args = parser.parse_args()

    try:
        tts_system = UniversalTTSSystem()
        
        for file_path in args.files:
            try:
                await tts_system.process_file(
                    file_path,
                    args.voice,
                    args.format,
                    save_audio=args.save
                )
            except TTSBaseException as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


