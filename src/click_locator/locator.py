"""
Click Locator Module

This module provides functionality to locate UI elements on screen based on descriptions
by using Google Vision API annotations and Gemini to identify the elements.
"""

import os
import sys
import json
import pyautogui
import time
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any
from PIL import Image, ImageDraw

# Add the parent directory to the Python path so 'src' is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ai_api.gemini import query_gemini
from src.ai_api.vision import query_vision
from src.templates.click_location_template import CLICK_LOCATION_TEMPLATE
from src.click_locator.text_box_detector import detect_text_boxes

def take_screenshot() -> str:
    """
    Take a screenshot of the current screen
    
    Returns:
        str: Path to the saved screenshot
    """
    # Create screenshots directory if it doesn't exist
    project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    screenshot_dir = project_root / "data" / "click_locator"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Take and save screenshot with timestamp for uniqueness
    timestamp = int(time.time() * 1000)  # millisecond precision timestamp
    screenshot_path = screenshot_dir / f"locator_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(str(screenshot_path))

    return str(screenshot_path)

def format_vision_annotations(annotations: Dict[str, List]) -> Dict[str, str]:
    """
    Format Vision API annotations for the template
    
    Args:
        annotations (Dict): Dictionary containing text_annotations, logo_annotations, etc.
        
    Returns:
        Dict[str, str]: Formatted annotations as strings
    """
    formatted = {}
    
    # Helper function to extract bounding box from vertices
    def get_bounds_from_vertices(vertices):
        xs = [v.get('x', 0) for v in vertices]
        ys = [v.get('y', 0) for v in vertices]
        left = min(xs) if xs else 0
        top = min(ys) if ys else 0
        right = max(xs) if xs else 0
        bottom = max(ys) if ys else 0
        return left, top, right, bottom
    
    # Skip the first text annotation which is usually the entire text content
    text_annotations = annotations.get("text_annotations", [])[1:] if len(annotations.get("text_annotations", [])) > 0 else []
    
    # Format text annotations
    text_blocks = []
    for i, block in enumerate(text_annotations, 1):
        try:
            # Extract vertices from the bounding poly
            vertices = block.get("bounding_poly", {}).get("vertices", [])
            if not vertices:
                continue
                
            # Get the rectangle coordinates
            left, top, right, bottom = get_bounds_from_vertices(vertices)
            
            # Skip if the bounding box has zero area
            if left == right or top == bottom:
                continue
                
            text_blocks.append(
                f"{i}. '{block.get('description', '')}' at coordinates "
                f"({left}, {top}, {right}, {bottom}) "
                f"with confidence {block.get('score', 0):.2f}"
            )
        except Exception as e:
            print(f"Error formatting text block {i}: {e}")
    
    formatted["text_blocks"] = "\n".join(text_blocks) if text_blocks else "None detected"
    
    # Format logo annotations
    logos = []
    for i, logo in enumerate(annotations.get("logo_annotations", []), 1):
        try:
            # Extract vertices from the bounding poly
            vertices = logo.get("bounding_poly", {}).get("vertices", [])
            if not vertices:
                continue
                
            # Get the rectangle coordinates
            left, top, right, bottom = get_bounds_from_vertices(vertices)
            
            # Skip if the bounding box has zero area
            if left == right or top == bottom:
                continue
                
            logos.append(
                f"{i}. '{logo.get('description', '')}' at coordinates "
                f"({left}, {top}, {right}, {bottom}) "
                f"with confidence {logo.get('score', 0):.2f}"
            )
        except Exception as e:
            print(f"Error formatting logo {i}: {e}")
    
    formatted["logo_detections"] = "\n".join(logos) if logos else "None detected"

    # Format text box annotations
    text_boxes = []
    for i, box in enumerate(annotations.get("text_box_annotations", []), 1):
        try:
            left, top, width, height = box
            right = left + width
            bottom = top + height
            
            text_boxes.append(
                f"{i}. Text box at coordinates "
                f"({left}, {top}, {right}, {bottom})"
            )
        except Exception as e:
            print(f"Error formatting text box {i}: {e}")
    
    formatted["text_box_annotations"] = "\n".join(text_boxes) if text_boxes else "None detected"

    formatted["image_properties_annotations"] = "\n".join(annotations.get("image_properties_annotations", [])) if annotations.get("image_properties_annotations", []) else "None detected"

    image_properties = []
    for i, property in enumerate(annotations.get("image_properties_annotations", []), 1):
        try:
            vertices = property.get("bounding_poly", {}).get("vertices", [])
            if not vertices:
                continue
            
            left, top, right, bottom = get_bounds_from_vertices(vertices)

            if left == right or top == bottom:
                continue
            
            image_properties.append(
                f"{i}. '{property.get('description', '')}' at coordinates "
                f"({left}, {top}, {right}, {bottom}) "
            )
        except Exception as e:
            print(f"Error formatting image property {i}: {e}")
    
    formatted["image_properties_annotations"] = "\n".join(image_properties) if image_properties else "None detected"
            
    return formatted

def visualize_all_annotations(screenshot_path: str, annotations: Dict[str, List]) -> str:
    """
    Create a visualization of all annotations from Vision API
    
    Args:
        screenshot_path (str): Path to the screenshot
        annotations (Dict): Dictionary containing text_annotations, logo_annotations, etc.
        
    Returns:
        str: Path to the saved annotated image
    """
    
    # Open the image
    img = Image.open(screenshot_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("Arial", 16)
    except:
        font = None
    
    # Function to extract bounding box from vertices
    def get_bounds_from_vertices(vertices):
        xs = [v.get('x', 0) for v in vertices]
        ys = [v.get('y', 0) for v in vertices]
        left = min(xs) if xs else 0
        top = min(ys) if ys else 0
        right = max(xs) if xs else 0
        bottom = max(ys) if ys else 0
        return left, top, right, bottom
    
    # Draw text annotations (green)
    for i, block in enumerate(annotations.get("text_annotations", []), 1):
        try:
            # Extract vertices from the bounding poly
            vertices = block.get("bounding_poly", {}).get("vertices", [])
            if not vertices:
                continue
                
            # Get the rectangle coordinates
            left, top, right, bottom = get_bounds_from_vertices(vertices)
            
            # Skip if the bounding box has zero area
            if left == right or top == bottom:
                continue
                
            # Draw the rectangle
            draw.rectangle([(left, top), (right, bottom)], outline=(0, 255, 0), width=2)
            
            # Add a label with the text content
            text_content = block.get('description', '')[:15]
            label = f"T{i}: {text_content}"
            
            # Add background to label for better visibility
            text_width = len(label) * 7 if font is None else draw.textlength(label, font)
            draw.rectangle([(left, top-20), (left + text_width, top)], fill=(0, 0, 0, 180))
            
            if font:
                draw.text((left, top-18), label, fill=(0, 255, 0), font=font)
            else:
                draw.text((left, top-18), label, fill=(0, 255, 0))
        except Exception as e:
            print(f"Error drawing text block {i}: {e}")
    
    # Draw logo annotations (blue)
    for i, logo in enumerate(annotations.get("logo_annotations", []), 1):
        try:
            # Extract vertices from the bounding poly
            vertices = logo.get("bounding_poly", {}).get("vertices", [])
            if not vertices:
                continue
                
            # Get the rectangle coordinates
            left, top, right, bottom = get_bounds_from_vertices(vertices)
            
            # Skip if the bounding box has zero area
            if left == right or top == bottom:
                continue
                
            # Draw the rectangle
            draw.rectangle([(left, top), (right, bottom)], outline=(0, 0, 255), width=2)
            
            # Add a label with the logo description
            logo_desc = logo.get('description', '')[:15]
            confidence = logo.get('score', 0)
            label = f"L{i}: {logo_desc} ({confidence:.2f})"
            
            # Add background to label for better visibility
            text_width = len(label) * 7 if font is None else draw.textlength(label, font)
            draw.rectangle([(left, top-20), (left + text_width, top)], fill=(0, 0, 0, 180))
            
            if font:
                draw.text((left, top-18), label, fill=(0, 0, 255), font=font)
            else:
                draw.text((left, top-18), label, fill=(0, 0, 255))
                
        except Exception as e:
            print(f"Error drawing logo {i}: {e}")
    
    # Draw text box annotations (red)
    for i, box in enumerate(annotations.get("text_box_annotations", []), 1):
        try:
            # Unpack the box coordinates
            left, top, width, height = box
            right = left + width
            bottom = top + height
            
            # Draw the rectangle
            draw.rectangle([(left, top), (right, bottom)], outline=(255, 0, 0), width=2)
            
            # Add a label
            label = f"B{i}"
            
            # Add background to label for better visibility
            text_width = len(label) * 7 if font is None else draw.textlength(label, font)
            draw.rectangle([(left, top-20), (left + text_width, top)], fill=(0, 0, 0, 180))
            
            if font:
                draw.text((left, top-18), label, fill=(255, 0, 0), font=font)
            else:
                draw.text((left, top-18), label, fill=(255, 0, 0))
                
        except Exception as e:
            print(f"Error drawing text box {i}: {e}")

    # Save the annotated image with high quality
    all_annotations_path = screenshot_path.replace(".png", "_all_annotations.png")
    img.save(all_annotations_path, quality=95)
    
    return all_annotations_path

def find_element_coordinates(element_description: str) -> Tuple[int, int]:
    """
    Find the coordinates of a UI element based on its description
    
    Args:
        element_description (str): Description of the UI element
        
    Returns:
        Tuple[int, int]: (x, y) coordinates of the element's center
        
    Raises:
        ValueError: If no matching element could be found
    """
    
    # Take a screenshot
    screenshot_path = take_screenshot()
    
    # Get Vision API annotations
    annotations = query_vision(screenshot_path)
    
    # Add text box annotations using OpenCV MSER
    text_boxes = detect_text_boxes(screenshot_path)
    annotations["text_box_annotations"] = text_boxes

    # Create a visualization of all annotations
    visualize_all_annotations(screenshot_path, annotations)

    # Format annotations for the template
    formatted_annotations = format_vision_annotations(annotations)
    
    # Format the prompt for Gemini
    prompt = CLICK_LOCATION_TEMPLATE.format(
        element_description=element_description,
        **formatted_annotations
    )
    
    # Query Gemini
    response = query_gemini(prompt, screenshot_path)

    # Clean the response (remove code blocks if any)
    response = clean_response(response)
    
    # Parse the response (now directly the bounding box)
    box = json.loads(response)
    
    # Get the coordinates
    left = box.get("left", 0)
    top = box.get("top", 0)
    right = box.get("right", 0)
    bottom = box.get("bottom", 0)
    
    # Visualize the bounding box on the screenshot
    img = Image.open(screenshot_path)
    draw = ImageDraw.Draw(img)
    
    # Draw rectangle (outline in red)
    draw.rectangle([(left, top), (right, bottom)], outline="red", width=3)
    
    # Draw a crosshair at the center
    center_x = int((left + right) / 2)
    center_y = int((top + bottom) / 2)
    crosshair_size = 10
    
    # Horizontal line
    draw.line([(center_x - crosshair_size, center_y), (center_x + crosshair_size, center_y)], 
              fill="red", width=2)
    # Vertical line
    draw.line([(center_x, center_y - crosshair_size), (center_x, center_y + crosshair_size)], 
              fill="red", width=2)
    
    # Calculate the center coordinates
    x = center_x
    y = center_y
    
    # Apply coordinate transformation to account for display scaling and multiple monitors
    # Get the actual screen size
    actual_width, actual_height = pyautogui.size()
    
    # Get the screenshot dimensions
    screenshot_width, screenshot_height = img.size
    
    # Calculate scaling factors
    scale_x = actual_width / screenshot_width
    scale_y = actual_height / screenshot_height
    
    # Apply scaling to the coordinates
    adjusted_x = int(x * scale_x)
    adjusted_y = int(y * scale_y)
    
    # Save the annotated image
    clicked_path = screenshot_path.replace(".png", "_clicked.png")
    img.save(clicked_path)
    
    return (adjusted_x, adjusted_y)

def clean_response(response: str) -> str:
    """
    Clean the response to extract the JSON object.
    Removes markdown code blocks and other text outside the JSON object.
    
    Args:
        response (str): The raw response from the model
        
    Returns:
        str: The cleaned JSON string
    """
    import re
    
    # Remove markdown code blocks (```json and ```)
    response = re.sub(r'```(?:json)?', '', response)
    
    # Find the first { and the last } to extract the JSON object
    start = response.find('{')
    end = response.rfind('}')
    
    if start != -1 and end != -1:
        return response[start:end+1]
    
    return response
