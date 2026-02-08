"""
Shared utilities package for Document Analyzer.
"""
from .config import settings
from .ai_service import analyzer
from .image_utils import (
    image_to_base64_data_uri,
    preprocess_image,
    convert_pdf_to_images,
    process_uploaded_file,
    cleanup_processed_files
)
from .prompts import get_extraction_prompt

__all__ = [
    'settings',
    'analyzer',
    'image_to_base64_data_uri',
    'preprocess_image',
    'convert_pdf_to_images',
    'process_uploaded_file',
    'cleanup_processed_files',
    'get_extraction_prompt'
]
