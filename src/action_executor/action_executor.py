"""
Action Executor module - Executes computer actions based on LLM instructions

This module provides functions to interpret action JSON and perform
the corresponding actions on the computer, such as:
- Clicking at specific coordinates
- Double-clicking at specific coordinates
- Typing text
- Scrolling
- Executing keyboard shortcuts (hotkeys)
"""

import os
import sys
import time
import pyautogui
import queue
from datetime import datetime, timedelta

# Add the parent directory to the Python path so 'src' is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the click locator
from src.click_locator.locator import find_element_coordinates

# Configure PyAutoGUI safety features
pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
pyautogui.PAUSE = 0.0  # Add pause between PyAutoGUI commands

# Rate limiting variables
MAX_REQUESTS_PER_MINUTE = 15
request_timestamps = queue.Queue(maxsize=MAX_REQUESTS_PER_MINUTE)

def enforce_rate_limit():
    """
    Enforce rate limiting to ensure no more than MAX_REQUESTS_PER_MINUTE requests
    in a rolling window of 60 seconds.
    
    This function will block until a request slot is available if the limit has been reached.
    """
    current_time = datetime.now()
    
    # If we haven't reached the maximum number of requests yet
    if request_timestamps.qsize() < MAX_REQUESTS_PER_MINUTE:
        request_timestamps.put(current_time)
        return
    
    # Queue is full, check if the oldest request is older than 60 seconds
    oldest_timestamp = request_timestamps.get()
    time_diff = (current_time - oldest_timestamp).total_seconds()
    
    # If the oldest request is less than 60 seconds old, we need to wait
    if time_diff < 60:
        wait_time = 60 - time_diff
        print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
        time.sleep(wait_time)
    
    # Add the current request to the queue
    request_timestamps.put(current_time)

def execute_action(action_data):
    """
    Execute an action based on the provided action data
    
    Args:
        action_data (dict): Dictionary containing action type and parameters
        
    Returns:
        bool: True if action was executed successfully, False otherwise
        
    Raises:
        ValueError: If the action type is unknown or parameters are invalid
        RuntimeError: If the action execution fails
    """
    action_type = action_data.get('action_type')
    if not action_type:
        raise ValueError("Missing 'action_type' in action data")
        
    parameters = action_data.get('parameters', {})
    if not parameters:
        raise ValueError("Missing 'parameters' in action data")
    
    if action_type == 'click':
        return handle_click(parameters)
    elif action_type == 'doubleclick':
        return handle_doubleclick(parameters)
    elif action_type == 'type':
        return handle_type(parameters)
    elif action_type == 'scroll':
        return handle_scroll(parameters)
    elif action_type == 'hotkey':
        return handle_hotkey(parameters)
    else:
        raise ValueError(f"Unknown action type: {action_type}")

def handle_click(parameters):
    """
    Handle a click action at the specified target
    
    Args:
        parameters (dict): Dictionary containing target description or x,y coordinates
        
    Returns:
        bool: True if action was executed successfully
        
    Raises:
        ValueError: If target description is missing
        RuntimeError: If the click action fails
    """
    # Support both old (x, y) and new (target) formats
    x = parameters.get('x')
    y = parameters.get('y')
    target = parameters.get('target')
    
    if x is not None and y is not None:
        # Use the provided coordinates
        try:
            print(f"Clicking at coordinates ({x}, {y})")
            pyautogui.click(x=x, y=y)
            return True
        except Exception as e:
            raise RuntimeError(f"Error during click action: {str(e)}")
    elif target:
        # Convert description to coordinates
        try:
            print(f"Searching for: {target}")
            x, y = find_element_coordinates(target)
            print(f"Clicking on: ({x}, {y})")
            pyautogui.click(x=x, y=y)
            return True
        except Exception as e:
            raise RuntimeError(f"Error during click action on '{target}': {str(e)}")
    else:
        raise ValueError("Missing target description or x,y coordinates for click action")

def handle_doubleclick(parameters):
    """
    Handle a double-click action at the specified target
    
    Args:
        parameters (dict): Dictionary containing target description or x,y coordinates
        
    Returns:
        bool: True if action was executed successfully
        
    Raises:
        ValueError: If target description is missing
        RuntimeError: If the doubleclick action fails
    """
    # Support both old (x, y) and new (target) formats
    x = parameters.get('x')
    y = parameters.get('y')
    target = parameters.get('target')
    
    if x is not None and y is not None:
        # Use the provided coordinates
        try:
            print(f"Double-clicking at coordinates ({x}, {y})")
            pyautogui.doubleClick(x=x, y=y)
            return True
        except Exception as e:
            raise RuntimeError(f"Error during doubleclick action: {str(e)}")
    elif target:
        # Convert description to coordinates
        try:
            print(f"Searching for: {target}")   
            x, y = find_element_coordinates(target)
            print(f"Double-clicking on: ({x}, {y})")
            pyautogui.doubleClick(x=x, y=y)
            return True
        except Exception as e:
            raise RuntimeError(f"Error during doubleclick action on '{target}': {str(e)}")
    else:
        raise ValueError("Missing target description or x,y coordinates for doubleclick action")

def handle_type(parameters):
    """
    Handle a type action with the specified text
    
    Args:
        parameters (dict): Dictionary containing text to type
        
    Returns:
        bool: True if action was executed successfully
        
    Raises:
        ValueError: If text is missing
        RuntimeError: If the type action fails
    """
    # Enforce rate limiting before executing the action
    enforce_rate_limit()
    
    text = parameters.get('text')
    
    if text is None:
        raise ValueError("Missing text for type action")
        
    try:
        print(f"Typing text: {text}")
        
        # Split the text into lines and clean up each line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            # If this is not the first line, press Enter first
            if i > 0:
                pyautogui.press('enter')
                time.sleep(0.1)  # Small delay between Enter and typing
            
            # Calculate proper indentation level
            # Count leading spaces and convert to tabs (4 spaces per tab)
            leading_spaces = len(line) - len(line.lstrip(' '))
            tab_count = leading_spaces // 4
            
            # Press tab the required number of times
            for _ in range(tab_count):
                pyautogui.press('tab')
                time.sleep(0.1)  # Small delay between tabs
            
            # Type the line without leading spaces
            pyautogui.typewrite(line.lstrip(' '))
            time.sleep(0.1)  # Small delay between typing lines
            
        return True
    except Exception as e:
        raise RuntimeError(f"Error during type action: {str(e)}")

def handle_scroll(parameters):
    """
    Handle a scroll action with the specified direction and amount
    
    Args:
        parameters (dict): Dictionary containing direction and amount
        
    Returns:
        bool: True if action was executed successfully
        
    Raises:
        ValueError: If direction or amount is missing or invalid
        RuntimeError: If the scroll action fails
    """
    direction = parameters.get('direction')
    amount = parameters.get('amount', 5)  # Default to 5 if not specified
    
    if direction is None:
        raise ValueError("Missing direction for scroll action")
        
    if direction not in ['up', 'down', 'left', 'right']:
        raise ValueError("Invalid scroll direction. Must be 'up', 'down', 'left', or 'right'")
    
    try:
        print(f"Scrolling {direction} by {amount}")
        if direction == 'up':
            pyautogui.scroll(amount)  # Positive value scrolls up
        elif direction == 'down':
            pyautogui.scroll(-amount)  # Negative value scrolls down
        elif direction == 'left':
            pyautogui.hscroll(-amount)  # Negative value scrolls left
        elif direction == 'right':
            pyautogui.hscroll(amount)  # Positive value scrolls right
            
        return True
    except Exception as e:
        raise RuntimeError(f"Error during scroll action: {str(e)}")

def handle_hotkey(parameters):
    """
    Handle a hotkey action with the specified keys
    
    Args:
        parameters (dict): Dictionary containing list of keys
        
    Returns:
        bool: True if action was executed successfully
        
    Raises:
        ValueError: If keys list is missing or empty
        RuntimeError: If the hotkey action fails
    """
    keys = parameters.get('keys')
    
    if not keys or not isinstance(keys, list):
        raise ValueError("Missing or invalid keys for hotkey action")
        
    try:
        print(f"Pressing hotkeys: {'+'.join(keys)}")
        pyautogui.hotkey(*keys)
        return True
    except Exception as e:
        raise RuntimeError(f"Error during hotkey action: {str(e)}") 