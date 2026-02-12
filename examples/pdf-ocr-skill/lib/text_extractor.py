"""
Text Extractor Module
High-level interface combining PDF processing and OCR
"""

from typing import List, Optional, NamedTuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageResult:
    """Result for a single page"""
    page_num: int
    text: Optional[str]
    has_ocr: bool = False
    error: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ExtractionResult:
    """Result for complete PDF extraction"""
    file_path: str
    pages: List[PageResult] = field(default_factory=list)
    total_pages: int = 0
    success_count: int = 0
    error_count: int = 0
    
    @property
    def full_text(self) -> str:
        """Get concatenated text from all pages"""
        texts = [p.text for p in self.pages if p.text]
        return "\n\n".join(texts)


class TextExtractor:
    """
    High-level text extraction interface.
    
    Combines PDFProcessor and OCREngine to provide easy-to-use
    text extraction from PDF documents.
    """
    
    def __init__(self, ocr_engine=None):
        """
        Initialize the text extractor.
        
        Args:
            ocr_engine: Optional OCREngine instance (creates default if None)
        """
        from .pdf_processor import PDFProcessor
        from .ocr_engine import OCREngine
        
        self.pdf_processor = PDFProcessor()
        self.ocr_engine = ocr_engine or OCREngine()
    
    def extract_from_pdf(self, path: str, use_ocr: bool = True) -> ExtractionResult:
        """
        Extract text from a PDF document.
        
        Args:
            path: Path to the PDF file
            use_ocr: Whether to use OCR for pages without text layer
            
        Returns:
            ExtractionResult with all extracted text
            
        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidPDFError: If file is not a valid PDF
        """
        # TODO: Implement extraction logic
        pass
    
    def extract_from_page(self, path: str, page_num: int, use_ocr: bool = True) -> PageResult:
        """
        Extract text from a single page.
        
        Args:
            path: Path to the PDF file
            page_num: Page number (0-indexed)
            use_ocr: Whether to use OCR if no text layer
            
        Returns:
            PageResult for the specified page
        """
        # TODO: Implement
        pass
    
    def batch_extract(self, paths: List[str], use_ocr: bool = True) -> List[ExtractionResult]:
        """
        Extract text from multiple PDF files.
        
        Args:
            paths: List of PDF file paths
            use_ocr: Whether to use OCR for pages without text layer
            
        Returns:
            List of ExtractionResult, one per file
        """
        # TODO: Implement batch processing with error handling
        pass
