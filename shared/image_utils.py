"""
Image processing utilities for document analysis.
"""
import base64
from pathlib import Path
from typing import List, Union
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
from loguru import logger

from shared.config import settings


def image_to_base64_data_uri(image_path: Union[str, Path]) -> str:
    """
    Convert image to base64 data URI for API consumption.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded data URI string
    """
    image_path = Path(image_path)
    
    with open(image_path, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine image type from extension
    ext = image_path.suffix.lower().lstrip('.')
    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    
    return f"data:{mime_type};base64,{img_base64}"


def preprocess_image(
    image: Image.Image,
    max_width: int = None,
    contrast_factor: float = 1.5
) -> Image.Image:
    """
    Preprocess image to optimize for OCR and reduce size.
    
    Args:
        image: PIL Image object
        max_width: Maximum width in pixels (uses config if not specified)
        contrast_factor: Contrast enhancement factor (1.0 = no change)
        
    Returns:
        Preprocessed PIL Image
    """
    if max_width is None:
        max_width = settings.max_image_width
    
    # Convert to grayscale (reduces size and improves OCR)
    gray_image = image.convert('L')
    
    # Resize if image is too large
    if gray_image.width > max_width:
        # Calculate new height to maintain aspect ratio
        ratio = max_width / gray_image.width
        new_height = int(gray_image.height * ratio)
        gray_image = gray_image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        logger.debug(f"Resized image to {max_width}x{new_height}")
    
    # Increase contrast for better text recognition
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(contrast_factor)
    
    return enhanced_image


def convert_pdf_to_images(
    pdf_path: Union[str, Path],
    output_dir: Union[str, Path],
    max_width: int = None,
    dpi: int = None
) -> List[Path]:
    """
    Convert a PDF file to a set of preprocessed images.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output images
        max_width: Maximum width for output images (uses config if not specified)
        dpi: DPI for PDF conversion (uses config if not specified)
        
    Returns:
        List of paths to generated image files
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    
    if max_width is None:
        max_width = settings.max_image_width
    if dpi is None:
        dpi = settings.image_dpi
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Converting {pdf_path.name} to images...")
    
    # Convert PDF to images
    images = convert_from_path(str(pdf_path), dpi=dpi)
    generated_paths = []
    
    # Process and save each page
    for page_num, image in enumerate(images, start=1):
        # Preprocess the image
        processed_image = preprocess_image(image, max_width)
        
        # Save as JPEG with optimization
        output_path = output_dir / f"page_{page_num:03d}.jpg"
        processed_image.save(
            output_path,
            'JPEG',
            quality=settings.image_quality,
            optimize=True
        )
        
        logger.debug(f"Saved page {page_num} -> {output_path}")
        generated_paths.append(output_path)
    
    logger.info(f"Converted {len(generated_paths)} pages from {pdf_path.name}")
    return generated_paths


def process_uploaded_file(
    file_path: Union[str, Path],
    output_dir: Union[str, Path]
) -> List[Path]:
    """
    Process an uploaded file (PDF or image) and return image paths.
    
    Args:
        file_path: Path to uploaded file
        output_dir: Directory to save processed images
        
    Returns:
        List of paths to processed image files
    """
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if it's a PDF or image
    extension = file_path.suffix.lower()
    
    if extension == '.pdf':
        # Convert PDF to images
        return convert_pdf_to_images(file_path, output_dir)
    
    elif extension in ['.jpg', '.jpeg', '.png']:
        # Process single image
        logger.info(f"Processing image {file_path.name}")
        
        # Open and preprocess
        image = Image.open(file_path)
        processed_image = preprocess_image(image)
        
        # Save processed image
        output_path = output_dir / f"page_001.jpg"
        processed_image.save(
            output_path,
            'JPEG',
            quality=settings.image_quality,
            optimize=True
        )
        
        logger.info(f"Processed image saved to {output_path}")
        return [output_path]
    
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def cleanup_processed_files(directory: Union[str, Path]):
    """
    Clean up processed files in a directory.
    
    Args:
        directory: Directory to clean
    """
    directory = Path(directory)
    if directory.exists():
        for file in directory.glob("*"):
            if file.is_file():
                file.unlink()
                logger.debug(f"Deleted {file}")
