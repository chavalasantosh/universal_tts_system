import numpy as np
import librosa
from typing import Dict, Optional, Tuple, List
import logging
from scipy import signal
from scipy.signal import butter, filtfilt

class SpectralProcessor:
    """Advanced spectral processing with sophisticated manipulation capabilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize processing parameters
        self.sample_rate = config.get('sample_rate', 44100)
        self.frame_length = config.get('frame_length', 2048)
        self.hop_length = config.get('hop_length', 512)
        
    def process_spectrum(self, audio: np.ndarray, effects: Optional[Dict] = None) -> np.ndarray:
        """
        Process audio spectrum with advanced effects.
        
        Args:
            audio: Input audio signal
            effects: Optional dictionary of effects to apply
            
        Returns:
            Processed audio signal
        """
        try:
            # Compute STFT
            D = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
            
            # Apply effects
            if effects:
                D = self._apply_spectral_effects(D, effects)
            
            # Inverse STFT
            return librosa.istft(D, hop_length=self.hop_length)
            
        except Exception as e:
            self.logger.error(f"Error processing spectrum: {str(e)}")
            raise
            
    def _apply_spectral_effects(self, D: np.ndarray, effects: Dict) -> np.ndarray:
        """Apply multiple spectral effects in sequence."""
        if effects.get('spectral_shaping'):
            D = self._apply_spectral_shaping(D, effects['spectral_shaping'])
            
        if effects.get('harmonic_enhancement'):
            D = self._enhance_harmonics(D, effects['harmonic_enhancement'])
            
        if effects.get('noise_gate'):
            D = self._apply_noise_gate(D, effects['noise_gate'])
            
        if effects.get('spectral_compression'):
            D = self._apply_spectral_compression(D, effects['spectral_compression'])
            
        if effects.get('phase_correction'):
            D = self._correct_phase(D, effects['phase_correction'])
            
        return D
        
    def _apply_spectral_shaping(self, D: np.ndarray, params: Dict) -> np.ndarray:
        """Apply spectral shaping to enhance or reduce specific frequency bands."""
        shape_factor = params.get('shape_factor', 1.0)
        bands = params.get('bands', [
            {'freq_low': 0, 'freq_high': 100, 'gain': 1.0},
            {'freq_low': 100, 'freq_high': 300, 'gain': 1.0},
            {'freq_low': 300, 'freq_high': 1000, 'gain': 1.0},
            {'freq_low': 1000, 'freq_high': 3000, 'gain': 1.0},
            {'freq_low': 3000, 'freq_high': 6000, 'gain': 1.0},
            {'freq_low': 6000, 'freq_high': 12000, 'gain': 1.0},
            {'freq_low': 12000, 'freq_high': 20000, 'gain': 1.0}
        ])
        
        # Convert frequencies to bin indices
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.frame_length)
        
        # Create shaping mask
        mask = np.ones_like(D, dtype=float)
        
        for band in bands:
            # Find bin indices for this band
            idx_low = np.searchsorted(freqs, band['freq_low'])
            idx_high = np.searchsorted(freqs, band['freq_high'])
            
            # Apply gain
            mask[idx_low:idx_high] *= band['gain'] ** shape_factor
            
        return D * mask
        
    def _enhance_harmonics(self, D: np.ndarray, params: Dict) -> np.ndarray:
        """Enhance harmonic content while preserving phase."""
        enhancement = params.get('enhancement', 1.5)
        threshold = params.get('threshold', 0.1)
        
        # Get magnitude and phase
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Find harmonic peaks
        peaks = self._find_harmonic_peaks(magnitude, threshold)
        
        # Enhance harmonics
        magnitude_enhanced = magnitude.copy()
        for peak in peaks:
            magnitude_enhanced[peak] *= enhancement
            
        # Reconstruct
        return magnitude_enhanced * np.exp(1j * phase)
        
    def _apply_noise_gate(self, D: np.ndarray, params: Dict) -> np.ndarray:
        """Apply spectral noise gate."""
        threshold = params.get('threshold', -60)
        ratio = params.get('ratio', 10.0)
        
        # Convert to dB
        magnitude_db = librosa.amplitude_to_db(np.abs(D))
        
        # Calculate gain reduction
        gain_reduction = np.zeros_like(magnitude_db)
        mask = magnitude_db < threshold
        gain_reduction[mask] = (threshold - magnitude_db[mask]) * (1 - 1/ratio)
        
        # Convert back to linear
        gain = librosa.db_to_amplitude(-gain_reduction)
        
        return D * gain
        
    def _apply_spectral_compression(self, D: np.ndarray, params: Dict) -> np.ndarray:
        """Apply compression in the spectral domain."""
        threshold = params.get('threshold', -20)
        ratio = params.get('ratio', 4.0)
        attack = params.get('attack', 0.003)
        release = params.get('release', 0.25)
        
        # Convert to dB
        magnitude_db = librosa.amplitude_to_db(np.abs(D))
        
        # Calculate gain reduction
        gain_reduction = np.zeros_like(magnitude_db)
        mask = magnitude_db > threshold
        gain_reduction[mask] = (magnitude_db[mask] - threshold) * (1 - 1/ratio)
        
        # Smooth gain reduction
        gain_reduction = self._smooth_gain_reduction(
            gain_reduction,
            int(attack * self.sample_rate / self.hop_length),
            int(release * self.sample_rate / self.hop_length)
        )
        
        # Convert back to linear
        gain = librosa.db_to_amplitude(-gain_reduction)
        
        return D * gain
        
    def _correct_phase(self, D: np.ndarray, params: Dict) -> np.ndarray:
        """Apply phase correction to improve coherence."""
        coherence = params.get('coherence', 0.5)
        
        # Get magnitude and phase
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Calculate phase differences
        phase_diff = np.diff(phase, axis=1)
        
        # Smooth phase differences
        phase_diff_smooth = np.zeros_like(phase_diff)
        for i in range(phase_diff.shape[0]):
            phase_diff_smooth[i] = self._smooth_phase(phase_diff[i], coherence)
            
        # Reconstruct phase
        phase_corrected = np.zeros_like(phase)
        phase_corrected[:, 0] = phase[:, 0]
        for i in range(1, phase.shape[1]):
            phase_corrected[:, i] = phase_corrected[:, i-1] + phase_diff_smooth[:, i-1]
            
        # Reconstruct
        return magnitude * np.exp(1j * phase_corrected)
        
    def _find_harmonic_peaks(self, magnitude: np.ndarray, threshold: float) -> List[int]:
        """Find harmonic peaks in the magnitude spectrum."""
        peaks = []
        
        # Find local maxima
        for i in range(1, magnitude.shape[0]-1):
            if (magnitude[i] > magnitude[i-1] and 
                magnitude[i] > magnitude[i+1] and 
                magnitude[i] > threshold):
                peaks.append(i)
                
        return peaks
        
    def _smooth_phase(self, phase: np.ndarray, coherence: float) -> np.ndarray:
        """Smooth phase differences."""
        # Unwrap phase
        phase_unwrapped = np.unwrap(phase)
        
        # Apply moving average
        window_size = int(1 / coherence)
        if window_size > 1:
            phase_smooth = np.convolve(
                phase_unwrapped,
                np.ones(window_size) / window_size,
                mode='same'
            )
        else:
            phase_smooth = phase_unwrapped
            
        return phase_smooth
        
    def _smooth_gain_reduction(self, gain_reduction: np.ndarray, attack: int, release: int) -> np.ndarray:
        """Smooth gain reduction with attack and release."""
        smoothed = np.zeros_like(gain_reduction)
        current_gain = gain_reduction[0]
        
        for i in range(len(gain_reduction)):
            if gain_reduction[i] > current_gain:
                # Attack phase
                current_gain += (gain_reduction[i] - current_gain) / attack
            else:
                # Release phase
                current_gain += (gain_reduction[i] - current_gain) / release
            smoothed[i] = current_gain
            
        return smoothed
        
    def analyze_spectrum(self, audio: np.ndarray) -> Dict:
        """Analyze spectral characteristics."""
        try:
            # Compute STFT
            D = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
            
            # Get magnitude spectrum
            magnitude = np.abs(D)
            
            # Compute spectral features
            spectral_centroid = librosa.feature.spectral_centroid(S=magnitude)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude)[0]
            spectral_flatness = librosa.feature.spectral_flatness(S=magnitude)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude)[0]
            
            # Compute harmonic features
            harmonic_peaks = self._find_harmonic_peaks(magnitude.mean(axis=1), 0.1)
            harmonic_energy = np.sum(magnitude[harmonic_peaks]) / np.sum(magnitude)
            
            return {
                'spectral_centroid_mean': np.mean(spectral_centroid),
                'spectral_rolloff_mean': np.mean(spectral_rolloff),
                'spectral_flatness_mean': np.mean(spectral_flatness),
                'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
                'harmonic_energy': harmonic_energy,
                'harmonic_peaks': harmonic_peaks
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing spectrum: {str(e)}")
            raise 