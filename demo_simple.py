#!/usr/bin/env python3
"""
Simple demo script for Universal TTS System
"""

import asyncio
from main import UniversalTTSSystem

async def main():
    # Initialize the TTS system
    tts = UniversalTTSSystem()
    
    # Test text
    test_text = "Hello! This is a test of the Universal TTS System. It's working great!"
    
    # Save the test text to a temporary file
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(test_text)
    
    try:
        # Process the text file
        print("Processing text file...")
        output_file = await tts.process_file(
            "test.txt",
            voice_profile="default",
            output_format="mp3",
            save_audio=True
        )
        
        if output_file:
            print(f"Success! Audio saved to: {output_file}")
        else:
            print("Audio was played but not saved.")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Clean up the temporary file
        import os
        if os.path.exists("test.txt"):
            os.remove("test.txt")

if __name__ == "__main__":
    asyncio.run(main()) 