from .base_reader import BaseReader
try:
    from ebooklib import epub
    import mobi
except ImportError:
    epub = None
    mobi = None

class MOBIReader(BaseReader):
    def extract_text_chunks(self, file_path, chunk_size=1000):
        text = ""
        # Try mobi module
        if mobi:
            try:
                book = mobi.Mobi(file_path)
                book.parse()
                text = book.getText()
            except Exception:
                pass
        # Try ebooklib as fallback
        if not text and epub:
            try:
                book = epub.read_epub(file_path)
                items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
                text = " ".join([item.get_content().decode(errors='ignore') for item in items])
            except Exception:
                pass
        # Fallback: just read as binary and decode
        if not text:
            with open(file_path, 'rb') as f:
                text = f.read().decode(errors='ignore')
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)] 