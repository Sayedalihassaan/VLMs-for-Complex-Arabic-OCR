"""
Shared utilities package for Document Analyzer.
"""
from shared.config import settings
from shared.ai_service import analyzer
from shared.image_utils import (
    image_to_base64_data_uri,
    preprocess_image,
    convert_pdf_to_images,
    process_uploaded_file,
    cleanup_processed_files
)
from shared.prompts import get_extraction_prompt

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
