# TodoAI

A desktop automation tool that executes computer tasks based on natural language instructions. The agent uses LLMs to interpret commands, break them down into steps, and execute them by analyzing the screen.

## Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure to configure your .env file with Google API credentials
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
# GEMINI_API_KEY=your_gemini_api_key
```

## Usage

```bash
source venv/bin/activate && python src/main.py
```

## Implement the agent on your own

```python
from todo_ai.agent import TodoAIAgent

# Initialize the agent with your task
agent = TodoAIAgent("Open Chrome and navigate to github.com")

# Execute the task
result = agent.execute_task()
print(result)
```
