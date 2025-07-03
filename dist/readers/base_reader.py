from abc import ABC, abstractmethod
from typing import List

class BaseReader(ABC):
    """Base class for all file readers"""
    
    @abstractmethod
    def extract_text_chunks(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """
        Extract text from file in chunks.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of each text chunk
            
        Returns:
            List of text chunks
        """
        pass 