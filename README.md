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

### 2. Install dependencies

```bash
python -m venv .venv
```

Activate the environment, then install the required packages.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create an API key through [Google AI Studio](https://aistudio.google.com/).

Set it as an environment variable instead of hardcoding it in the source code.

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

**macOS / Linux:**

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Never commit your real API key to GitHub.

### 4. Run the agent

From the repository root:

```bash
python multi-tool-autonomous-agent/agent.py
```

Enter a question when prompted.

## Example Task

```text
Read project_notes.txt, calculate 2026 - 2024,
and search the web for the official Python website.
Summarize the results from all three tools.
```

The agent can use the file reader, calculator, and web search tools to complete the request.

## Running Tests

Run the automated tests from the repository root:

```bash
python -m pytest tests/test_tools.py -v
```

The current test suite includes five tests covering calculator operations, rejection of unsupported expressions, local file reading, and workspace access restrictions.

## Security Considerations

- The calculator restricts the types of Python expressions it evaluates.
- The file reader limits access to the designated workspace and supported file types.
- API credentials should be supplied through environment variables or a secret manager.
- Web search results should be verified when accuracy is important.

## Future Improvements

- Expand automated tests for agent behavior and tool integration.
- Improve final-answer formatting and error handling.
- Add support for additional tools.
- Evaluate performance on a collection of multi-step research tasks.
