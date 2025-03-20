"""
Step Handler Module

This module analyzes screenshots and determines the next step to take to complete a task
by using the Gemini API to understand the current state and required actions.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Union, Optional
import re
import pyautogui
import time
import json

# Add the parent directory to the Python path so 'src' is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ai_api.gemini import query_gemini
from src.templates.action_analysis_template import ACTION_ANALYSIS_TEMPLATE
from src.action_executor.action_executor import execute_action

class MaxAttemptsExceeded(Exception):
    """Raised when the maximum number of attempts is exceeded"""
    pass

class GeminiResponseError(Exception):
    """Raised when the Gemini response is not valid JSON"""
    pass

class StepHandler:
    """
    Step Handler class that uses Gemini to determine actions needed to complete a task
    """
    
    def __init__(self, task_description: str, expected_outcome: str, max_attempts: int = 10, delay_between_attempts: float = 2.0):
        """
        Initialize the StepHandler with a specific task
        
        Args:
            task_description (str): Description of the task to complete (e.g. "Open Google Chrome")
            expected_outcome (str): Expected outcome when task is complete (e.g. "Google Chrome browser is visible")
            max_attempts (int): Maximum number of attempts before giving up (default: 10)
            delay_between_attempts (float): Delay in seconds between attempts (default: 2.0)
            
        Raises:
            ValueError: If max_attempts is less than 1
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
            
        self.task_description = task_description
        self.expected_outcome = expected_outcome
        self.step_history: List[Dict] = []
        
        # Use absolute path to the project's data directory
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        self.screenshot_dir = project_root / "data" / "step_handler"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_attempts = max_attempts
        self.delay_between_attempts = delay_between_attempts
    
    def take_screenshot(self) -> str:
        """
        Take a screenshot of the current screen state
        
        Returns:
            str: Path to the saved screenshot
        """
        # Generate unique timestamp for the filename
        timestamp = int(time.time() * 1000)  # millisecond precision timestamp
        screenshot_path = self.screenshot_dir / f"step_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        
        # Save the screenshot
        screenshot.save(str(screenshot_path))
        return str(screenshot_path)
    
    def format_history(self) -> str:
        """
        Format the step history into a readable string
        
        Returns:
            str: Formatted history of steps taken
        """
        if not self.step_history:
            return "No steps taken yet."
            
        history = "Previous steps taken:\n"
        for i, step in enumerate(self.step_history, 1):
            history += f"{i}. Action: {step['action_type']} - {json.dumps(step['parameters'])}\n"
        return history
    
    def format_prompt(self) -> str:
        """
        Format the prompt for Gemini using the template
            
        Returns:
            str: The formatted prompt
        """
        return ACTION_ANALYSIS_TEMPLATE.format(
            task_description=self.task_description,
            expected_outcome=self.expected_outcome,
            step_history=self.format_history(),
        )
    
    def execute_task(self) -> Dict[str, Union[str, Dict[str, Union[str, List[str]]]]]:
        """
        Execute a task by taking screenshots, analyzing them, and executing actions until 
        success or failure is determined.
        
        Returns:
            dict: Either a success or problem response
            
        Raises:
            MaxAttemptsExceeded: If the maximum number of attempts is exceeded
            GeminiResponseError: If the Gemini response is not valid JSON
        """
        attempt = 0
        
        # Log the start of the task
        print(f"Starting task: {self.task_description}")
        
        while attempt < self.max_attempts:
            # Take initial screenshot
            screenshot_path = self.take_screenshot()
            
            # Format the prompt
            prompt = self.format_prompt()
            
            # Query Gemini
            response = query_gemini(prompt, screenshot_path)
            
            # Clean the response to remove markdown code blocks
            cleaned_response = clean_response(response)
            
            # Parse the response
            try:
                result = json.loads(cleaned_response)
            except json.JSONDecodeError:
                raise GeminiResponseError(f"Invalid response format from model: {response}")
            
            # Handle success or problem responses - immediately return without adding to history
            if "result" in result:
                if result["result"] == "success":
                    print(f"Success: {result.get('description', 'No description provided')}")
                    return result
                elif result["result"] == "problem":
                    print(f"Problem: {result.get('description', 'No description provided')}")
                    return result
                
            # Add the action to history
            self.step_history.append(result)
            
            # Execute the action
            execute_action(result)
            
            # Wait for the action to complete
            time.sleep(self.delay_between_attempts)
            
            # Take another screenshot after the action
            screenshot_path = self.take_screenshot()
            
            attempt += 1
        
        # If we've exceeded max attempts, raise an exception
        raise MaxAttemptsExceeded(f"Exceeded maximum number of attempts ({self.max_attempts}) without success or clear action")

def clean_response(response: str) -> str:
    """
    Clean the response to extract the JSON object.
    Removes markdown code blocks and other text outside the JSON object.
    
    Args:
        response (str): The raw response from the model
        
    Returns:
        str: The cleaned JSON string
    """
    # Remove markdown code blocks (```json and ```)
    response = re.sub(r'```(?:json)?', '', response)
    
    # Find the first { and the last } to extract the JSON object
    start = response.find('{')
    end = response.rfind('}')
    
    if start != -1 and end != -1:
        return response[start:end+1]
    
    return response

