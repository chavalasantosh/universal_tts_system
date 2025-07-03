#!/usr/bin/env python3
"""
Text file reader for Universal TTS System
"""

from .base_reader import BaseReader

class TxtReader(BaseReader):
    """Reader for plain text files"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.txt']
    
    def extract_text_chunks(self, file_path: str, chunk_size: int = 1000) -> list:
        """
        Extract text from a text file in chunks
        
        Args:
            file_path: Path to the text file
            chunk_size: Size of each text chunk
            
        Returns:
            list: List of text chunks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split text into chunks
            chunks = []
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                if chunk.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
            
            return chunks
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}") 