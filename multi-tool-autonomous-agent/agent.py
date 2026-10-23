
import os
import re

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from tools import web_search, calculate, read_local_file


# Initialize the console
console = Console()

# Match URLs in tool results
URL_PATTERN = re.compile(r"https?://[^\s\]\)<>\"']+")


# -----------------------------
# 1. Define the agent tools
# -----------------------------

@tool
def web_search_tool(query: str) -> str:
    """Search the internet for information about a topic."""
    return web_search(query, max_results=5)


@tool
def calculator_tool(expression: str) -> str:
    """Safely calculate a mathematical expression."""
    return calculate(expression)


@tool
def file_reader_tool(filename: str) -> str:
    """Read a TXT, Markdown, or CSV file from the workspace."""
    return read_local_file(filename)


tools = [
    web_search_tool,
    calculator_tool,
    file_reader_tool,
]


# -----------------------------
# 2. Format the content
# -----------------------------

def format_content(content):
    """Convert the agent response into readable text."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])

        return "\n".join(parts).strip()

    return str(content).strip()


# -----------------------------
# 3. Extract source URLs
# -----------------------------

def extract_urls(text):
    """Extract unique URLs from text."""

    urls = URL_PATTERN.findall(text)
    cleaned_urls = []

    for url in urls:
        url = url.rstrip(".,;:")

        if url and url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def collect_source_urls(messages):
    """Collect URLs from tool results and the final answer."""

    source_urls = []

    for message in messages:
        # Collect URLs from tool observations
        if getattr(message, "type", "") == "tool":
            observation = format_content(message.content)
            source_urls.extend(extract_urls(observation))

    # Also check the final answer for any URLs
    if messages:
        final_answer = format_content(messages[-1].content)
        source_urls.extend(extract_urls(final_answer))

    # Remove duplicates while preserving order
    return list(dict.fromkeys(source_urls))


# -----------------------------
# 4. Create the research agent
# -----------------------------

def create_research_agent():
    """Initialize the Gemini model and autonomous agent."""

    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. "
            "Set it as an environment variable."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        max_retries=3,
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
You are a helpful autonomous research assistant.

Available tools:
- web_search_tool: Search the internet for information.
- calculator_tool: Perform safe mathematical calculations.
- file_reader_tool: Read files from the project workspace.

Instructions:
1. Select the appropriate tools for the user's request.
2. Use tools for external information, calculations, and file contents.
3. Use multiple tools for compound tasks when appropriate.
4. Base your answers on actual tool results.
5. Organize answers using Markdown headings and bullet points.
6. Include relevant source titles and exact URLs from search results.
7. Never invent URLs, facts, calculations, or sources.
8. Never claim a tool succeeded if it returned an error.
9. If a tool returns an error, explain the problem clearly.
10. Keep answers clear, concise, and organized.
""",
    )

    return agent


# -----------------------------
# 5. Display source URLs
# -----------------------------

def display_sources(source_urls):
    """Display source URLs separately as clickable terminal links."""

    console.print()
    console.print(
        Panel(
            "Links extracted from the tool results",
            title="Sources",
            border_style="cyan",
        )
    )

    if not source_urls:
        console.print(
            "[yellow]No source URLs were found in the results.[/yellow]"
        )
        return

    for index, url in enumerate(source_urls, start=1):
        # Use Text instead of parsing the URL as Rich markup
        link_text = Text(f"{index}. {url}")
        link_text.stylize(f"link {url}", len(f"{index}. "), len(f"{index}. {url}"))
        console.print(link_text)


# -----------------------------
# 6. Run the agent
# -----------------------------

if __name__ == "__main__":
    try:
        agent = create_research_agent()

        console.print(
            Panel(
                "Ask a question that may require research, "
                "calculations, or reading a local file.",
                title="Multi-Tool Autonomous AI Agent",
                border_style="cyan",
            )
        )

        question = console.input(
            "\n[bold cyan]Enter your question:[/bold cyan] "
        ).strip()

        if not question:
            console.print(
                "[bold red]Please enter a question.[/bold red]"
            )
            raise SystemExit(1)

        # Invoke the agent
        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )

        messages = response["messages"]

        # Display the execution trace
        console.print()

        console.print(
            Panel(
                "Tools selected and their returned results",
                title="Execution Trace",
                border_style="cyan",
            )
        )

        for message in messages:

            # Display tool calls and their inputs
            if getattr(message, "tool_calls", None):
                for call in message.tool_calls:
                    console.print(
                        f"\n[bold yellow]Action:[/bold yellow] "
                        f"{call['name']}"
                    )

                    console.print(
                        Text(
                            f"Input: {call.get('args', {})}"
                        )
                    )

            # Display tool results
            elif getattr(message, "type", "") == "tool":
                observation = format_content(message.content)

                console.print(
                    "\n[bold green]Observation:[/bold green]"
                )

                console.print(Text(observation))

        # Get the final answer
        final_answer = format_content(messages[-1].content)

        # Collect URLs independently of the model's final wording
        source_urls = collect_source_urls(messages)

        # Display the final answer
        console.print()

        console.print(
            Panel(
                Markdown(final_answer or "The agent returned an empty answer."),
                title="Final Answer",
                border_style="green",
                padding=(1, 2),
            )
        )

        # Always display the collected URLs separately
        display_sources(source_urls)

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Agent execution cancelled by user.[/yellow]"
        )

    except Exception as error:
        console.print(
            f"\n[bold red]An error occurred:[/bold red] {error}"
        )
