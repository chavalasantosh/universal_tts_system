import os
import asyncio
import yaml
from pathlib import Path
from engines.local_engine import LocalTTSEngine
from utils.advanced_audio_processor import AdvancedAudioProcessor
from utils.advanced_voice_processor import AdvancedVoiceProcessor
from utils.spectral_processor import SpectralProcessor
from utils.advanced_synthesizer import AdvancedSynthesizer
from utils.text_processor import TextProcessor
from utils.local_voice_cloner import LocalVoiceCloner

async def main():
    # Load configuration
    config_path = Path('config.yaml')
    if not config_path.exists():
        config_path = Path('config_sample.yaml')
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    tts_engine = LocalTTSEngine(config['tts_engines']['local'])
    audio_processor = AdvancedAudioProcessor(config['audio_processing'])
    voice_processor = AdvancedVoiceProcessor(config['voice_processing'])
    spectral_processor = SpectralProcessor(config['spectral_processing'])
    synthesizer = AdvancedSynthesizer(config['synthesis'])
    text_processor = TextProcessor(config['content_processing'])
    voice_cloner = LocalVoiceCloner(config)
    
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Sample text in multiple languages
    sample_texts = {
        'en': """
        Welcome to the Ultra Advanced TTS System!
        
        This demonstration showcases:
        - Professional-grade audio processing
        - Advanced voice manipulation
        - Spectral processing
        - Voice synthesis
        - Voice cloning and mixing
        - And much more!
        """,
        'es': """
        ¡Bienvenido al Sistema TTS Ultra Avanzado!
        
        Esta demostración muestra:
        - Procesamiento de audio profesional
        - Manipulación avanzada de voz
        - Procesamiento espectral
        - Síntesis de voz
        - Clonación y mezcla de voces
        - ¡Y mucho más!
        """
    }
    
    # 1. Generate base TTS
    print("\n1. Generating base TTS...")
    base_audio_path = output_dir / 'base_tts.wav'
    processed_text = text_processor.process_text(sample_texts['en'])
    await tts_engine.synthesize(processed_text, str(base_audio_path))
    print("Generated base TTS")
    
    # 2. Apply advanced audio processing
    print("\n2. Applying advanced audio processing...")
    audio_effects = {
        'noise_reduction': True,
        'equalization': {
            'bands': [
                {'freq': 60, 'gain': 2, 'q': 1.0},
                {'freq': 170, 'gain': 1, 'q': 1.0},
                {'freq': 310, 'gain': 0, 'q': 1.0},
                {'freq': 600, 'gain': -1, 'q': 1.0},
                {'freq': 1000, 'gain': 0, 'q': 1.0},
                {'freq': 3000, 'gain': 2, 'q': 1.0},
                {'freq': 6000, 'gain': 3, 'q': 1.0},
                {'freq': 12000, 'gain': 2, 'q': 1.0},
                {'freq': 14000, 'gain': 1, 'q': 1.0},
                {'freq': 16000, 'gain': 0, 'q': 1.0}
            ]
        },
        'compression': {
            'threshold': -20,
            'ratio': 4.0,
            'attack': 0.003,
            'release': 0.25
        },
        'reverb': {
            'room_size': 0.5,
            'damping': 0.5,
            'wet_level': 0.3
        },
        'stereo_width': {
            'width': 1.5
        }
    }
    
    processed_audio_path = output_dir / 'processed_audio.wav'
    audio_processor.process_audio(str(base_audio_path), str(processed_audio_path), audio_effects)
    print("Applied advanced audio processing")
    
    # 3. Apply voice processing
    print("\n3. Applying voice processing...")
    voice_effects = {
        'formant_shift': {
            'shift_factor': 1.2
        },
        'vocal_range': {
            'range_factor': 1.1
        },
        'breathiness': {
            'amount': 0.3
        },
        'resonance': {
            'amount': 0.4,
            'frequency': 1000
        },
        'vibrato': {
            'rate': 5.0,
            'depth': 0.3
        },
        'tremolo': {
            'rate': 6.0,
            'depth': 0.2
        }
    }
    
    voice_processed_path = output_dir / 'voice_processed.wav'
    voice_processor.process_voice(str(processed_audio_path), str(voice_processed_path), voice_effects)
    print("Applied voice processing")
    
    # 4. Apply spectral processing
    print("\n4. Applying spectral processing...")
    spectral_effects = {
        'spectral_shaping': {
            'shape_factor': 1.2,
            'bands': [
                {'freq_low': 0, 'freq_high': 100, 'gain': 1.0},
                {'freq_low': 100, 'freq_high': 300, 'gain': 1.2},
                {'freq_low': 300, 'freq_high': 1000, 'gain': 1.0},
                {'freq_low': 1000, 'freq_high': 3000, 'gain': 1.3},
                {'freq_low': 3000, 'freq_high': 6000, 'gain': 1.1},
                {'freq_low': 6000, 'freq_high': 12000, 'gain': 1.0},
                {'freq_low': 12000, 'freq_high': 20000, 'gain': 0.9}
            ]
        },
        'harmonic_enhancement': {
            'enhancement': 1.5,
            'threshold': 0.1
        },
        'noise_gate': {
            'threshold': -60,
            'ratio': 10.0
        },
        'spectral_compression': {
            'threshold': -20,
            'ratio': 4.0,
            'attack': 0.003,
            'release': 0.25
        },
        'phase_correction': {
            'coherence': 0.5
        }
    }
    
    spectral_processed_path = output_dir / 'spectral_processed.wav'
    audio, _ = librosa.load(str(voice_processed_path), sr=None)
    processed_audio = spectral_processor.process_spectrum(audio, spectral_effects)
    librosa.output.write_wav(str(spectral_processed_path), processed_audio, config['sample_rate'])
    print("Applied spectral processing")
    
    # 5. Demonstrate voice synthesis
    print("\n5. Demonstrating voice synthesis...")
    voice_params = {
        'pitch': 220,
        'duration': 3.0,
        'formants': [
            {'freq': 500, 'bandwidth': 100},
            {'freq': 1500, 'bandwidth': 100},
            {'freq': 2500, 'bandwidth': 100},
            {'freq': 3500, 'bandwidth': 100},
            {'freq': 4500, 'bandwidth': 100}
        ],
        'brightness': 1.2,
        'warmth': 1.1,
        'presence': 1.3,
        'attack': 0.01,
        'release': 0.1,
        'vibrato_rate': 5.0,
        'vibrato_depth': 0.3,
        'tremolo_rate': 6.0,
        'tremolo_depth': 0.2,
        'pitch_contour': [1.0, 1.2, 1.0, 0.8, 1.0],
        'timing': [1.0, 1.1, 1.0, 0.9, 1.0],
        'stress': [1.0, 1.3, 1.0, 1.2, 1.0]
    }
    
    synthesized_path = output_dir / 'synthesized_voice.wav'
    synthesizer.synthesize_voice(
        text=sample_texts['en'],
        voice_params=voice_params,
        output_path=str(synthesized_path)
    )
    print("Generated synthesized voice")
    
    # 6. Demonstrate voice cloning
    print("\n6. Demonstrating voice cloning...")
    reference_audio = "path/to/reference_audio.wav"  # Replace with actual path
    if os.path.exists(reference_audio):
        # Clone voice
        voice_info = voice_cloner.clone_voice(
            reference_audio=reference_audio,
            voice_name="cloned_voice"
        )
        print(f"Cloned voice: {voice_info}")
        
        # Generate speech with cloned voice
        cloned_output_path = output_dir / 'cloned_voice.wav'
        voice_cloner.synthesize_with_cloned_voice(
            text=sample_texts['en'],
            voice_name="cloned_voice",
            output_path=str(cloned_output_path)
        )
        print("Generated speech with cloned voice")
        
        # Apply voice processing to cloned voice
        processed_cloned_path = output_dir / 'processed_cloned_voice.wav'
        voice_processor.process_voice(str(cloned_output_path), str(processed_cloned_path), voice_effects)
        print("Applied voice processing to cloned voice")
    
    # 7. Demonstrate voice mixing
    print("\n7. Demonstrating voice mixing...")
    if len(voice_cloner.get_cloned_voices()) >= 2:
        # Mix two voices
        mixed_voice = voice_cloner.mix_voices(
            voice_names=["cloned_voice", "another_voice"],
            weights=[0.7, 0.3],
            output_voice_name="mixed_voice"
        )
        print(f"Created mixed voice: {mixed_voice}")
        
        # Generate speech with mixed voice
        mixed_output_path = output_dir / 'mixed_voice.wav'
        voice_cloner.synthesize_with_cloned_voice(
            text=sample_texts['en'],
            voice_name="mixed_voice",
            output_path=str(mixed_output_path)
        )
        print("Generated speech with mixed voice")
        
        # Apply voice processing to mixed voice
        processed_mixed_path = output_dir / 'processed_mixed_voice.wav'
        voice_processor.process_voice(str(mixed_output_path), str(processed_mixed_path), voice_effects)
        print("Applied voice processing to mixed voice")
    
    # 8. Analyze voice characteristics
    print("\n8. Analyzing voice characteristics...")
    voice_analysis = voice_processor.analyze_voice(str(voice_processed_path))
    print("\nVoice Analysis Results:")
    print(f"Mean Pitch: {voice_analysis['pitch_mean']:.2f} Hz")
    print(f"Spectral Centroid: {voice_analysis['spectral_centroid_mean']:.2f} Hz")
    print(f"Spectral Rolloff: {voice_analysis['spectral_rolloff_mean']:.2f} Hz")
    print(f"RMS Energy: {voice_analysis['rms_mean']:.4f}")
    print(f"Formants: {voice_analysis['formants']}")
    
    # 9. Analyze spectral characteristics
    print("\n9. Analyzing spectral characteristics...")
    spectral_analysis = spectral_processor.analyze_spectrum(processed_audio)
    print("\nSpectral Analysis Results:")
    print(f"Spectral Centroid: {spectral_analysis['spectral_centroid_mean']:.2f} Hz")
    print(f"Spectral Rolloff: {spectral_analysis['spectral_rolloff_mean']:.2f} Hz")
    print(f"Spectral Flatness: {spectral_analysis['spectral_flatness_mean']:.4f}")
    print(f"Spectral Bandwidth: {spectral_analysis['spectral_bandwidth_mean']:.2f} Hz")
    print(f"Harmonic Energy: {spectral_analysis['harmonic_energy']:.4f}")
    print(f"Number of Harmonic Peaks: {len(spectral_analysis['harmonic_peaks'])}")
    
    # 10. Get audio information
    print("\n10. Getting audio information...")
    audio_info = audio_processor.get_audio_info(str(voice_processed_path))
    print("\nProcessed Audio Information:")
    print(f"Duration: {audio_info['duration']:.2f} seconds")
    print(f"Sample Rate: {audio_info['sample_rate']} Hz")
    print(f"Channels: {audio_info['channels']}")
    print(f"Format: {audio_info['format']}")
    print(f"RMS: {audio_info['rms']:.4f}")
    print(f"Peak: {audio_info['peak']:.4f}")
    print(f"Crest Factor: {audio_info['crest_factor']:.2f}")
    
    print(f"\nAll generated files are in: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main()) 