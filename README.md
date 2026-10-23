# Multi-Tool Autonomous AI Agent

A Python-based AI agent built with LangChain and Google's Gemini models. The agent uses web search, mathematical calculations, and local file reading to solve research questions and multi-step tasks.

## Overview

This project demonstrates how an AI agent can select and execute tools based on a user's request instead of relying solely on its language model.

The agent can combine multiple tools in a single workflow, inspect their outputs, handle tool errors, and generate a consolidated final answer.

## Features

- **Web Search:** Retrieve relevant web results using DuckDuckGo.
- **Python Calculator:** Evaluate mathematical expressions using a restricted Python AST evaluator without using `eval()`.
- **Local File Reader:** Read supported text, Markdown, and CSV files within the designated workspace.
- **Autonomous Tool Selection:** Select suitable tools based on the task.
- **Multi-Step Execution:** Combine multiple tools to complete compound requests.
- **Execution Trace:** Display tool calls, inputs, observations, and the final answer.
- **Error Handling:** Report tool errors while allowing the agent to continue with other steps when possible.
- **Automated Tests:** Test calculator operations, unsupported expressions, file reading, and workspace access restrictions.

## Tech Stack

- Python
- LangChain
- Google Gemini
- DuckDuckGo Search (`ddgs`)
- Pytest

## Project Structure

```text
Multi_Tool_Autonomous_AI_Agent/
├── multi-tool-autonomous-agent/
│   ├── agent.py
│   └── tools.py
├── tests/
│   └── test_tools.py
├── workspace/
│   └── project_notes.txt
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/engy-salem/Multi_Tool_Autonomous_AI_Agent.git
cd Multi_Tool_Autonomous_AI_Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create an API key through [Google AI Studio](https://aistudio.google.com/).

Set the key as an environment variable.

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

**macOS / Linux:**

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual key. Never hardcode your API key in source files or commit it to GitHub.

### 4. Run the agent

From the repository root, execute:

```bash
python multi-tool-autonomous-agent/agent.py
```

Enter your task when prompted.

## Example Task

```text
Read project_notes.txt and summarize its main purpose.
Calculate (125 * 8) + (2026 - 2024).
Search the web for the official Python downloads page.
Combine the results under clear headings.
```

For this task, the agent can use:

1. **File Reader** to retrieve information from `project_notes.txt`.
2. **Calculator** to evaluate the mathematical expression.
3. **Web Search** to retrieve relevant search results.

The agent then combines the tool outputs into a single response.

## Running Tests

Run the automated tests from the repository root:

```bash
python -m pytest tests/test_tools.py -v
```

The current test suite contains five tests covering:

- Calculator multiplication and subtraction.
- Rejection of unsupported calculator expressions.
- Reading the project notes file.
- Blocking file access outside the designated workspace.

All five tests passed in the latest test run. These tests validate the covered tool functions and file-access restrictions; they do not establish the accuracy of every web search result or test every possible agent workflow.

## Security Considerations

- The calculator uses a restricted AST evaluator to reject unsupported expressions.
- The file reader limits access to the designated workspace and supported file types.
- API credentials should be provided through environment variables or a secret manager.
- Web search results should be checked against reliable sources when accuracy is important.

## Future Improvements

- Expand automated tests for agent behavior and tool integration.
- Improve final-answer formatting and error handling.
- Add support for additional tools.
- Evaluate performance across a collection of multi-step research tasks.
