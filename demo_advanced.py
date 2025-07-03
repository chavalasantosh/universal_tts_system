#!/usr/bin/env python3
"""
Advanced demo script for Universal TTS System
Supports multiple file types and voice profiles
"""

import asyncio
import os
from main import UniversalTTSSystem

async def process_file(tts, file_path, voice_profile="default", output_format="mp3"):
    """Process a single file with the TTS system"""
    try:
        print(f"\nProcessing file: {file_path}")
        print(f"Using voice profile: {voice_profile}")
        print(f"Output format: {output_format}")
        
        output_file = await tts.process_file(
            file_path,
            voice_profile=voice_profile,
            output_format=output_format,
            save_audio=True
        )
        
        if output_file:
            print(f"Success! Audio saved to: {output_file}")
            return True
        else:
            print("Audio was played but not saved.")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

async def main():
    # Initialize the TTS system
    tts = UniversalTTSSystem()
    
    # Test files
    test_files = [
        "test.txt",
        "test.pdf",
        "test.md"
    ]
    
    # Voice profiles to test
    voice_profiles = [
        "default",
        "male",
        "female"
    ]
    
    # Process each file with different voice profiles
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"\nSkipping {file_path} - file not found")
            continue
            
        for voice_profile in voice_profiles:
            success = await process_file(
                tts,
                file_path,
                voice_profile=voice_profile,
                output_format="mp3"
            )
            
            if not success:
                print(f"Failed to process {file_path} with voice profile {voice_profile}")
                break

if __name__ == "__main__":
    asyncio.run(main()) 