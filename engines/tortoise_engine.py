import os
import torch
from typing import Dict, Optional
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices
from .base import BaseTTSEngine

class TortoiseEngine(BaseTTSEngine):
    """Tortoise TTS Engine implementation."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Load configuration
        self.preset = config.get('preset', 'fast')
        self.voice = config.get('voice', 'random')
        self.use_deterministic_seed = config.get('use_deterministic_seed', False)
        self.seed = config.get('seed', None)
        
        # Initialize TTS
        self.tts = TextToSpeech()
        
        # Load voice samples if provided
        self.voice_samples = None
        if isinstance(self.voice, str) and self.voice != 'random':
            self.voice_samples = load_voice(self.voice)
        elif isinstance(self.voice, list):
            self.voice_samples = load_voices(self.voice)

    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """
        Synthesize text to speech using Tortoise TTS.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file
            **kwargs: Additional parameters
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Generate audio
            gen_audio = self.tts.tts(
                text=text,
                voice_samples=self.voice_samples,
                preset=self.preset,
                use_deterministic_seed=self.use_deterministic_seed,
                seed=self.seed
            )
            
            # Convert to numpy array and save
            gen_audio = gen_audio.squeeze().cpu().numpy()
            import soundfile as sf
            sf.write(output_path, gen_audio, 22050)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error in Tortoise synthesis: {str(e)}")
            raise

    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available voices."""
        try:
            voices = self.tts.available_voices
            return {voice: f"Tortoise voice: {voice}" for voice in voices}
        except Exception as e:
            self.logger.error(f"Error fetching Tortoise voices: {str(e)}")
            return {}

    def validate_config(self) -> bool:
        """Validate the engine configuration."""
        required_fields = ['preset']
        return all(field in self.config for field in required_fields)

    def set_voice(self, voice: str) -> None:
        """Set or update the voice."""
        self.voice = voice
        if voice != 'random':
            self.voice_samples = load_voice(voice)
        else:
            self.voice_samples = None 