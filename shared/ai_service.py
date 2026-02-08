"""
AI service for document analysis using LiteLLM and OpenRouter.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Union
from litellm import completion
from loguru import logger

from .config import settings
from .prompts import get_extraction_prompt
from .image_utils import image_to_base64_data_uri


class DocumentAnalyzer:
    """Service class for analyzing documents using AI."""
    
    def __init__(self):
        """Initialize the document analyzer."""
        self.model_id = settings.model_id
        self.max_tokens = settings.max_tokens
        self.prompt = get_extraction_prompt()
        logger.info(f"DocumentAnalyzer initialized with model: {self.model_id}")
    
    def analyze_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a single document image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Parsed JSON response from the model
            
        Raises:
            Exception: If analysis fails
        """
        image_path = Path(image_path)
        logger.info(f"Analyzing image: {image_path.name}")
        
        try:
            # Convert image to base64
            image_data_uri = image_to_base64_data_uri(image_path)
            
            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_uri}
                        }
                    ]
                }
            ]
            
            # Call the model
            logger.debug(f"Calling model {self.model_id}...")
            response = completion(
                model=self.model_id,
                messages=messages,
                max_tokens=self.max_tokens
            )
            
            # Extract response content
            content = response.choices[0].message.content
            logger.debug(f"Received response ({len(content)} chars)")
            
            # Parse JSON response
            result = self._parse_response(content)
            
            logger.info(f"Successfully analyzed {image_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {image_path.name}: {str(e)}")
            raise
    
    def analyze_multiple_images(
        self,
        image_paths: List[Union[str, Path]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple document images.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of parsed JSON responses
        """
        logger.info(f"Analyzing {len(image_paths)} images")
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {i}/{len(image_paths)}")
            try:
                result = self.analyze_image(image_path)
                result['_metadata'] = {
                    'page_number': i,
                    'total_pages': len(image_paths),
                    'source_file': str(image_path)
                }
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze image {i}: {str(e)}")
                results.append({
                    'error': str(e),
                    '_metadata': {
                        'page_number': i,
                        'total_pages': len(image_paths),
                        'source_file': str(image_path)
                    }
                })
        
        logger.info(f"Completed analysis of {len(results)} images")
        return results
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse the model response into JSON.
        
        Args:
            content: Raw response content
            
        Returns:
            Parsed JSON object
        """
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw content: {content[:500]}...")
            raise ValueError(f"Invalid JSON response from model: {str(e)}")


# Global analyzer instance
analyzer = DocumentAnalyzer()
