from typing import List
import PyPDF2
from .base_reader import BaseReader

class PDFReader(BaseReader):
    """Reader for PDF files using PyPDF2"""
    
    def extract_text_chunks(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """
        Extract text from PDF file in chunks.
        
        Args:
            file_path: Path to the PDF file
            chunk_size: Size of each text chunk
            
        Returns:
            List of text chunks
        """
        try:
            chunks = []
            current_chunk = ""
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    words = text.split()
                    
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= chunk_size:
                            current_chunk += " " + word if current_chunk else word
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = word
                
                if current_chunk:
                    chunks.append(current_chunk)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}") 