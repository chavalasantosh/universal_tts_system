#!/usr/bin/env python3
"""
Demo script for testing voice cloning functionality
"""

import os
import asyncio
from engines.voice_cloner import VoiceCloner

async def main():
    # Initialize voice cloner
    cloner = VoiceCloner()
    
    # Test files
    source_audio = "sample_voice.wav"  # You'll need to provide a sample voice recording
    target_text = "This is a test of the voice cloning system. It should sound similar to the source voice."
    output_path = "cloned_voice.wav"
    
    print("Starting voice cloning process...")
    print(f"Source audio: {source_audio}")
    print(f"Target text: {target_text}")
    print(f"Output will be saved to: {output_path}")
    
    # Check if source audio exists
    if not os.path.exists(source_audio):
        print(f"Error: Source audio file {source_audio} not found!")
        print("Please provide a sample voice recording in WAV format.")
        return
    
    # Perform voice cloning
    success = cloner.clone_voice(source_audio, target_text, output_path)
    
    if success:
        print("\nVoice cloning completed successfully!")
        print(f"Output saved to: {output_path}")
    else:
        print("\nVoice cloning failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 