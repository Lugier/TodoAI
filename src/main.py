"""
Computer Automation Agent - Main Script

This script implements the complete workflow of the automation agent:
1. Asks the user for a task description
2. Uses the TaskExecutor to break down and execute the task
3. Reports the result to the user
"""

import sys
import os
import time
import shutil
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the TodoAIAgent
from todo_ai.agent import TodoAIAgent

def cleanup_screenshots():
    """
    Clean up all screenshot files from previous runs
    """
    # Get the project root directory
    project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Hardcoded screenshot directories
    directories = [
        project_root / "data" / "task_planner",
        project_root / "data" / "click_locator",
        project_root / "data" / "step_handler"
    ]
    
    # Clear each directory
    for directory in directories:
        if directory.exists():
            for screenshot in directory.glob("*.png"):
                try:
                    os.remove(screenshot)
                except Exception as e:
                    raise e

def print_banner():
    """Print a banner for the application"""
    print("\n" + "=" * 60)
    print(" TodoAI Agent ".center(60, "="))
    print("=" * 60)
    print("\nThis program will help you automate computer tasks.\n")
    print("Simply describe what you want to do, and I'll try to execute it.")
    print("\nNote: Make sure to grant accessibility permissions to the terminal.")
    print("=" * 60 + "\n")

def get_user_task():
    """
    Get the task description from the user
    
    Returns:
        str: Task description
    """
    try:
        task = input("Please describe the task you want to automate: ")
        while not task.strip():
            print("Task description cannot be empty. Please try again.")
            task = input("Please describe the task you want to automate: ")
        return task.strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)

def main():
    """
    Main function that implements the complete automation workflow
    """
    # Print banner
    print_banner()
    
    # Clean up all screenshots
    cleanup_screenshots()
    
    # Get task from user
    task_description = get_user_task()
    
    # Execute the task using TodoAIAgent
    agent = TodoAIAgent(task_description)
    result = agent.execute_task()
    
    # Print the result
    print("\n" + "=" * 60)
    print(f"\n{result}\n")
    print("=" * 60)

if __name__ == "__main__":
    main()