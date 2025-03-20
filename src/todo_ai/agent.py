"""
TodoAI Agent Module

This module processes user task descriptions and breaks them down into step-by-step plans,
then executes each step until the task is completed or determined to be impossible.
"""

import os
import sys
import json
import time
import pyautogui
from pathlib import Path
from typing import Dict, List, Union, Optional

# Add the parent directory to the Python path so 'src' is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ai_api.gemini import query_gemini
from src.step_handler.step_handler import StepHandler
from src.templates.task_execution_template import TASK_EXECUTION_TEMPLATE

class TodoAIAgent:
    """
    Agent class that breaks down tasks into steps and executes them
    """
    
    def __init__(self, task_description: str, max_iterations: int = 20, delay_between_steps: float = 2.0):
        """
        Initialize the TodoAIAgent with a task
        
        Args:
            task_description (str): Description of the task to complete
            max_iterations (int): Maximum number of iterations before giving up
            delay_between_steps (float): Delay between executing steps (default: 2.0)
        """
        self.task_description = task_description
        self.max_iterations = max_iterations
        self.delay_between_steps = delay_between_steps
        self.step_history = []
        
        # Create project paths
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        self.screenshot_dir = project_root / "data" / "task_planner"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(self) -> str:
        """
        Take a screenshot of the current screen
        
        Returns:
            str: Path to the saved screenshot
        """
        # Generate unique timestamp for the filename
        timestamp = int(time.time() * 1000)  # millisecond precision timestamp
        screenshot_path = self.screenshot_dir / f"task_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(screenshot_path))
        return str(screenshot_path)
    
    def format_history(self) -> str:
        """
        Format the step history into a readable string
        
        Returns:
            str: Formatted history of steps taken and their results
        """
        if not self.step_history:
            return "No steps taken yet."
            
        history = "Steps executed so far:\n"
        for i, step in enumerate(self.step_history, 1):
            history += f"Step {i}:\n"
            history += f"  Description: {step['description']}\n"
            history += f"  Result: {step['result']}\n"
        return history
    
    def format_prompt(self) -> str:
        """
        Format the prompt for Gemini
            
        Returns:
            str: The formatted prompt
        """
        return TASK_EXECUTION_TEMPLATE.format(
            task_description=self.task_description,
            step_history=self.format_history()
        )
    
    def execute_step(self, step_description: str, expected_outcome: str) -> Dict[str, str]:
        """
        Execute a single step using the TaskAnalyzer
        
        Args:
            step_description (str): Description of the step to execute
            expected_outcome (str): Expected outcome of the step
            
        Returns:
            Dict[str, str]: Result of the step execution
        """
        
        # Create a StepHandler for this specific step
        step_handler = StepHandler(
            task_description=step_description,
            expected_outcome=expected_outcome,
            delay_between_attempts=self.delay_between_steps
        )
        
        # Execute the step
        try:
            result = step_handler.execute_task()
            if "result" in result and result["result"] == "success":
                return {
                    "status": "success",
                    "message": result.get("description", "Step completed successfully")
                }
            else:
                return {
                    "status": "failure",
                    "message": result.get("description", "Step failed")
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during step execution: {str(e)}"
            }
    
    def parse_response(self, response: str) -> Dict:
        """
        Clean the response to extract JSON

        Args:
            response (str): Response from Gemini
            
        Returns:
            Dict: Parsed response with status and details
        
        Raises:
            ValueError: If the response is not a valid JSON object 
        """
        response = self.clean_response(response)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            raise ValueError(f"Error parsing Gemini response: {response}")
    
    def clean_response(self, response: str) -> str:
        """
        Clean the response to extract the JSON object
        
        Args:
            response (str): Raw response from Gemini
            
        Returns:
            str: Cleaned JSON string
        """
        import re
        
        # Remove markdown code blocks
        response = re.sub(r'```(?:json)?', '', response)
        
        # Find the first { and the last } to extract the JSON object
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1:
            return response[start:end+1]
        
        return response
    
    def execute_task(self) -> str:
        """
        Execute the complete task by breaking it down into steps and executing each one
        
        Returns:
            str: Message about the task completion or failure
        """
        print(f"Starting task execution: {self.task_description}")
        iteration = 0
        
        while iteration < self.max_iterations:
            # Take initial screenshot
            screenshot_path = self.take_screenshot()
            
            # Format the prompt
            prompt = self.format_prompt()
            
            # Query Gemini
            response = query_gemini(prompt, screenshot_path)
            
            # Parse the response
            result = self.parse_response(response)
            
            # Handle the response
            if "status" in result:
                if result["status"] == "success":
                    return f"Task completed successfully: {result.get('message', '')}"
                    
                elif result["status"] == "failure":
                    return f"Task failed: {result.get('message', '')}"
                    
                elif result["status"] == "next_step":
                    step_description = result.get("description", "Unknown step")
                    expected_outcome = result.get("expected_outcome", "Step completed")
                    
                    # Execute the step
                    step_result = self.execute_step(step_description, expected_outcome)
                    
                    # Add to history
                    self.step_history.append({
                        "description": step_description,
                        "result": step_result.get("message", "Unknown result")
                    })
                    
                    # Wait for the step to complete
                    time.sleep(self.delay_between_steps)
                    
                    # Take another screenshot after the step
                    screenshot_path = self.take_screenshot()
            else:
                raise ValueError(f"Invalid response from Gemini: {result}")
            
            iteration += 1
        
        raise ValueError("Task timed out after {self.max_iterations} iterations")