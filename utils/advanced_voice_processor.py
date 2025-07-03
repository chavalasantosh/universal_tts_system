import os
import numpy as np
import soundfile as sf
import librosa
from typing import Dict, Optional, List, Tuple
import logging
from scipy import signal
from scipy.signal import butter, filtfilt

class AdvancedVoiceProcessor:
    """Advanced voice processing with sophisticated manipulation capabilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize processing parameters
        self.sample_rate = config.get('sample_rate', 44100)
        self.frame_length = config.get('frame_length', 2048)
        self.hop_length = config.get('hop_length', 512)
        
    def process_voice(self, input_path: str, output_path: str, effects: Optional[Dict] = None) -> str:
        """
        Process voice with advanced effects.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save processed audio
            effects: Optional dictionary of effects to apply
            
        Returns:
            Path to processed audio file
        """
        try:
            # Load audio
            audio, sr = librosa.load(input_path, sr=self.sample_rate)
            
            # Apply effects
            if effects:
                audio = self._apply_voice_effects(audio, effects)
            
            # Save processed audio
            sf.write(output_path, audio, self.sample_rate)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing voice: {str(e)}")
            raise
            
    def _apply_voice_effects(self, audio: np.ndarray, effects: Dict) -> np.ndarray:
        """Apply multiple voice effects in sequence."""
        if effects.get('formant_shift'):
            audio = self._shift_formants(audio, effects['formant_shift'])
            
        if effects.get('vocal_range'):
            audio = self._adjust_vocal_range(audio, effects['vocal_range'])
            
        if effects.get('breathiness'):
            audio = self._adjust_breathiness(audio, effects['breathiness'])
            
        if effects.get('resonance'):
            audio = self._adjust_resonance(audio, effects['resonance'])
            
        if effects.get('vibrato'):
            audio = self._add_vibrato(audio, effects['vibrato'])
            
        if effects.get('tremolo'):
            audio = self._add_tremolo(audio, effects['tremolo'])
            
        return audio
        
    def _shift_formants(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Shift formants while preserving pitch."""
        shift_factor = params.get('shift_factor', 1.0)
        
        # Compute STFT
        D = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        
        # Shift formants
        D_shifted = np.zeros_like(D)
        for i in range(D.shape[0]):
            new_idx = int(i * shift_factor)
            if new_idx < D.shape[0]:
                D_shifted[new_idx] = D[i]
                
        # Inverse STFT
        return librosa.istft(D_shifted, hop_length=self.hop_length)
        
    def _adjust_vocal_range(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Adjust vocal range while preserving formants."""
        range_factor = params.get('range_factor', 1.0)
        
        # Compute STFT
        D = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        
        # Get phase and magnitude
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Adjust magnitude
        magnitude_adjusted = magnitude ** range_factor
        
        # Reconstruct
        D_adjusted = magnitude_adjusted * np.exp(1j * phase)
        
        # Inverse STFT
        return librosa.istft(D_adjusted, hop_length=self.hop_length)
        
    def _adjust_breathiness(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Adjust breathiness of voice."""
        breathiness = params.get('amount', 0.5)
        
        # Compute STFT
        D = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        
        # Get magnitude and phase
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Add noise to magnitude
        noise = np.random.normal(0, breathiness, magnitude.shape)
        magnitude_noisy = magnitude + noise
        
        # Reconstruct
        D_noisy = magnitude_noisy * np.exp(1j * phase)
        
        # Inverse STFT
        return librosa.istft(D_noisy, hop_length=self.hop_length)
        
    def _adjust_resonance(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Adjust vocal resonance."""
        resonance = params.get('amount', 0.5)
        freq = params.get('frequency', 1000)
        
        # Design resonant filter
        b, a = self._design_resonant_filter(freq, resonance, self.sample_rate)
        
        # Apply filter
        return filtfilt(b, a, audio)
        
    def _add_vibrato(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Add vibrato effect."""
        rate = params.get('rate', 5.0)
        depth = params.get('depth', 0.5)
        
        # Generate vibrato modulation
        t = np.arange(len(audio)) / self.sample_rate
        modulation = depth * np.sin(2 * np.pi * rate * t)
        
        # Apply modulation
        return librosa.effects.pitch_shift(
            audio,
            sr=self.sample_rate,
            n_steps=modulation
        )
        
    def _add_tremolo(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Add tremolo effect."""
        rate = params.get('rate', 5.0)
        depth = params.get('depth', 0.5)
        
        # Generate tremolo modulation
        t = np.arange(len(audio)) / self.sample_rate
        modulation = 1 + depth * np.sin(2 * np.pi * rate * t)
        
        # Apply modulation
        return audio * modulation
        
    def _design_resonant_filter(self, freq: float, resonance: float, fs: float) -> Tuple[np.ndarray, np.ndarray]:
        """Design a resonant filter."""
        w0 = 2 * np.pi * freq / fs
        alpha = np.sin(w0) / (2 * resonance)
        
        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        
        return np.array([b0, b1, b2]), np.array([a0, a1, a2])
        
    def analyze_voice(self, audio_path: str) -> Dict:
        """Analyze voice characteristics."""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Compute features
            pitch, _ = librosa.piptrack(y=audio, sr=sr)
            pitch_mean = np.mean(pitch[pitch > 0])
            
            # Spectral features
            S = np.abs(librosa.stft(audio))
            spectral_centroid = librosa.feature.spectral_centroid(S=S)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=S)[0]
            
            # Energy features
            rms = librosa.feature.rms(y=audio)[0]
            
            # Formant estimation
            formants = self._estimate_formants(audio)
            
            return {
                'pitch_mean': pitch_mean,
                'spectral_centroid_mean': np.mean(spectral_centroid),
                'spectral_rolloff_mean': np.mean(spectral_rolloff),
                'rms_mean': np.mean(rms),
                'formants': formants
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing voice: {str(e)}")
            raise
            
    def _estimate_formants(self, audio: np.ndarray) -> List[float]:
        """Estimate formant frequencies."""
        # Compute LPC coefficients
        lpc_coeffs = librosa.lpc(audio, order=8)
        
        # Find roots of LPC polynomial
        roots = np.roots(lpc_coeffs)
        
        # Get angles of roots
        angles = np.angle(roots)
        
        # Convert to frequencies
        freqs = angles * self.sample_rate / (2 * np.pi)
        
        # Get positive frequencies
        freqs = freqs[freqs > 0]
        
        # Sort and get first few formants
        freqs = np.sort(freqs)
        return freqs[:3].tolist() 