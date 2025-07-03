from .base_reader import BaseReader
from docx import Document

class DOCXReader(BaseReader):
    def extract_text_chunks(self, file_path, chunk_size=1000):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        text = '\n'.join(full_text)
        # Split into chunks
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)] 