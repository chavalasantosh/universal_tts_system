#!/usr/bin/env python3
"""
Test script to verify all required dependencies are installed correctly
"""

def test_imports():
    print("Testing imports...")
    
    # Core dependencies
    try:
        import pyttsx3
        print("✓ pyttsx3 installed")
    except ImportError:
        print("✗ pyttsx3 not installed")
    
    try:
        import yaml
        print("✓ PyYAML installed")
    except ImportError:
        print("✗ PyYAML not installed")
    
    # File processing
    try:
        import docx
        print("✓ python-docx installed")
    except ImportError:
        print("✗ python-docx not installed")
    
    try:
        import PyPDF2
        print("✓ PyPDF2 installed")
    except ImportError:
        print("✗ PyPDF2 not installed")
    
    try:
        import ebooklib
        print("✓ ebooklib installed")
    except ImportError:
        print("✗ ebooklib not installed")
    
    # Audio processing
    try:
        from pydub import AudioSegment
        print("✓ pydub installed")
    except ImportError:
        print("✗ pydub not installed")
    
    try:
        import sounddevice
        print("✓ sounddevice installed")
    except ImportError:
        print("✗ sounddevice not installed")
    
    try:
        import numpy
        print("✓ numpy installed")
    except ImportError:
        print("✗ numpy not installed")
    
    try:
        import librosa
        print("✓ librosa installed")
    except ImportError:
        print("✗ librosa not installed")

if __name__ == "__main__":
    print("Starting dependency check...")
    test_imports()
    print("\nDependency check complete!") 