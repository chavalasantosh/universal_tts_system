import re
from typing import Dict, List, Optional
import langdetect
from langdetect import detect
import logging

class TextProcessor:
    """Advanced text processing utilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load text processing settings
        self.ssml_enabled = config.get('ssml_enabled', True)
        self.punctuation_pause = config.get('punctuation_pause_duration', 0.5)
        self.sentence_pause = config.get('sentence_pause_duration', 1.0)
        self.paragraph_pause = config.get('paragraph_pause_duration', 2.0)
        self.text_cleanup = config.get('text_cleanup', True)
        self.language_detection = config.get('language_detection', True)

    def process_text(self, text: str, language: Optional[str] = None) -> str:
        """
        Process text with configured enhancements.
        
        Args:
            text: Input text to process
            language: Optional language code (if None, will be detected)
            
        Returns:
            Processed text
        """
        try:
            # Clean up text if enabled
            if self.text_cleanup:
                text = self._clean_text(text)
            
            # Detect language if enabled and not provided
            if self.language_detection and not language:
                language = self._detect_language(text)
            
            # Add SSML if enabled
            if self.ssml_enabled:
                text = self._add_ssml(text, language)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error processing text: {str(e)}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        text = re.sub(r'([.,!?])\s*([.,!?])', r'\1', text)
        
        # Fix spacing around quotes
        text = re.sub(r'\s*["\']\s*', '"', text)
        
        # Fix spacing around parentheses
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)
        
        return text.strip()

    def _detect_language(self, text: str) -> str:
        """Detect text language."""
        try:
            return detect(text)
        except:
            return 'en'  # Default to English if detection fails

    def _add_ssml(self, text: str, language: str) -> str:
        """Add SSML tags for better speech synthesis."""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            processed_sentences = []
            
            for sentence in sentences:
                # Add pauses for punctuation
                sentence = self._add_punctuation_pauses(sentence)
                processed_sentences.append(sentence)
            
            # Join sentences with appropriate pause
            paragraph_text = f'<break time="{self.sentence_pause}s"/>'.join(processed_sentences)
            processed_paragraphs.append(paragraph_text)
        
        # Join paragraphs with longer pause
        text = f'<break time="{self.paragraph_pause}s"/>'.join(processed_paragraphs)
        
        # Wrap in SSML
        return f'''<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
            {text}
        </speak>'''

    def _add_punctuation_pauses(self, text: str) -> str:
        """Add SSML breaks for punctuation."""
        # Add pauses for commas
        text = re.sub(r',', f'<break time="{self.punctuation_pause}s"/>', text)
        
        # Add pauses for semicolons
        text = re.sub(r';', f'<break time="{self.punctuation_pause}s"/>', text)
        
        # Add pauses for colons
        text = re.sub(r':', f'<break time="{self.punctuation_pause}s"/>', text)
        
        return text

    def split_into_chunks(self, text: str, max_chunk_size: int = 5000) -> List[str]:
        """Split text into manageable chunks for TTS processing."""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            if current_size + len(paragraph) > max_chunk_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = len(paragraph)
            else:
                current_chunk.append(paragraph)
                current_size += len(paragraph)
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks 