from ebooklib import epub
from bs4 import BeautifulSoup
from typing import Optional, List
import os
from utils.logger import TTSLogger
from utils.exceptions import FileReaderError

class EPUBReader:
    """Reader for extracting text from EPUB files."""

    def __init__(self):
        self.logger = TTSLogger()

    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        try:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}")
                return None

            print(f"Reading EPUB file: {file_path}")
            book = epub.read_epub(file_path)
            
            # Get book metadata
            title = book.get_metadata('DC', 'title')
            print(f"Book title: {title[0][0] if title else 'Unknown'}")
            
            text = []
            items = list(book.get_items())  # Convert generator to list
            total_items = len(items)
            print(f"Found {total_items} items in the book")
            
            for i, item in enumerate(items, 1):
                if item.get_type() == 9:
                    print(f"Processing item {i}/{total_items}")
                    content = item.get_content()
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        # Get text and clean it
                        item_text = soup.get_text(separator='\n', strip=True)
                        if item_text:
                            text.append(item_text)
            
            if not text:
                print("Warning: No text content found in the EPUB file")
                return None
                
            final_text = '\n\n'.join(text)
            print(f"Successfully extracted {len(final_text)} characters of text")
            return final_text
            
        except Exception as e:
            print(f"Error reading EPUB: {str(e)}")
            return None 

    def extract_text_chunks(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """Extract text from EPUB file in chunks"""
        try:
            book = epub.read_epub(file_path)
            chunks = []
            current_chunk = []
            current_size = 0
            
            for item in book.get_items():
                if item.get_type() == 9:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    
                    # Split text into sentences
                    sentences = text.split('. ')
                    
                    for sentence in sentences:
                        sentence = sentence.strip() + '. '
                        sentence_size = len(sentence)
                        
                        if current_size + sentence_size > chunk_size and current_chunk:
                            chunks.append(''.join(current_chunk))
                            current_chunk = []
                            current_size = 0
                        
                        current_chunk.append(sentence)
                        current_size += sentence_size
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append(''.join(current_chunk))
            
            return chunks
        except Exception as e:
            self.logger.error(f"Error reading EPUB file: {str(e)}")
            raise FileReaderError(f"Failed to read EPUB file: {str(e)}") 