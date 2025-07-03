import os
from typing import Dict, Optional
import numpy as np
import soundfile as sf
import librosa
import noisereduce as nr
from pysndfx import AudioEffectsChain
import logging

class AudioProcessor:
    """Advanced audio processing utilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load audio processing settings
        self.noise_reduction = config.get('noise_reduction', {})
        self.normalization = config.get('normalization', {})
        self.effects = config.get('effects', {})
        self.output_format = config.get('output_format', 'mp3')
        self.sample_rate = config.get('sample_rate', 44100)
        self.channels = config.get('channels', 2)

    def process_audio(self, input_path: str, output_path: str) -> str:
        """
        Process audio file with configured enhancements.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save processed audio
            
        Returns:
            Path to processed audio file
        """
        try:
            # Load audio
            audio, sr = librosa.load(input_path, sr=self.sample_rate)
            
            # Apply noise reduction if enabled
            if self.noise_reduction.get('enabled', False):
                audio = self._apply_noise_reduction(audio, sr)
            
            # Apply normalization if enabled
            if self.normalization.get('enabled', False):
                audio = self._apply_normalization(audio)
            
            # Apply audio effects if enabled
            if self.effects.get('enabled', False):
                audio = self._apply_effects(audio, sr)
            
            # Save processed audio
            sf.write(output_path, audio, sr)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            raise

    def _apply_noise_reduction(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction to audio."""
        strength = self.noise_reduction.get('strength', 0.5)
        return nr.reduce_noise(
            y=audio,
            sr=sr,
            prop_decrease=strength
        )

    def _apply_normalization(self, audio: np.ndarray) -> np.ndarray:
        """Apply audio normalization."""
        target_level = self.normalization.get('target_level', -14)
        current_level = librosa.amplitude_to_db(np.abs(audio)).mean()
        gain = target_level - current_level
        return audio * (10 ** (gain / 20))

    def _apply_effects(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply audio effects chain."""
        fx = AudioEffectsChain()
        
        # Add reverb if specified
        if self.effects.get('reverb', 0) > 0:
            fx = fx.reverb(
                reverberance=self.effects['reverb'],
                room_scale=100,
                stereo_depth=100
            )
        
        # Add echo if specified
        if self.effects.get('echo', 0) > 0:
            fx = fx.echo(
                gain_in=self.effects['echo'],
                gain_out=0.8,
                n_echos=3,
                delays=[60, 120, 180]
            )
        
        # Add compression if specified
        if self.effects.get('compression', 0) > 0:
            fx = fx.compress(
                attack=0.1,
                release=0.1,
                threshold=-20,
                ratio=4
            )
        
        return fx(audio)

    def get_audio_info(self, file_path: str) -> Dict:
        """Get audio file information."""
        try:
            info = sf.info(file_path)
            return {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format
            }
        except Exception as e:
            self.logger.error(f"Error getting audio info: {str(e)}")
            return {} 