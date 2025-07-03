import os
from typing import Dict, Optional
from TTS.api import TTS
from .base import BaseTTSEngine

class CoquiEngine(BaseTTSEngine):
    """Coqui TTS Engine implementation."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Load configuration
        self.model_name = config.get('model_name', 'tts_models/en/ljspeech/tacotron2-DDC')
        self.vocoder_name = config.get('vocoder_name', 'vocoder_models/en/ljspeech/hifigan_v2')
        self.gpu = config.get('use_gpu', True)
        
        # Initialize TTS
        self.tts = TTS(model_name=self.model_name, 
                      vocoder_name=self.vocoder_name,
                      gpu=self.gpu)

    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """
        Synthesize text to speech using Coqui TTS.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file
            **kwargs: Additional parameters
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Generate audio
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=kwargs.get('speaker_wav'),
                language=kwargs.get('language', 'en')
            )
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error in Coqui synthesis: {str(e)}")
            raise

    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models."""
        try:
            models = TTS().list_models()
            return {model['name']: model['description'] for model in models}
        except Exception as e:
            self.logger.error(f"Error fetching Coqui models: {str(e)}")
            return {}

    def validate_config(self) -> bool:
        """Validate the engine configuration."""
        required_fields = ['model_name']
        return all(field in self.config for field in required_fields) 