from .base_reader import BaseReader

class MDReader(BaseReader):
    def extract_text_chunks(self, file_path, chunk_size=1000):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)] 