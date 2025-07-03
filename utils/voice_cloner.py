import os
import torch
import numpy as np
from typing import Dict, Optional, List
import soundfile as sf
from TTS.api import TTS
from tortoise.api import TextToSpeech
import logging

class VoiceCloner:
    """Voice cloning utilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize TTS engines
        self.coqui_tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts",
                            gpu=torch.cuda.is_available())
        self.tortoise_tts = TextToSpeech()
        
        # Voice storage
        self.voice_samples = {}
        self.voice_embeddings = {}

    def clone_voice(self, 
                   reference_audio: str, 
                   voice_name: str,
                   engine: str = 'coqui') -> Dict:
        """
        Clone a voice from reference audio.
        
        Args:
            reference_audio: Path to reference audio file
            voice_name: Name to save the voice as
            engine: TTS engine to use ('coqui' or 'tortoise')
            
        Returns:
            Dict containing voice information
        """
        try:
            # Load and process reference audio
            audio, sr = sf.read(reference_audio)
            
            if engine.lower() == 'coqui':
                # Clone using Coqui TTS
                self.voice_samples[voice_name] = {
                    'audio': audio,
                    'sample_rate': sr,
                    'engine': 'coqui'
                }
                
            elif engine.lower() == 'tortoise':
                # Clone using Tortoise TTS
                self.voice_samples[voice_name] = {
                    'audio': audio,
                    'sample_rate': sr,
                    'engine': 'tortoise'
                }
                
            else:
                raise ValueError(f"Unsupported engine: {engine}")
            
            return {
                'voice_name': voice_name,
                'engine': engine,
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
            
            if voice_data['engine'] == 'coqui':
                # Synthesize using Coqui TTS
                self.coqui_tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=voice_data['audio'],
                    language='en'
                )
                
            elif voice_data['engine'] == 'tortoise':
                # Synthesize using Tortoise TTS
                gen_audio = self.tortoise_tts.tts(
                    text=text,
                    voice_samples=voice_data['audio'],
                    preset='fast'
                )
                
                # Save audio
                gen_audio = gen_audio.squeeze().cpu().numpy()
                sf.write(output_path, gen_audio, 22050)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error synthesizing with cloned voice: {str(e)}")
            raise

    def get_cloned_voices(self) -> Dict[str, Dict]:
        """Get information about all cloned voices."""
        return {
            name: {
                'engine': data['engine'],
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