# Universal Text-to-Speech System

A powerful, multi-format text-to-speech system that can convert various document formats into audio files.

## Features

- Supports multiple input formats:
  - PDF files (.pdf)
  - EPUB e-books (.epub)
  - Text files (.txt)
  - HTML files (.html)
  - Markdown files (.md)
  - Word documents (.docx)
  - Rich Text Format (.rtf)

- Supports multiple output formats:
  - WAV (.wav)
  - MP3 (.mp3)
  - OGG (.ogg)

- Parallel processing for faster conversion
- Progress tracking and status updates
- Customizable voice profiles

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Clone or download this repository
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

To convert a single file:
```bash
python run_conversion.py "path/to/your/file.pdf" --voice default --save --format wav
```

### Parallel Processing

To convert multiple files at once:
```bash
python run_parallel_conversion.py
```

### Command Line Options

- `--voice` or `-v`: Select voice profile (default: "default")
- `--save` or `-s`: Save audio to file
- `--format` or `-f`: Output format (mp3, wav, or ogg)

## Project Structure

```
universal_tts_system/
├── engines/           # TTS engine implementations
├── readers/           # File reader implementations
├── profiles/          # Voice profiles
├── utils/             # Utility functions
├── main.py           # Main system implementation
├── run_conversion.py # Single file conversion script
├── run_parallel_conversion.py # Parallel processing script
└── requirements.txt   # Project dependencies
```

## Supported File Types

### Input Formats
- PDF (.pdf)
- EPUB (.epub)
- Text (.txt)
- HTML (.html)
- Markdown (.md)
- Word (.docx)
- Rich Text (.rtf)

### Output Formats
- WAV (.wav)
- MP3 (.mp3)
- OGG (.ogg)

## Troubleshooting

1. If you get a "No reader available" error:
   - Make sure the file format is supported
   - Check if all dependencies are installed

2. If you get a TTS engine error:
   - Try using a different voice profile
   - Check if your system has the required audio drivers

## Contributing

Feel free to submit issues and enhancement requests!
