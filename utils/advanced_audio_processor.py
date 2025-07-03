import os
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.signal import butter, filtfilt
import librosa
from typing import Dict, Optional, Tuple, List
import logging

class AdvancedAudioProcessor:
    """Advanced audio processing with professional-grade effects."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize processing parameters
        self.sample_rate = config.get('sample_rate', 44100)
        self.channels = config.get('channels', 2)
        
        # Initialize effect parameters
        self.effects = config.get('effects', {})
        
    def process_audio(self, input_path: str, output_path: str, effects: Optional[Dict] = None) -> str:
        """
        Process audio with advanced effects.
        
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
                audio = self._apply_effects(audio, effects)
            else:
                audio = self._apply_effects(audio, self.effects)
            
            # Save processed audio
            sf.write(output_path, audio, self.sample_rate)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            raise
            
    def _apply_effects(self, audio: np.ndarray, effects: Dict) -> np.ndarray:
        """Apply multiple audio effects in sequence."""
        if effects.get('noise_reduction'):
            audio = self._reduce_noise(audio)
            
        if effects.get('equalization'):
            audio = self._apply_eq(audio, effects['equalization'])
            
        if effects.get('compression'):
            audio = self._apply_compression(audio, effects['compression'])
            
        if effects.get('reverb'):
            audio = self._apply_reverb(audio, effects['reverb'])
            
        if effects.get('echo'):
            audio = self._apply_echo(audio, effects['echo'])
            
        if effects.get('pitch_shift'):
            audio = self._shift_pitch(audio, effects['pitch_shift'])
            
        if effects.get('time_stretch'):
            audio = self._stretch_time(audio, effects['time_stretch'])
            
        if effects.get('stereo_width'):
            audio = self._adjust_stereo_width(audio, effects['stereo_width'])
            
        return audio
        
    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Apply advanced noise reduction."""
        # Spectral gating
        S = np.abs(librosa.stft(audio))
        S_db = librosa.amplitude_to_db(S)
        
        # Estimate noise floor
        noise_floor = np.mean(S_db, axis=1)
        threshold = noise_floor + 10
        
        # Apply gate
        S_db_gated = np.maximum(S_db, threshold[:, np.newaxis])
        S_gated = librosa.db_to_amplitude(S_db_gated)
        
        # Reconstruct signal
        return librosa.istft(S_gated)
        
    def _apply_eq(self, audio: np.ndarray, eq_params: Dict) -> np.ndarray:
        """Apply parametric equalization."""
        bands = eq_params.get('bands', [
            {'freq': 60, 'gain': 0, 'q': 1.0},
            {'freq': 170, 'gain': 0, 'q': 1.0},
            {'freq': 310, 'gain': 0, 'q': 1.0},
            {'freq': 600, 'gain': 0, 'q': 1.0},
            {'freq': 1000, 'gain': 0, 'q': 1.0},
            {'freq': 3000, 'gain': 0, 'q': 1.0},
            {'freq': 6000, 'gain': 0, 'q': 1.0},
            {'freq': 12000, 'gain': 0, 'q': 1.0},
            {'freq': 14000, 'gain': 0, 'q': 1.0},
            {'freq': 16000, 'gain': 0, 'q': 1.0}
        ])
        
        # Apply each band
        for band in bands:
            b, a = self._design_peaking_filter(
                band['freq'],
                band['gain'],
                band['q'],
                self.sample_rate
            )
            audio = filtfilt(b, a, audio)
            
        return audio
        
    def _apply_compression(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply multi-band compression."""
        threshold = params.get('threshold', -20)
        ratio = params.get('ratio', 4.0)
        attack = params.get('attack', 0.003)
        release = params.get('release', 0.25)
        
        # Convert to dB
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Calculate gain reduction
        gain_reduction = np.zeros_like(audio_db)
        mask = audio_db > threshold
        gain_reduction[mask] = (audio_db[mask] - threshold) * (1 - 1/ratio)
        
        # Apply attack/release
        attack_samples = int(attack * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        # Smooth gain reduction
        gain_reduction = self._smooth_gain_reduction(
            gain_reduction,
            attack_samples,
            release_samples
        )
        
        # Apply gain reduction
        audio = audio * np.power(10, -gain_reduction/20)
        return audio
        
    def _apply_reverb(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply convolution reverb."""
        room_size = params.get('room_size', 0.5)
        damping = params.get('damping', 0.5)
        wet_level = params.get('wet_level', 0.3)
        
        # Generate impulse response
        ir_length = int(room_size * self.sample_rate)
        impulse_response = np.exp(-damping * np.arange(ir_length))
        impulse_response = impulse_response / np.sum(impulse_response)
        
        # Apply convolution
        reverb = signal.convolve(audio, impulse_response, mode='full')
        reverb = reverb[:len(audio)]
        
        # Mix with original
        return (1 - wet_level) * audio + wet_level * reverb
        
    def _apply_echo(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply multi-tap echo."""
        delay = params.get('delay', 0.3)
        feedback = params.get('feedback', 0.3)
        taps = params.get('taps', 3)
        
        delay_samples = int(delay * self.sample_rate)
        output = np.copy(audio)
        
        for i in range(taps):
            delay_amount = delay_samples * (i + 1)
            delayed = np.roll(audio, delay_amount)
            delayed[:delay_amount] = 0
            output += delayed * (feedback ** (i + 1))
            
        return output
        
    def _shift_pitch(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply pitch shifting."""
        semitones = params.get('semitones', 0)
        return librosa.effects.pitch_shift(
            audio,
            sr=self.sample_rate,
            n_steps=semitones
        )
        
    def _stretch_time(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply time stretching."""
        rate = params.get('rate', 1.0)
        return librosa.effects.time_stretch(audio, rate=rate)
        
    def _adjust_stereo_width(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Adjust stereo width."""
        width = params.get('width', 1.0)
        
        if len(audio.shape) == 1:
            return audio
            
        mid = (audio[:, 0] + audio[:, 1]) / 2
        side = (audio[:, 0] - audio[:, 1]) / 2
        
        side *= width
        
        return np.column_stack((mid + side, mid - side))
        
    def _design_peaking_filter(self, freq: float, gain: float, q: float, fs: float) -> Tuple[np.ndarray, np.ndarray]:
        """Design a peaking filter."""
        w0 = 2 * np.pi * freq / fs
        alpha = np.sin(w0) / (2 * q)
        
        A = np.sqrt(10 ** (gain / 20))
        
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A
        
        return np.array([b0, b1, b2]), np.array([a0, a1, a2])
        
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
        
    def get_audio_info(self, audio_path: str) -> Dict:
        """Get detailed information about an audio file."""
        try:
            info = sf.info(audio_path)
            duration = info.duration
            sample_rate = info.samplerate
            channels = info.channels
            format = info.format
            
            # Get additional metrics
            audio, _ = librosa.load(audio_path, sr=None)
            rms = np.sqrt(np.mean(audio**2))
            peak = np.max(np.abs(audio))
            crest_factor = peak / (rms + 1e-10)
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'format': format,
                'rms': rms,
                'peak': peak,
                'crest_factor': crest_factor
            }
            
        except Exception as e:
            self.logger.error(f"Error getting audio info: {str(e)}")
            raise 