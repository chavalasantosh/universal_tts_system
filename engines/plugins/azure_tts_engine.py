"""Azure Cognitive Services TTS Engine Plugin for Universal TTS System"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import tempfile
import json
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime

from ..tts_interface import TTSEngineInterface
from utils.exceptions import TTSEngineError
from utils.logger import TTSLogger

class AzureTTSEngine(TTSEngineInterface):
    """Azure Cognitive Services TTS Engine implementation with advanced features"""

    def __init__(self) -> None:
        """Initialize the Azure TTS engine."""
        self._speaking = False
        self._paused = False
        self._settings: Dict[str, Any] = {
            "voice": "en-US-GuyNeural",
            "rate": 0,
            "pitch": 0,
            "style": "general",
            "style_degree": 1.0,
            "role": "Default",
            "output_format": "riff-24khz-16bit-mono-pcm"
        }
        self._logger = TTSLogger()
        self._speech_config: Optional[speechsdk.SpeechConfig] = None
        self._synthesizer: Optional[speechsdk.SpeechSynthesizer] = None
        self._voice_cache: Dict[str, Any] = {}
        self._last_voice_update: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize the Azure TTS engine with required resources."""
        try:
            # Get API credentials from environment
            subscription_key = os.getenv("AZURE_SPEECH_KEY")
            region = os.getenv("AZURE_SPEECH_REGION")
            
            if not subscription_key or not region:
                raise TTSEngineError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables must be set")
            
            # Create speech config
            self._speech_config = speechsdk.SpeechConfig(
                subscription=subscription_key,
                region=region
            )
            
            # Create synthesizer
            self._synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config
            )
            
            # Get available voices
            await self._update_voice_cache()
        except Exception as e:
            raise TTSEngineError(f"Failed to initialize Azure TTS engine: {str(e)}")

    async def _update_voice_cache(self) -> None:
        """Update the voice cache with latest available voices."""
        try:
            if not self._speech_config:
                raise TTSEngineError("Speech config not initialized")

            # Get available voices
            result = self._synthesizer.get_voices_async().get()
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices = result.voices
                self._voice_cache = {
                    voice.name: {
                        "name": voice.name,
                        "locale": voice.locale,
                        "gender": voice.gender,
                        "voice_type": voice.voice_type,
                        "style_list": voice.style_list,
                        "sample_rate_hertz": voice.sample_rate_hertz
                    }
                    for voice in voices
                }
                self._last_voice_update = datetime.now()
            else:
                raise TTSEngineError("Failed to get voices list")
        except Exception as e:
            raise TTSEngineError(f"Failed to update voice cache: {str(e)}")

    async def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the Azure TTS engine with specific settings.

        Args:
            settings: Dictionary of engine-specific settings
        """
        try:
            if not self._speech_config:
                raise TTSEngineError("Speech config not initialized")

            # Update settings with validation
            for key, value in settings.items():
                if key in self._settings:
                    if key == "voice" and value not in self._voice_cache:
                        raise TTSEngineError(f"Invalid voice: {value}")
                    if key == "rate" and not isinstance(value, (int, float)):
                        raise TTSEngineError("Rate must be a number")
                    if key == "pitch" and not isinstance(value, (int, float)):
                        raise TTSEngineError("Pitch must be a number")
                    if key == "style_degree" and not isinstance(value, (int, float)):
                        raise TTSEngineError("Style degree must be a number")
                    self._settings[key] = value

            # Apply settings to speech config
            self._speech_config.speech_synthesis_voice_name = self._settings["voice"]
            
            # Create SSML with settings
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
                <voice name="{self._settings['voice']}">
                    <prosody rate="{self._settings['rate']}%" pitch="{self._settings['pitch']}Hz">
                        <mstts:express-as style="{self._settings['style']}" 
                                         styledegree="{self._settings['style_degree']}">
                            <mstts:role role="{self._settings['role']}">
                                {{text}}
                            </mstts:role>
                        </mstts:express-as>
                    </prosody>
                </voice>
            </speak>
            """
            self._speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat[self._settings["output_format"]]
            )
        except Exception as e:
            raise TTSEngineError(f"Failed to configure Azure TTS engine: {str(e)}")

    async def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Args:
            text: Text to convert to speech
        """
        try:
            if not self._synthesizer:
                raise TTSEngineError("Synthesizer not initialized")

            self._speaking = True
            self._paused = False

            # Create SSML with text
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
                <voice name="{self._settings['voice']}">
                    <prosody rate="{self._settings['rate']}%" pitch="{self._settings['pitch']}Hz">
                        <mstts:express-as style="{self._settings['style']}" 
                                         styledegree="{self._settings['style_degree']}">
                            <mstts:role role="{self._settings['role']}">
                                {text}
                            </mstts:role>
                        </mstts:express-as>
                    </prosody>
                </voice>
            </speak>
            """

            # Synthesize and play
            result = self._synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self._speaking = False
            else:
                raise TTSEngineError(f"Speech synthesis failed: {result.reason}")

        except Exception as e:
            self._speaking = False
            raise TTSEngineError(f"Failed to speak text: {str(e)}")

    async def text_to_file(self, text: str, output_path: Union[str, Path]) -> str:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file

        Returns:
            str: Path to the saved audio file
        """
        try:
            if not self._synthesizer:
                raise TTSEngineError("Synthesizer not initialized")

            output_path = str(output_path)

            # Create SSML with text
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                   xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
                <voice name="{self._settings['voice']}">
                    <prosody rate="{self._settings['rate']}%" pitch="{self._settings['pitch']}Hz">
                        <mstts:express-as style="{self._settings['style']}" 
                                         styledegree="{self._settings['style_degree']}">
                            <mstts:role role="{self._settings['role']}">
                                {text}
                            </mstts:role>
                        </mstts:express-as>
                    </prosody>
                </voice>
            </speak>
            """

            # Create audio config for file output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config,
                audio_config=audio_config
            )

            # Synthesize to file
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return output_path
            else:
                raise TTSEngineError(f"Speech synthesis failed: {result.reason}")

        except Exception as e:
            raise TTSEngineError(f"Failed to save text to file: {str(e)}")

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the engine.

        Returns:
            List of dictionaries containing voice information
        """
        try:
            # Update cache if needed
            if not self._voice_cache or (
                self._last_voice_update and 
                (datetime.now() - self._last_voice_update).total_seconds() > 3600
            ):
                await self._update_voice_cache()

            return list(self._voice_cache.values())
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
        try:
            if not self._voice_cache:
                await self._update_voice_cache()

            if voice_id not in self._voice_cache:
                raise TTSEngineError(f"Voice not found: {voice_id}")

            return self._voice_cache[voice_id]
        except Exception as e:
            raise TTSEngineError(f"Failed to get voice info: {str(e)}")

    async def pause(self) -> None:
        """Pause the current speech output."""
        try:
            if self._speaking and not self._paused and self._synthesizer:
                self._synthesizer.pause()
                self._paused = True
        except Exception as e:
            raise TTSEngineError(f"Failed to pause speech: {str(e)}")

    async def resume(self) -> None:
        """Resume the paused speech output."""
        try:
            if self._speaking and self._paused and self._synthesizer:
                self._synthesizer.resume()
                self._paused = False
        except Exception as e:
            raise TTSEngineError(f"Failed to resume speech: {str(e)}")

    async def stop(self) -> None:
        """Stop the current speech output."""
        try:
            if self._speaking and self._synthesizer:
                self._synthesizer.stop_speaking_async()
                self._speaking = False
                self._paused = False
        except Exception as e:
            raise TTSEngineError(f"Failed to stop speech: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources used by the engine."""
        try:
            await self.stop()
            if self._synthesizer:
                self._synthesizer = None
            if self._speech_config:
                self._speech_config = None
            self._voice_cache.clear()
        except Exception as e:
            raise TTSEngineError(f"Failed to cleanup engine: {str(e)}")

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
        return "Azure Cognitive Services TTS"

    @property
    def engine_version(self) -> str:
        """Get the version of the TTS engine."""
        return speechsdk.__version__

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported audio output formats."""
        return [
            "riff-8khz-8bit-mono-mulaw",
            "riff-16khz-16bit-mono-pcm",
            "riff-24khz-16bit-mono-pcm",
            "riff-48khz-16bit-mono-pcm",
            "audio-16khz-32kbitrate-mono-mp3",
            "audio-16khz-64kbitrate-mono-mp3",
            "audio-16khz-128kbitrate-mono-mp3",
            "audio-24khz-48kbitrate-mono-mp3",
            "audio-24khz-96kbitrate-mono-mp3",
            "audio-24khz-160kbitrate-mono-mp3",
            "audio-48khz-96kbitrate-mono-mp3",
            "audio-48khz-192kbitrate-mono-mp3"
        ]

    @property
    def requires_internet(self) -> bool:
        """Check if the engine requires internet connection."""
        return True

    @property
    def max_text_length(self) -> Optional[int]:
        """Get maximum text length supported by the engine."""
        return 5000  # Azure TTS limit

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        try:
            if not self._voice_cache:
                await self._update_voice_cache()
            return list(set(voice["locale"] for voice in self._voice_cache.values()))
        except Exception:
            return []

ENGINE_NAME = "azure-tts"
ENGINE_CLASS = AzureTTSEngine 