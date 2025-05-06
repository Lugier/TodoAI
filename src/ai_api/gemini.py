"""
Gemini API Helper

Simple interface for querying Google's Gemini API with text and images.
"""

import os
import base64
import time
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from typing import Optional, Union, Dict, Any, List
from dotenv import load_dotenv
from io import BytesIO
from src.config import GEMINI_API, UI, DEVELOPER

def query_gemini(prompt: str, image_path: Optional[Union[str, Path]] = None, 
                 max_output_tokens: Optional[int] = None) -> str:
    """
    Send a query to the Gemini API
    
    Args:
        prompt: The text prompt to send
        image_path: Optional path to an image to include with the prompt
        max_output_tokens: Maximum number of tokens in the response (uses config if not specified)
        
    Returns:
        str: The model's response
    """
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        error_msg = (
            "Error: GEMINI_API_KEY not found in environment variables.\n"
            "Please set up your .env file with your Gemini API key:\n"
            "GEMINI_API_KEY=your_api_key_here"
        )
        print(error_msg)
        return error_msg
    
    # Configure Gemini API - the API key is only used here and not stored in variables
    genai.configure(api_key=api_key)
    
    # Set generation config with values from config file
    generation_config = {
        "max_output_tokens": max_output_tokens or GEMINI_API["max_output_tokens"],
        "temperature": GEMINI_API["temperature"],
        "top_p": GEMINI_API["top_p"],
        "top_k": GEMINI_API["top_k"],
    }
    
    # Create model with enhanced configuration
    model = genai.GenerativeModel(
        GEMINI_API["model"],
        generation_config=generation_config
    )
    
    # Prepare content for API
    content = [{"role": "user", "parts": [prompt]}]
    
    # Add image if provided
    if image_path:
        # Open and compress image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (using config value)
            max_size = UI["max_screenshot_width"]
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to JPEG bytes with quality from config
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=UI["screenshot_quality"], optimize=True)
            image_data = buffer.getvalue()
        
        # Add image to content
        content[0]["parts"].append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
        })
    
    # Get response from API with retries
    timeout = GEMINI_API.get("timeout_seconds", 30)
    max_retries = GEMINI_API.get("retry_count", 3)
    retry_delay = GEMINI_API.get("retry_delay", 2.0)
    
    for retry in range(max_retries + 1):
        try:
            response = model.generate_content(
                content, 
                request_options={"timeout": timeout}
            )
            
            # Save API response for debugging if enabled - no sensitive data here
            if DEVELOPER["save_api_responses"]:
                save_response_for_debugging(prompt, response.text, image_path)
            
            return response.text
        
        except Exception as e:
            if retry < max_retries:
                # Log error and retry
                print(f"Error querying Gemini API (attempt {retry+1}/{max_retries+1}): {str(e)}")
                time.sleep(retry_delay)
            else:
                # Final attempt failed
                error_msg = f"Error querying Gemini API after {max_retries+1} attempts: {str(e)}"
                
                # Save error for debugging if enabled
                if DEVELOPER["save_api_responses"]:
                    save_response_for_debugging(prompt, error_msg, image_path, is_error=True)
                
                return error_msg

def save_response_for_debugging(prompt: str, response: str, image_path: Optional[Union[str, Path]] = None, is_error: bool = False):
    """
    Save API responses and prompts for debugging
    
    Args:
        prompt: The prompt sent to the API
        response: The response received
        image_path: Optional path to the image included in the request
        is_error: Whether this response is an error
    """
    import json
    from datetime import datetime
    
    # Create directory if it doesn't exist
    response_dir = Path(DEVELOPER["api_responses_path"])
    response_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "error_" if is_error else ""
    response_file = response_dir / f"{prefix}gemini_response_{timestamp}.json"
    
    # Create response data - no API keys or sensitive credentials stored
    response_data = {
        "timestamp": timestamp,
        "model": GEMINI_API["model"],
        "prompt": prompt,
        "response": response,
        "image_included": image_path is not None,
        "image_path": str(image_path) if image_path else None,
        "is_error": is_error,
        "config": {
            "temperature": GEMINI_API["temperature"],
            "top_p": GEMINI_API["top_p"],
            "top_k": GEMINI_API["top_k"],
            "max_output_tokens": GEMINI_API["max_output_tokens"]
        }
    }
    
    # Save to file
    with open(response_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)