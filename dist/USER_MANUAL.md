# Universal TTS System - User Manual

## Quick Start Guide

### Installation
1. **Prerequisites**
   - Python 3.8 or higher
   - Internet connection (for online TTS engines)
   - Audio output device

2. **Setup Steps**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd universal_tts_system

   # Install dependencies
   pip install -r requirements.txt

   # Run setup
   python setup.py install
   ```

## Key Features

### 1. Multiple Input Formats
- PDF Documents
- EPUB E-books
- Text Files
- HTML Files
- Markdown Files
- DOCX Documents
- RTF Files

### 2. Multiple Output Formats
- WAV (High Quality)
- MP3 (Compressed)
- OGG (Open Format)

### 3. Voice Options
- Default Voice
- Custom Voice Profiles
- Multiple Languages
- Voice Speed Control
- Pitch Adjustment

## Main Functionalities

### 1. Single File Conversion
```bash
# Basic conversion
python run_conversion.py "your_file.pdf" --voice default --save --format wav

# Advanced options
python run_conversion.py "your_file.pdf" --voice custom_voice --save --format mp3 --speed 1.2
```

### 2. Batch Processing
```bash
# Process all supported files in a directory
python run_parallel_conversion.py
```

### 3. Voice Profile Management
```bash
# List available voices
python run_conversion.py --list-voices

# Create custom voice profile
python run_conversion.py --create-profile "my_voice" --language en --gender female
```

## Usage Scenarios

### 1. Converting a PDF Book
```bash
# Convert a PDF book to audio
python run_conversion.py "book.pdf" --voice default --save --format mp3
```
- Output: `book_output.mp3`
- Estimated time: 2-3 minutes per 100 pages
- Quality: 128kbps MP3

### 2. Batch Processing Multiple Files
```bash
# Process all PDFs in current directory
python run_parallel_conversion.py
```
- Automatically detects supported files
- Uses optimal number of CPU cores
- Creates separate output files for each input

### 3. Custom Voice Settings
```bash
# Use custom voice profile
python run_conversion.py "document.pdf" --voice custom_voice --speed 1.2 --pitch 1.1
```
- Adjust speech rate
- Modify pitch
- Select language
- Choose gender

## Important Settings

### 1. Output Format Options
- **WAV**: Highest quality, largest file size
  ```bash
  python run_conversion.py "file.pdf" --format wav
  ```
- **MP3**: Good quality, smaller file size
  ```bash
  python run_conversion.py "file.pdf" --format mp3
  ```
- **OGG**: Open format, good compression
  ```bash
  python run_conversion.py "file.pdf" --format ogg
  ```

### 2. Voice Profile Settings
- **Speed**: 0.5 to 2.0 (default: 1.0)
- **Pitch**: 0.5 to 2.0 (default: 1.0)
- **Language**: Multiple options available
- **Gender**: Male/Female/Neutral

### 3. Processing Options
- **Chunk Size**: Text processing chunks
- **Parallel Processing**: Number of simultaneous conversions
- **Memory Usage**: Buffer size settings

## Troubleshooting Guide

### 1. Common Issues

#### File Not Found
```bash
Error: File not found: your_file.pdf
```
Solution: Check file path and permissions

#### Voice Profile Error
```bash
Error: Voice profile not found: custom_voice
```
Solution: Create voice profile first or use default

#### Format Not Supported
```bash
Error: Unsupported output format: invalid_format
```
Solution: Use supported formats (wav, mp3, ogg)

### 2. Performance Issues

#### Slow Processing
- Reduce chunk size
- Use parallel processing
- Check system resources

#### High Memory Usage
- Reduce buffer size
- Process smaller files
- Close other applications

### 3. Audio Quality Issues

#### Poor Sound Quality
- Use WAV format
- Check audio device
- Adjust voice settings

#### Voice Speed Problems
- Adjust speed parameter
- Check voice profile
- Try different voice

## Best Practices

### 1. File Preparation
- Use clean, well-formatted documents
- Remove unnecessary images
- Check file encoding

### 2. Processing
- Start with small files
- Use appropriate format
- Monitor system resources

### 3. Output Management
- Use meaningful filenames
- Organize output directory
- Backup important files

## Advanced Features

### 1. Custom Voice Profiles
```bash
# Create custom profile
python run_conversion.py --create-profile "my_voice" \
    --language en \
    --gender female \
    --speed 1.2 \
    --pitch 1.1
```

### 2. Batch Processing with Options
```bash
# Process specific file types
python run_parallel_conversion.py --types pdf,epub

# Use custom settings
python run_parallel_conversion.py --voice custom_voice --format mp3
```

### 3. Output Management
```bash
# Specify output directory
python run_conversion.py "file.pdf" --output-dir "audio_files"

# Custom output filename
python run_conversion.py "file.pdf" --output "custom_name.mp3"
```

## Tips and Tricks

### 1. Performance Optimization
- Use parallel processing for multiple files
- Choose appropriate output format
- Monitor system resources

### 2. Quality Improvement
- Use WAV for best quality
- Adjust voice settings
- Check audio device

### 3. File Management
- Organize input files
- Use consistent naming
- Backup regularly

## Support and Resources

### 1. Getting Help
- Check documentation
- Review error logs
- Contact support

### 2. Updates
- Regular updates
- New features
- Bug fixes

### 3. Community
- User forums
- Feature requests
- Bug reports

## Conclusion

The Universal TTS System provides:
- Easy-to-use interface
- Multiple format support
- Customizable voices
- High-quality output
- Efficient processing

For additional help or questions, please refer to:
- Technical Documentation
- Issue Tracker
- Support Team 