@echo off
echo 🎤 Installing Universal TTS System...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✅ Installation complete!
echo Run: python demo.py
pause
