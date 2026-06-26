import pypdf
from app.config import settings

class PDFService:
    def extract_text(self, file_path: str) -> str:
        """Extracts all text content from a PDF file."""
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
            
        return text

    def extract_pages(self, file_path: str) -> list[str]:
        """Extracts text content page-by-page from a PDF file."""
        pages = []
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        except Exception as e:
            raise Exception(f"Failed to extract pages from PDF: {str(e)}")
        return pages

    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
        """Splits text into overlapping chunks for AI consumption."""
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if overlap is None:
            overlap = settings.CHUNK_OVERLAP

        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start pointer forward by chunk_size - overlap
            start += chunk_size - overlap
            # Guard against infinite loops if overlap >= chunk_size
            if overlap >= chunk_size:
                start += chunk_size
                
        return chunks

pdf_service = PDFService()
