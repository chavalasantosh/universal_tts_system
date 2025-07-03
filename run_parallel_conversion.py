import multiprocessing
import sys
import os
import asyncio
from main import UniversalTTSSystem
from typing import List
import time

def get_supported_files() -> List[str]:
    """Get list of supported files in current directory"""
    return [
        f for f in os.listdir('.') 
        if f.lower().endswith(('.pdf', '.epub', '.docx', '.md', '.mobi'))
    ]

async def process_file_async(file_path: str) -> None:
    """Process a single file asynchronously"""
    try:
        print(f"\nStarting conversion of: {file_path}")
        start_time = time.time()
        
        tts = UniversalTTSSystem()
        output_path = await tts.process_file(
            file_path,
            voice_profile="default",
            output_format="wav",
            save_audio=True
        )
        
        duration = time.time() - start_time
        print(f"\nCompleted conversion of {file_path}")
        print(f"Output saved to: {output_path}")
        print(f"Time taken: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"\nError processing {file_path}: {str(e)}")

def process_file(file_path: str) -> None:
    """Process a single file (wrapper for async function)"""
    asyncio.run(process_file_async(file_path))

def main():
    # Get list of supported files
    input_files = get_supported_files()
    
    if not input_files:
        print("No supported files found in current directory!")
        return
        
    print(f"\nFound {len(input_files)} files to process:")
    for f in input_files:
        print(f"- {f}")
    
    # Calculate optimal number of processes
    num_processes = min(len(input_files), multiprocessing.cpu_count())
    print(f"\nUsing {num_processes} processes for parallel conversion")
    
    # Process files in parallel
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_file, input_files)

if __name__ == "__main__":
    main() 