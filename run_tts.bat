@echo off
cd /d "%~dp0"
python main.py "John Fowles - The Collector-Little, Brown & Co (1963).epub" --voice default --save --format mp3
pause 