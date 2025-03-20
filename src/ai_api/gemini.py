"""
Gemini API Helper

Simple interface for querying Google's Gemini API with text and images.
"""

import os
import base64
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from typing import Optional, Union
from dotenv import load_dotenv
from io import BytesIO

def query_gemini(prompt: str, image_path: Optional[Union[str, Path]] = None) -> str:
    """
    Send a query to the Gemini API
    
    Args:
        prompt: The text prompt to send
        image_path: Optional path to an image to include with the prompt
        
    Returns:
        str: The model's response
    """
    # Load API key from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
    
    # Prepare content for API
    content = [{"role": "user", "parts": [prompt]}]
    
    # Add image if provided
    if image_path:
        # Open and compress image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 1280px on longest side)
            max_size = 1280
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to JPEG bytes
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=75, optimize=True)
            image_data = buffer.getvalue()
        
        # Add image to content
        content[0]["parts"].append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
        })
    
    # Get response from API
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error querying Gemini API: {str(e)}"