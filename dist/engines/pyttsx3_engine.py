"""PyTTSx3 TTS Engine Implementation"""

import asyncio
import pyttsx3
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import threading
from queue import Queue
import time
import tempfile
import os
import wave

from .tts_interface import TTSEngineInterface
from utils.exceptions import TTSEngineError

class PyTTSx3Engine(TTSEngineInterface):
    """PyTTSx3 TTS Engine implementation"""

    def __init__(self) -> None:
        """Initialize the PyTTSx3 engine."""
        self._engine: Optional[pyttsx3.Engine] = None
        self._speaking = False
        self._paused = False
        self._stop_requested = False
        self._text_queue: Queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._settings: Dict[str, Any] = {}
        self._current_voice: Optional[Dict[str, Any]] = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the PyTTSx3 engine with required resources."""
        if not self.initialized:
            try:
                self._engine = pyttsx3.init()
                self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
                self._worker_thread.start()
                self.initialized = True
            except Exception as e:
                raise TTSEngineError(f"Failed to initialize PyTTSx3 engine: {str(e)}")

    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the PyTTSx3 engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        if not self.initialized:
            await self.initialize()

        try:
            self._settings = settings

            # Configure rate
            if "rate" in settings:
                self._engine.setProperty("rate", settings["rate"])

            # Configure volume
            if "volume" in settings:
                self._engine.setProperty("volume", settings["volume"])

            # Configure voice
            if "voice" in settings:
                voices = self._engine.getProperty("voices")
                for voice in voices:
                    if voice.id == settings["voice"]:
                        self._engine.setProperty("voice", voice.id)
                        self._current_voice = {
                            "id": voice.id,
                            "name": voice.name,
                            "languages": [voice.languages[0].decode() if voice.languages else "en"],
                            "gender": voice.gender,
                            "age": voice.age
                        }
                        break

        except Exception as e:
            raise TTSEngineError(f"Failed to configure PyTTSx3 engine: {str(e)}")

    async def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Args:
            text: Text to convert to speech
        """
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            self._text_queue.put(text)
            self._speaking = True
            self._stop_requested = False
            self._paused = False

            # Run in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._engine.say, text)
            await loop.run_in_executor(None, self._engine.runAndWait)
        except Exception as e:
            raise TTSEngineError(f"Failed to speak text: {str(e)}")

    async def text_to_file(self, text: str, output_path: Union[str, Path], append: bool = False) -> str:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            append: Whether to append to an existing file

        Returns:
            str: Path to the saved audio file
        """
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            output_path = str(output_path)
            if output_path.lower().endswith('.mp3'):
                output_path = output_path[:-4] + '.wav'
            # Create a temporary file for this chunk
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name

            # Save the chunk to temporary file
            self._engine.save_to_file(text, temp_path)
            self._engine.runAndWait()

            if append and os.path.exists(output_path):
                # Combine the audio files
                with wave.open(output_path, 'rb') as existing_file:
                    existing_params = existing_file.getparams()
                    existing_frames = existing_file.readframes(existing_file.getnframes())

                with wave.open(temp_path, 'rb') as new_file:
                    new_frames = new_file.readframes(new_file.getnframes())

                # Combine the frames
                combined_frames = existing_frames + new_frames

                # Write the combined audio
                with wave.open(output_path, 'wb') as output_file:
                    output_file.setparams(existing_params)
                    output_file.writeframes(combined_frames)
            else:
                # Just copy the temporary file to the output path
                with open(temp_path, 'rb') as src, open(output_path, 'wb') as dst:
                    dst.write(src.read())

            # Clean up temporary file
            os.unlink(temp_path)
            return output_path
        except Exception as e:
            raise TTSEngineError(f"Failed to save text to file: {str(e)}")

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the engine.

        Returns:
            List of dictionaries containing voice information
        """
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            voices = self._engine.getProperty("voices")
            return [{
                "id": voice.id,
                "name": voice.name,
                "languages": [voice.languages[0].decode() if voice.languages else "en"],
                "gender": voice.gender,
                "age": voice.age
            } for voice in voices]
        except Exception as e:
            raise TTSEngineError(f"Failed to get available voices: {str(e)}")

    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice.

        Args:
            voice_id: ID of the voice to get information for

        Returns:
            Dictionary containing voice information
        """
        if not self._engine:
            raise TTSEngineError("Engine not initialized")
        voices = self._engine.getProperty("voices")
        for voice in voices:
            if voice.id == voice_id:
                return {
                    "id": voice.id,
                    "name": voice.name,
                    "languages": [voice.languages[0].decode() if voice.languages else "en"],
                    "gender": voice.gender,
                    "age": voice.age
                }
        raise TTSEngineError(f"Voice not found: {voice_id}")

    async def pause(self) -> None:
        """Pause the current speech output."""
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            self._engine.stop()
            self._paused = True
        except Exception as e:
            raise TTSEngineError(f"Failed to pause speech: {str(e)}")

    async def resume(self) -> None:
        """Resume the paused speech output."""
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            self._paused = False
            if not self._text_queue.empty():
                text = self._text_queue.get()
                await self.speak(text)
        except Exception as e:
            raise TTSEngineError(f"Failed to resume speech: {str(e)}")

    async def stop(self) -> None:
        """Stop the current speech output."""
        if not self._engine:
            raise TTSEngineError("Engine not initialized")

        try:
            self._engine.stop()
            self._stop_requested = True
            self._speaking = False
            self._paused = False
            while not self._text_queue.empty():
                self._text_queue.get()
        except Exception as e:
            raise TTSEngineError(f"Failed to stop speech: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        try:
            await self.stop()
            if self._engine:
                self._engine = None
        except Exception as e:
            raise TTSEngineError(f"Failed to cleanup engine: {str(e)}")

    def _process_queue(self) -> None:
        """Process the text queue in a separate thread."""
        while True:
            if not self._text_queue.empty() and not self._stop_requested:
                text = self._text_queue.get()
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"Error processing text: {str(e)}")
            time.sleep(0.1)

    @property
    def is_speaking(self) -> bool:
        """Check if the engine is currently speaking."""
        return self._speaking

    @property
    def is_paused(self) -> bool:
        """Check if the engine is currently paused."""
        return self._paused

    @property
    def engine_name(self) -> str:
        """Get the name of the TTS engine."""
        return "PyTTSx3"

    @property
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        return pyttsx3.__version__

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported audio output formats."""
        return ["wav"]

    @property
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection."""
        return False

    @property
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine."""
        return None  # PyTTSx3 doesn't have a strict limit

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        if not self._engine:
            return []
        voices = self._engine.getProperty("voices")
        languages = set()
        for voice in voices:
            if voice.languages:
                languages.add(voice.languages[0].decode())
        return list(languages)

    # Remove duplicate method
    # def get_supported_languages(self):
    #     return ['en'] 