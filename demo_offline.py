import os
import asyncio
import yaml
from pathlib import Path
from engines.local_engine import LocalTTSEngine
from utils.audio_processor import AudioProcessor
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
    audio_processor = AudioProcessor(config['audio_processing'])
    text_processor = TextProcessor(config['content_processing'])
    voice_cloner = LocalVoiceCloner(config)
    
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Sample text in multiple languages
    sample_texts = {
        'en': """
        Hello! This is a demonstration of the offline TTS system.
        
        It features:
        - Local TTS models
        - Voice cloning
        - Advanced audio processing
        - SSML support
        - Multiple languages
        - And much more!
        """,
        'es': """
        ¡Hola! Esta es una demostración del sistema TTS sin conexión.
        
        Características:
        - Modelos TTS locales
        - Clonación de voz
        - Procesamiento de audio avanzado
        - Soporte SSML
        - Múltiples idiomas
        - ¡Y mucho más!
        """
    }
    
    # 1. Demonstrate basic TTS
    print("\n1. Generating speech with local TTS...")
    for lang, text in sample_texts.items():
        processed_text = text_processor.process_text(text, language=lang)
        output_path = output_dir / f'tts_{lang}.wav'
        await tts_engine.synthesize(processed_text, str(output_path))
        print(f"Generated {lang} audio")
    
    # 2. Demonstrate voice cloning
    print("\n2. Demonstrating voice cloning...")
    # Assuming you have a reference audio file
    reference_audio = "path/to/reference_audio.wav"  # Replace with actual path
    if os.path.exists(reference_audio):
        # Clone voice
        voice_info = voice_cloner.clone_voice(
            reference_audio=reference_audio,
            voice_name="cloned_voice"
        )
        print(f"Cloned voice: {voice_info}")
        
        # Generate speech with cloned voice
        output_path = output_dir / 'cloned_voice.wav'
        voice_cloner.synthesize_with_cloned_voice(
            text=sample_texts['en'],
            voice_name="cloned_voice",
            output_path=str(output_path)
        )
        print("Generated speech with cloned voice")
    
    # 3. Demonstrate voice mixing
    print("\n3. Demonstrating voice mixing...")
    if len(voice_cloner.get_cloned_voices()) >= 2:
        # Mix two voices
        mixed_voice = voice_cloner.mix_voices(
            voice_names=["cloned_voice", "another_voice"],
            weights=[0.7, 0.3],
            output_voice_name="mixed_voice"
        )
        print(f"Created mixed voice: {mixed_voice}")
        
        # Generate speech with mixed voice
        output_path = output_dir / 'mixed_voice.wav'
        voice_cloner.synthesize_with_cloned_voice(
            text=sample_texts['en'],
            voice_name="mixed_voice",
            output_path=str(output_path)
        )
        print("Generated speech with mixed voice")
    
    # 4. Demonstrate audio processing
    print("\n4. Demonstrating audio processing...")
    # Process one of the generated files
    input_path = output_dir / 'tts_en.wav'
    processed_path = output_dir / 'processed_audio.wav'
    
    # Apply various effects
    config['audio_processing']['effects']['enabled'] = True
    config['audio_processing']['effects']['reverb'] = 0.3
    config['audio_processing']['effects']['echo'] = 0.2
    config['audio_processing']['effects']['compression'] = 0.5
    
    audio_processor.process_audio(str(input_path), str(processed_path))
    print("Applied audio processing effects")
    
    # Get audio information
    audio_info = audio_processor.get_audio_info(str(processed_path))
    print("\nProcessed audio information:")
    print(f"Duration: {audio_info['duration']:.2f} seconds")
    print(f"Sample rate: {audio_info['sample_rate']} Hz")
    print(f"Channels: {audio_info['channels']}")
    print(f"Format: {audio_info['format']}")
    
    print(f"\nAll generated files are in: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main()) 