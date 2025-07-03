#!/usr/bin/env python3
"""
Reader factory for Universal TTS System
"""

from typing import Optional
from .base_reader import BaseReader
from .epub_reader import EPUBReader
from .pdf_reader import PDFReader
from .docx_reader import DOCXReader
from .md_reader import MDReader
from .mobi_reader import MOBIReader
from .txt_reader import TxtReader

class ReaderFactory:
    """Factory for creating appropriate file readers"""
    
    def __init__(self):
        self.readers = {
            'pdf': PDFReader(),
            'epub': EPUBReader(),
            'docx': DOCXReader(),
            'mobi': MOBIReader(),
            'md': MDReader(),
            'txt': TxtReader()
        }
    
    def get_reader(self, file_type: str) -> Optional[BaseReader]:
        """
        Get appropriate reader for file type
        
        Args:
            file_type: File extension (e.g., 'pdf', 'txt')
            
        Returns:
            Reader instance or None if no reader available
        """
        return self.readers.get(file_type.lower())

    def list_supported_types(self):
        return ["txt", "pdf", "docx", "html", "json", "md", "mobi"]
