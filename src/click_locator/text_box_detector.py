import cv2
import numpy as np
import os

def detect_text_boxes(image_path):
    """
    Detects potential text boxes in an image using OpenCV MSER
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of bounding boxes (x, y, w, h)
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    # Get bounding boxes using only MSER method
    mser_boxes = detect_boxes_mser(image)
    
    # Merge overlapping boxes
    merged_boxes = merge_overlapping_boxes(mser_boxes)
    
    return merged_boxes

def detect_boxes_mser(image):
    """
    Detects text regions using MSER (Maximally Stable Extremal Regions)
    
    Args:
        image: Input image
        
    Returns:
        List of bounding boxes (x, y, w, h)
    """
    # Get image dimensions for size filtering
    height, width = image.shape[:2]
    
    # Calculate minimum size threshold (5% of screen size)
    min_width = int(width * 0.05)
    min_height = int(height * 0.05)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Initialize MSER detector
    mser = cv2.MSER_create()
    
    # Detect regions
    regions, _ = mser.detectRegions(gray)
    
    bounding_boxes = []
    
    for region in regions:
        # Get bounding box for each region
        x, y, w, h = cv2.boundingRect(region)
        
        # Filter based on size and aspect ratio
        area = w * h
        aspect_ratio = float(w) / h
        
        # Only keep boxes that:
        # 1. Have sufficient area
        # 2. Have reasonable aspect ratio
        # 3. Are at least 5% of screen size on at least one axis
        if (area > 100 and 
            0.1 <= aspect_ratio <= 10 and 
            (w >= min_width or h >= min_height)):
            bounding_boxes.append((x, y, w, h))
    
    return bounding_boxes

def merge_overlapping_boxes(boxes, overlap_thresh=0.8):
    """
    Merge boxes that have significant overlap
    
    Args:
        boxes: List of bounding boxes (x, y, w, h)
        overlap_thresh: Threshold for overlap ratio
        
    Returns:
        List of merged bounding boxes
    """
    if len(boxes) == 0:
        return []
    
    # Initialize list of merged boxes
    merged_boxes = []
    
    # Create a copy of boxes to modify
    remaining_boxes = boxes.copy()
    
    while len(remaining_boxes) > 0:
        # Take the first box as reference
        current_box = remaining_boxes.pop(0)
        x1, y1, w1, h1 = current_box
        
        # Boxes to be merged with the current box
        to_merge = []
        
        # Indices of boxes to be removed
        to_remove = []
        
        # Check overlap with all remaining boxes
        for i, box in enumerate(remaining_boxes):
            x2, y2, w2, h2 = box
            
            # Calculate overlap area
            x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            overlap_area = x_overlap * y_overlap
            
            # Calculate area of each box
            area1 = w1 * h1
            area2 = w2 * h2
            
            # Calculate overlap ratio relative to the smaller box
            overlap_ratio = overlap_area / min(area1, area2)
            
            # If overlap is significant, add to merge list
            if overlap_ratio > overlap_thresh:
                to_merge.append(box)
                to_remove.append(i)
        
        # If boxes to merge were found
        if to_merge:
            # Calculate combined box that includes all overlapping boxes
            all_boxes = [current_box] + to_merge
            min_x = min(box[0] for box in all_boxes)
            min_y = min(box[1] for box in all_boxes)
            max_x = max(box[0] + box[2] for box in all_boxes)
            max_y = max(box[1] + box[3] for box in all_boxes)
            
            # Create merged box
            merged_box = (min_x, min_y, max_x - min_x, max_y - min_y)
            merged_boxes.append(merged_box)
            
            # Remove merged boxes from the remaining list
            for i in sorted(to_remove, reverse=True):
                remaining_boxes.pop(i)
        else:
            # If no boxes to merge, keep the current box as is
            merged_boxes.append(current_box)
    
    return merged_boxes 