# Multi-Tool Autonomous AI Agent

A Python-based AI agent that uses multiple tools to solve research questions and multi-step tasks. Built with LangChain and Google's Gemini models.

## Overview

This project demonstrates how an AI agent can select and use different tools based on a user's request instead of relying only on its language model.

The agent can combine web search, mathematical calculations, and local file reading to answer compound questions.

## Features

- **Web Search:** Search the web for relevant information using DuckDuckGo.
- **Python Calculator:** Evaluate mathematical expressions using a restricted Python AST evaluator.
- **Local File Reader:** Read supported text, Markdown, and CSV files from the project workspace.
- **Autonomous Tool Selection:** Select appropriate tools based on the task.
- **Multi-Step Task Execution:** Use multiple tools to complete compound requests.
- **Execution Trace:** Display tool actions, inputs, observations, and the final answer.

## Tech Stack

- Python
- LangChain
- Google Gemini
- DuckDuckGo Search (`ddgs`)
- Pytest

## Project Structure

```text
multi-tool-autonomous-agent/
├── agent.py
├── tools.py
├── requirements.txt
├── .gitignore
├── README.md
└── workspace/
    └── project_notes.txt
```

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd multi-tool-autonomous-agent
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Install dependencies

```bash
python -m venv .venv
```

Activate the environment, then install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a Gemini API key through Google AI Studio.

Set it as an environment variable instead of hardcoding it in the source code.

On Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

On macOS or Linux:

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Never commit your real API key to GitHub.

### 4. Run the agent

```bash
python agent.py
```

Enter a question when prompted.

## Example Task

```text
Read project_notes.txt, calculate 2026 - 2024,
and search the web for the official Python website.
Then summarize the results.
```

The agent can use the file reader, calculator, and web search tools to complete the request.

## Security Considerations

- The calculator restricts the types of Python expressions it evaluates.
- The file reader is designed to limit access to the project workspace and supported file types.
- API credentials should be supplied through environment variables or a secret manager.
- Web search results should be verified when accuracy is important.

## Future Improvements

- Add automated tests for each tool.
- Improve error handling and tool execution logging.
- Add support for additional tools.
- Evaluate performance on a collection of multi-step research tasks.
