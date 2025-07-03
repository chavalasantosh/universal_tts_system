from typing import List
import PyPDF2
import os
from .base_reader import BaseReader

class PDFReader(BaseReader):
    """Reader for PDF files using PyPDF2"""
    
    def extract_text_chunks(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """
        Extract text from PDF file in chunks.
        Falls back to text file reading if PDF reading fails.
        
        Args:
            file_path: Path to the PDF file
            chunk_size: Size of each text chunk
            
        Returns:
            List of text chunks
        """
        try:
            # Try reading as PDF first
            chunks = []
            current_chunk = ""
            
            with open(file_path, 'rb') as file:
                try:
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
                    
                    if chunks:  # If we successfully read PDF content
                        return chunks
                        
                except Exception as pdf_error:
                    print(f"PDF reading failed: {str(pdf_error)}")
            
            # Fallback to text file reading
            print("Falling back to text file reading...")
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split text into chunks
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                if chunk.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}") 