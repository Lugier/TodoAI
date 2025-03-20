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

## Demo Use Cases

The following demo videos showcase TodoAI in action:

1. **Using the console and writing texts**: [demo_use_cases/writing_text.mp4](demo_use_cases/writing_text.mp4)
   - Prompt: "Open a new terminal and run code saying hello YC. Then open Word and write a poem."
   - See how TodoAI can assist writing tasks and using the console

2. **Running python code**: [demo_use_cases/running_code.mp4](demo_use_cases/running_code.mp4)
   - Prompt: "Save my python file under my downloads Folder as 'hangman.py'. Then execute it via cmd."
   - Watch TodoAI execute code and perform programming-related tasks

3. **Ordering a book on Amazon**: [demo_use_cases/ordering_on_amazon.mp4](demo_use_cases/ordering_on_amazon.mp4)
   - Prompt: "Go to Amazon.com and buy the book the singularity is nearer from Kurzweil in paperback."
   - Example of TodoAI navigating e-commerce websites