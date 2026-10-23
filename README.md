# Multi-Tool Autonomous AI Agent

A Python-based autonomous AI agent built with LangChain and Google's Gemini models. The agent uses web search, mathematical calculations, and local file reading to solve research questions and multi-step tasks.

## Overview

This project demonstrates how an AI agent can select and execute tools based on a user's request rather than relying solely on its language model.

The agent can combine multiple tools in a single workflow, observe their results, and generate a consolidated final answer.

## Features

- **Web Search:** Retrieve relevant web results using DuckDuckGo.
- **Python Calculator:** Evaluate mathematical expressions using a restricted Python AST evaluator without using `eval()`.
- **Local File Reader:** Read supported text, Markdown, and CSV files within the designated workspace.
- **Autonomous Tool Selection:** Choose suitable tools according to the user's request.
- **Multi-Step Execution:** Combine multiple tools to complete compound tasks.
- **Execution Trace:** Display tool actions, inputs, observations, and the final answer.
- **Automated Tests:** Validate calculator behavior, error handling, file reading, and workspace access restrictions.

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

Activate it before installing dependencies.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create an API key through [Google AI Studio](https://aistudio.google.com/).

Set the key as an environment variable. Never hardcode your real API key in source code or commit it to GitHub.

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

**macOS / Linux:**

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual key locally. Do not include the real key in this README.

### 4. Run the agent

From the repository root, run:

```bash
python multi-tool-autonomous-agent/agent.py
```

Enter a research question when prompted.

## Example Task

```text
Read project_notes.txt, calculate 2026 - 2024,
and search the web for the official Python website.
Summarize the results from all three tools.
```

For this request, the agent can:

1. Read the project notes using the file reader.
2. Calculate the difference using the calculator.
3. Search for the official Python website.
4. Combine the observations into a final response.

## Running Tests

Run the automated tests from the repository root:

```bash
python -m pytest tests/test_tools.py -v
```

The current test suite covers:

- Calculator multiplication and subtraction.
- Rejection of unsupported calculator expressions.
- Reading the project notes.
- Blocking attempts to access files outside the workspace.

## Security Considerations

- The calculator uses a restricted AST evaluator instead of executing arbitrary Python expressions.
- The file reader restricts supported file types and prevents path traversal outside the workspace.
- API credentials should be stored in environment variables or a secret manager.
- Web search results may be incomplete or inaccurate and should be verified when necessary.

## Future Improvements

- Expand automated tests for agent behavior and tool integration.
- Improve final-answer formatting and error handling.
- Add more tools and research capabilities.
- Evaluate the agent on a broader collection of multi-step tasks.
