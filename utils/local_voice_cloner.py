import os
import torch
import numpy as np
from typing import Dict, Optional, List
import soundfile as sf
from TTS.api import TTS
import logging

class LocalVoiceCloner:
    """Offline voice cloning utilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize TTS with YourTTS model (works offline)
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts",
                      gpu=torch.cuda.is_available(),
                      progress_bar=False)
        
        # Voice storage
        self.voice_samples = {}
        self.voice_embeddings = {}

    def clone_voice(self, 
                   reference_audio: str, 
                   voice_name: str) -> Dict:
        """
        Clone a voice from reference audio using local model.
        
        Args:
            reference_audio: Path to reference audio file
            voice_name: Name to save the voice as
            
        Returns:
            Dict containing voice information
        """
        try:
            # Load and process reference audio
            audio, sr = sf.read(reference_audio)
            
            # Extract voice embeddings
            embeddings = self.tts.speaker_encoder.forward(torch.from_numpy(audio).float())
            
            # Store voice data
            self.voice_samples[voice_name] = {
                'audio': audio,
                'sample_rate': sr,
                'embeddings': embeddings.detach().numpy()
            }
            
            return {
                'voice_name': voice_name,
                'sample_rate': sr,
                'duration': len(audio) / sr
            }
            
        except Exception as e:
            self.logger.error(f"Error cloning voice: {str(e)}")
            raise

    def synthesize_with_cloned_voice(self,
                                   text: str,
                                   voice_name: str,
                                   output_path: str) -> str:
        """
        Synthesize speech using a cloned voice.
        
        Args:
            text: Text to synthesize
            voice_name: Name of the cloned voice to use
            output_path: Path to save the output audio
            
        Returns:
            Path to the generated audio file
        """
        try:
            if voice_name not in self.voice_samples:
                raise ValueError(f"Voice {voice_name} not found")
            
            voice_data = self.voice_samples[voice_name]
            
            # Synthesize using YourTTS
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=voice_data['audio'],
                language='en'
            )
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error synthesizing with cloned voice: {str(e)}")
            raise

    def get_cloned_voices(self) -> Dict[str, Dict]:
        """Get information about all cloned voices."""
        return {
            name: {
                'sample_rate': data['sample_rate'],
                'duration': len(data['audio']) / data['sample_rate']
            }
            for name, data in self.voice_samples.items()
        }

    def delete_cloned_voice(self, voice_name: str) -> bool:
        """Delete a cloned voice."""
        if voice_name in self.voice_samples:
            del self.voice_samples[voice_name]
            return True
        return False

    def mix_voices(self,
                  voice_names: List[str],
                  weights: Optional[List[float]] = None,
                  output_voice_name: str = None) -> Dict:
        """
        Mix multiple cloned voices.
        
        Args:
            voice_names: List of voice names to mix
            weights: Optional list of weights for each voice
            output_voice_name: Name for the mixed voice
            
        Returns:
            Dict containing mixed voice information
        """
        try:
            if not all(name in self.voice_samples for name in voice_names):
                raise ValueError("One or more voices not found")
            
            if weights is None:
                weights = [1.0 / len(voice_names)] * len(voice_names)
            
            if len(weights) != len(voice_names):
                raise ValueError("Number of weights must match number of voices")
            
            # Mix embeddings
            mixed_embedding = np.zeros_like(self.voice_samples[voice_names[0]]['embeddings'])
            for name, weight in zip(voice_names, weights):
                mixed_embedding += weight * self.voice_samples[name]['embeddings']
            
            # Store mixed voice
            if output_voice_name:
                self.voice_samples[output_voice_name] = {
                    'audio': None,  # No reference audio for mixed voice
                    'sample_rate': self.voice_samples[voice_names[0]]['sample_rate'],
                    'embeddings': mixed_embedding
                }
            
            return {
                'voice_name': output_voice_name,
                'mixed_voices': voice_names,
                'weights': weights
            }
            
        except Exception as e:
            self.logger.error(f"Error mixing voices: {str(e)}")
            raise 