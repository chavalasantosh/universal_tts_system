import numpy as np
from scipy import signal
import librosa
import soundfile as sf
from typing import Tuple, List, Optional
import os

class VoiceCloner:
    """Offline voice cloning using traditional signal processing techniques"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.n_fft = 2048
        self.hop_length = 512
        self.n_mels = 80
        
    def extract_features(self, audio_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract pitch and formant features from audio
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # Extract pitch using YIN algorithm
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Extract formants using LPC
        formants = self._extract_formants(y, sr)
        
        return pitches, formants
    
    def _extract_formants(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Extract formants using Linear Predictive Coding (LPC)
        """
        # Pre-emphasis
        pre_emphasis = 0.97
        emphasized_audio = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
        
        # Frame the signal
        frame_length = int(0.025 * sr)
        frame_step = int(0.010 * sr)
        frames = librosa.util.frame(emphasized_audio, frame_length=frame_length, hop_length=frame_step)
        
        # Apply window
        window = np.hamming(frame_length)
        windowed_frames = frames * window[:, np.newaxis]
        
        # Calculate LPC coefficients
        lpc_order = 12
        lpc_coeffs = np.zeros((lpc_order + 1, frames.shape[1]))
        
        for i in range(frames.shape[1]):
            lpc_coeffs[:, i] = librosa.lpc(windowed_frames[:, i], order=lpc_order)
        
        return lpc_coeffs
    
    def clone_voice(self, source_audio: str, target_text: str, output_path: str) -> bool:
        """
        Clone voice from source audio to target text
        """
        try:
            # Extract features from source audio
            pitches, formants = self.extract_features(source_audio)
            
            # Generate base speech using pyttsx3
            import pyttsx3
            engine = pyttsx3.init()
            
            # Save temporary base speech
            temp_path = "temp_base.wav"
            engine.save_to_file(target_text, temp_path)
            engine.runAndWait()
            
            # Load base speech
            base_audio, sr = librosa.load(temp_path, sr=self.sample_rate)
            
            # Apply voice characteristics
            modified_audio = self._apply_voice_characteristics(base_audio, pitches, formants)
            
            # Save result
            sf.write(output_path, modified_audio, self.sample_rate)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return True
            
        except Exception as e:
            print(f"Error in voice cloning: {str(e)}")
            return False
    
    def _apply_voice_characteristics(self, 
                                   base_audio: np.ndarray, 
                                   pitches: np.ndarray, 
                                   formants: np.ndarray) -> np.ndarray:
        """
        Apply voice characteristics from source to base audio
        """
        # Resample pitches to match base audio length
        target_length = len(base_audio)
        pitches_resampled = signal.resample(pitches, target_length)
        
        # Apply pitch modification
        modified_audio = librosa.effects.pitch_shift(
            base_audio,
            sr=self.sample_rate,
            n_steps=np.mean(pitches_resampled)
        )
        
        # Apply formant modification
        modified_audio = self._apply_formant_modification(modified_audio, formants)
        
        return modified_audio
    
    def _apply_formant_modification(self, 
                                  audio: np.ndarray, 
                                  formants: np.ndarray) -> np.ndarray:
        """
        Apply formant modification using LPC analysis/synthesis
        """
        # Calculate LPC coefficients for base audio
        lpc_order = 12
        lpc_coeffs = librosa.lpc(audio, order=lpc_order)
        
        # Modify LPC coefficients based on target formants
        modified_coeffs = np.mean(formants, axis=1)
        
        # Apply modified coefficients
        modified_audio = signal.lfilter([1], modified_coeffs, audio)
        
        return modified_audio 