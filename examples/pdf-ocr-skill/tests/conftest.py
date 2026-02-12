"""
Test fixtures and utilities for PDF OCR Skill tests
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.pdf_processor import PDFProcessor, DocumentHandle
from lib.ocr_engine import OCREngine, OCRResult
from lib.text_extractor import TextExtractor, PageResult, ExtractionResult


@pytest.fixture
def sample_pdf_path():
    """Path to a sample PDF file for testing"""
    return "tests/fixtures/sample.pdf"


@pytest.fixture
def mock_pdf_document():
    """Mock PDF document handle"""
    doc = MagicMock()
    doc.page_count = 10
    doc.metadata = {"title": "Test Document"}
    return doc


@pytest.fixture
def pdf_processor():
    """PDFProcessor instance"""
    return PDFProcessor()


@pytest.fixture
def mock_fitz():
    """Mock PyMuPDF fitz module"""
    with pytest.mock.patch('lib.pdf_processor.fitz') as mock:
        yield mock


@pytest.fixture
def ocr_engine():
    """OCREngine instance"""
    engine = OCREngine()
    engine.initialize = Mock()
    engine.process_image = Mock(return_value=OCRResult(
        text="Extracted text",
        confidence=0.95,
        language="eng",
        word_count=10
    ))
    return engine


@pytest.fixture
def text_extractor(ocr_engine):
    """TextExtractor instance with mocked OCR"""
    return TextExtractor(ocr_engine=ocr_engine)


@pytest.fixture
def sample_page_result():
    """Sample PageResult for testing"""
    return PageResult(
        page_num=0,
        text="Sample extracted text",
        has_ocr=True,
        confidence=0.95
    )


@pytest.fixture
def sample_extraction_result():
    """Sample ExtractionResult for testing"""
    return ExtractionResult(
        file_path="tests/fixtures/sample.pdf",
        pages=[
            PageResult(page_num=0, text="Page 1 text", has_ocr=True),
            PageResult(page_num=1, text="Page 2 text", has_ocr=True),
        ],
        total_pages=2,
        success_count=2,
        error_count=0
    )


@pytest.fixture
def empty_pdf():
    """Mock empty PDF (0 pages)"""
    doc = MagicMock()
    doc.page_count = 0
    return doc
