# Contributing to the Computer Automation Agent

Thank you for your interest in contributing to the Computer Automation Agent! This document provides guidelines and best practices for contributors.

## Security Guidelines

### 🔐 Handling Sensitive Data

1. **API Keys and Credentials**:
   - Store API keys and credentials EXCLUSIVELY in the `.env` file
   - NEVER include sensitive data directly in code
   - Always use example keys or placeholders for tests

2. **Screenshots and Test Data**:
   - NEVER commit screenshots, logs, or other output files
   - Carefully check each commit for accidentally added sensitive data
   - If accidentally transmitted: Immediately revoke affected keys/credentials

3. **Data Directory**:
   - Strictly adhere to the guidelines in `data/README.md`
   - Use `.gitkeep` files to maintain empty directories
   - Only add the directory structure, never the contents

## Development Process

### 🌿 Git Workflow

1. **New Features**:
   - Create a new branch: `feature/descriptive-name`
   - Keep commits small and focused on individual changes
   - Use meaningful commit messages in the format:
     ```
     Area: Brief summary (max 50 characters)
     
     - More detailed explanation of what changed
     - Why the change was necessary
     - References to related issues
     ```

2. **Bugfixes**:
   - Create a branch: `fix/bug-description`
   - Reproduce the error with a test if possible
   - Ensure the solution actually fixes the bug

3. **Pull Requests**:
   - Describe in detail what your changes aim to accomplish
   - Reference related issues with `#issue-number`
   - Respond promptly to feedback and review comments

### 🧪 Tests

- Write tests for all new functionality
- Ensure existing tests continue to pass
- Prefer automated tests over manual validations

## Code Standards

### 📝 Python Style Guidelines

- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) standard
- Use descriptive variable and function names
- Document functions with DocStrings in the following format:
  ```python
  def function_name(param1, param2):
      """
      Brief description of the function
      
      Args:
          param1: Description of the first parameter
          param2: Description of the second parameter
          
      Returns:
          Description of return values
          
      Raises:
          ExceptionType: When this exception is raised
      """
      # Function implementation
  ```

### 🏗️ Architecture Principles

1. **Modularity**:
   - Keep modules independent with clearly defined interfaces
   - Avoid circular dependencies between modules

2. **Configuration**:
   - Add new configuration options to `src/config.py`
   - Document all configuration options

3. **Error Handling**:
   - Implement robust error handling for external dependencies
   - Log errors with appropriate detail
   - Provide user-friendly error messages

## Documentation

- Update README.md for major changes
- Document new features or behavior changes
- Keep comments in code up to date

## Communication

- Use Issues for bug reports and feature requests
- Discuss larger changes first in an Issue or Pull Request
- Be respectful and constructive in all interactions

---

Thank you for your contribution to the project! Your collaboration makes this software better for all users. 