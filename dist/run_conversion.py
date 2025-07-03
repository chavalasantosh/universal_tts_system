import argparse
import asyncio
from main import UniversalTTSSystem

async def main():
    parser = argparse.ArgumentParser(description="Universal TTS System - Single File Conversion")
    parser.add_argument("file", help="File to process")
    parser.add_argument("--voice", "-v", default="default", help="Voice profile to use")
    parser.add_argument("--save", "-s", action="store_true", help="Save audio to file")
    parser.add_argument("--format", "-f", default="mp3", choices=["mp3", "wav", "ogg"], help="Output audio format")
    args = parser.parse_args()

    tts = UniversalTTSSystem()
    await tts.process_file(
        args.file,
        voice_profile=args.voice,
        output_format=args.format,
        save_audio=args.save
    )

if __name__ == "__main__":
    asyncio.run(main()) 