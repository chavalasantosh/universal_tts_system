import os
from typing import Dict, Optional
import elevenlabs
from elevenlabs import generate, set_api_key
from .base import BaseTTSEngine

class ElevenLabsEngine(BaseTTSEngine):
    """ElevenLabs TTS Engine implementation."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        set_api_key(self.api_key)
        
        # Load configuration
        self.voice_id = config.get('voice_id', 'default')
        self.stability = config.get('stability', 0.75)
        self.similarity_boost = config.get('similarity_boost', 0.75)
        self.style = config.get('style', 0.0)
        self.use_speaker_boost = config.get('use_speaker_boost', True)

    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """
        Synthesize text to speech using ElevenLabs.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file
            **kwargs: Additional parameters
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Generate audio
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2",
                stability=self.stability,
                similarity_boost=self.similarity_boost,
                style=self.style,
                use_speaker_boost=self.use_speaker_boost
            )
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(audio)
                
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error in ElevenLabs synthesis: {str(e)}")
            raise

    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available voices."""
        try:
            voices = elevenlabs.voices()
            return {voice.name: voice.voice_id for voice in voices}
        except Exception as e:
            self.logger.error(f"Error fetching ElevenLabs voices: {str(e)}")
            return {}

    def validate_config(self) -> bool:
        """Validate the engine configuration."""
        required_fields = ['voice_id']
        return all(field in self.config for field in required_fields) 