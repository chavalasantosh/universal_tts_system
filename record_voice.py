#!/usr/bin/env python3
"""
Script to record voice samples for voice cloning
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import time

def record_voice(duration=5, sample_rate=22050, output_file="sample_voice.wav"):
    """
    Record voice for the specified duration
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Audio sample rate
        output_file: Output WAV file path
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Ensure .wav extension
        if not output_file.endswith('.wav'):
            output_file += '.wav'
            
        print(f"\nRecording will start in 3 seconds...")
        print("Please speak clearly into your microphone.")
        print(f"Recording duration: {duration} seconds")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("\nRecording started!")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        
        # Wait for recording to complete
        sd.wait()
        
        # Save recording
        sf.write(output_file, recording, sample_rate)
        
        print(f"\nRecording completed!")
        print(f"Saved to: {output_file}")
        
        # Play back the recording
        print("\nPlaying back the recording...")
        sd.play(recording, sample_rate)
        sd.wait()
        
        return output_file
        
    except Exception as e:
        print(f"\nError during recording: {str(e)}")
        return None

def main():
    try:
        # Get recording duration from user
        while True:
            try:
                duration = float(input("\nEnter recording duration in seconds (default: 5): ") or "5")
                if duration > 0:
                    break
                print("Duration must be greater than 0")
            except ValueError:
                print("Please enter a valid number")
        
        # Get output filename
        output_file = input("Enter output filename (default: sample_voice.wav): ") or "sample_voice.wav"
        
        # Record voice
        result = record_voice(duration, output_file=output_file)
        
        if result:
            print("\nYou can now use this recording for voice cloning!")
            print("Run demo_voice_clone.py to test voice cloning with this recording.")
        else:
            print("\nRecording failed. Please try again.")
            
    except KeyboardInterrupt:
        print("\nRecording cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 