import os
import torch
import numpy as np
from typing import Dict, Optional
import soundfile as sf
from TTS.api import TTS
from .base import BaseTTSEngine

class LocalTTSEngine(BaseTTSEngine):
    """Local TTS Engine implementation using only offline models."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Load configuration
        self.model_name = config.get('model_name', 'tts_models/en/ljspeech/tacotron2-DDC')
        self.vocoder_name = config.get('vocoder_name', 'vocoder_models/en/ljspeech/hifigan_v2')
        self.gpu = config.get('use_gpu', True)
        self.sample_rate = config.get('sample_rate', 22050)
        
        # Initialize TTS with local model
        self.tts = TTS(model_name=self.model_name, 
                      vocoder_name=self.vocoder_name,
                      gpu=self.gpu,
                      progress_bar=False)

    async def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """
        Synthesize text to speech using local model.
        
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
            self.logger.error(f"Error in local synthesis: {str(e)}")
            raise

    def get_available_models(self) -> Dict[str, str]:
        """Get list of available local models."""
        try:
            models = TTS().list_models()
            # Filter only local models
            local_models = {
                name: desc for name, desc in models.items()
                if not any(api in name.lower() for api in ['api', 'cloud', 'online'])
            }
            return local_models
        except Exception as e:
            self.logger.error(f"Error fetching local models: {str(e)}")
            return {}

    def validate_config(self) -> bool:
        """Validate the engine configuration."""
        required_fields = ['model_name']
        return all(field in self.config for field in required_fields)

    def get_voice_embeddings(self, audio_path: str) -> np.ndarray:
        """Extract voice embeddings from audio file."""
        try:
            audio, sr = sf.read(audio_path)
            # Use the TTS model's speaker encoder
            embeddings = self.tts.speaker_encoder.forward(torch.from_numpy(audio).float())
            return embeddings.detach().numpy()
        except Exception as e:
            self.logger.error(f"Error extracting voice embeddings: {str(e)}")
            return None 