"""
Google Vision API Helper

Simple interface for getting annotations from Google's Vision API,
optimized for computer screenshots with German text, logos, and icons.
"""

import os
from pathlib import Path
from typing import Optional, Union, Dict, Any
from google.cloud import vision
from dotenv import load_dotenv

def query_vision(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get annotations from Google Vision API optimized for computer screenshots
    
    Args:
        image_path: Path to the screenshot to analyze
        
    Returns:
        dict: The Vision API response containing text, logo, and object annotations
        
    Raises:
        ValueError: If credentials path is not found in .env file
        FileNotFoundError: If the image file or credentials file doesn't exist
    """
    # Load environment variables from .env
    load_dotenv()
    
    # Get credentials path from .env
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in .env file")
    
    # Convert to absolute path if relative
    if not os.path.isabs(credentials_path):
        # Get the project root directory (two levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        credentials_path = os.path.join(project_root, credentials_path)
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
    
    # Set the credentials environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
    # Check if image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Initialize Vision API client
    client = vision.ImageAnnotatorClient()
    
    # Load the image
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    
    # Set up image context optimized for German computer UI
    image_context = vision.ImageContext(
        language_hints=['de'],  # German language hint
        text_detection_params=vision.TextDetectionParams(
            enable_text_detection_confidence_score=True  # Enable confidence scores for text detection
        )
    )
    
    # Create request with features optimized for computer screenshots
    request = vision.AnnotateImageRequest(
        image=image,
        features=[
            # DOCUMENT_TEXT_DETECTION is better for UI text than TEXT_DETECTION
            vision.Feature(type=vision.Feature.Type.DOCUMENT_TEXT_DETECTION),
            # Detect logos (app icons, company logos, etc.)
            vision.Feature(type=vision.Feature.Type.LOGO_DETECTION),
            # Detect objects (helps with identifying UI elements and icons)
            vision.Feature(type=vision.Feature.Type.OBJECT_LOCALIZATION),
            # Get image properties (can help with identifying UI elements)
            vision.Feature(type=vision.Feature.Type.IMAGE_PROPERTIES)
        ],
        image_context=image_context
    )
    
    # Send request and process response
    try:
        response = client.annotate_image(request=request)
        result = vision.AnnotateImageResponse.to_dict(response)
        return result
        
    except Exception as e:
        return {"error": f"Error querying Vision API: {str(e)}"}
