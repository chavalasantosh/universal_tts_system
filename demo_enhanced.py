import os
import asyncio
import yaml
from pathlib import Path
from engines.elevenlabs_engine import ElevenLabsEngine
from utils.audio_processor import AudioProcessor
from utils.text_processor import TextProcessor

async def main():
    # Load configuration
    config_path = Path('config.yaml')
    if not config_path.exists():
        config_path = Path('config_sample.yaml')
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    tts_engine = ElevenLabsEngine(config['tts_engines']['elevenlabs'])
    audio_processor = AudioProcessor(config['audio_processing'])
    text_processor = TextProcessor(config['content_processing'])
    
    # Sample text with various features
    sample_text = """
    Hello! This is a demonstration of the enhanced TTS system.
    
    It features:
    - Natural-sounding voices
    - Advanced audio processing
    - SSML support
    - Multiple languages
    - And much more!
    
    Let's try some special effects: The quick brown fox jumps over the lazy dog.
    """
    
    # Process text
    processed_text = text_processor.process_text(sample_text)
    print("Processed text with SSML:")
    print(processed_text)
    
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Generate speech
    raw_audio_path = output_dir / 'raw_output.wav'
    await tts_engine.synthesize(processed_text, str(raw_audio_path))
    
    # Process audio
    final_audio_path = output_dir / 'final_output.wav'
    audio_processor.process_audio(str(raw_audio_path), str(final_audio_path))
    
    # Get audio info
    audio_info = audio_processor.get_audio_info(str(final_audio_path))
    print("\nAudio file information:")
    print(f"Duration: {audio_info['duration']:.2f} seconds")
    print(f"Sample rate: {audio_info['sample_rate']} Hz")
    print(f"Channels: {audio_info['channels']}")
    print(f"Format: {audio_info['format']}")
    
    print(f"\nGenerated audio saved to: {final_audio_path}")

if __name__ == "__main__":
    asyncio.run(main()) 