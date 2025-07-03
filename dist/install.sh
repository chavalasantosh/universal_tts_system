#!/bin/bash
echo "🎤 Installing Universal TTS System..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Installation complete!"
echo "Run: python demo.py"
