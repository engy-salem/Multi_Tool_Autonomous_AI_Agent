
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


console = Console()

URL_PATTERN = re.compile(r"https?://[^\s\]\)<>\"']+")


# --------------------------------------------------
# 1. Register the tools
# --------------------------------------------------

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


# --------------------------------------------------
# 2. Normalize content and extract real source URLs
# --------------------------------------------------

def format_content(content):
    """Convert model or tool output into readable text."""

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


def extract_urls(text):
    """Extract unique URLs from actual tool results."""

    urls = URL_PATTERN.findall(text)
    cleaned_urls = []

    for url in urls:
        url = url.rstrip(".,;:")

        if url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def add_sources(final_answer, source_urls):
    """Always append source URLs returned by web search."""

    if not source_urls:
        return (
            final_answer.rstrip()
            + "\n\n### Sources\n"
            + "No source URLs were returned by the search tool."
        )

    source_lines = ["### Sources", ""]

    for url in source_urls:
        source_lines.append(f"- {url}")

    return (
        final_answer.rstrip()
        + "\n\n"
        + "\n".join(source_lines)
    )


# --------------------------------------------------
# 3. Create the agent
# --------------------------------------------------

def create_research_agent():
    """Create and return the multi-tool AI agent."""

    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. Set it as an environment variable."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        max_retries=3,
    )

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        You are a helpful autonomous research assistant.

        Available tools:
        - web_search_tool: Search the internet.
        - calculator_tool: Perform safe mathematical calculations.
        - file_reader_tool: Read files from the project workspace.

        Instructions:
        1. Select tools appropriate to the user's request.
        2. Use tools for external information, calculations, and file contents.
        3. Use multiple tools for compound tasks when appropriate.
        4. Base answers on actual tool results.
        5. Format the answer with Markdown headings and bullet points.
        6. Include relevant source titles and exact URLs from web search.
        7. Never invent URLs, facts, or sources.
        8. Never claim a tool succeeded if it returned an error.
        9. Keep the answer clear, concise, and organized.
        """
    )


# --------------------------------------------------
# 4. Run the agent
# --------------------------------------------------

if __name__ == "__main__":
    try:
        agent = create_research_agent()

        question = console.input(
            "[bold cyan]Enter your question:[/bold cyan] "
        ).strip()

        if not question:
            console.print("[bold red]Please enter a question.[/bold red]")
            raise SystemExit(1)

        response = agent.invoke({
            "messages": [
                {"role": "user", "content": question}
            ]
        })

        messages = response["messages"]
        source_urls = []
        tool_observations = []

        # Collect tool calls and their actual results.
        console.print()
        console.print(
            Panel(
                "Tool calls and results",
                title="Execution Trace",
                border_style="cyan",
            )
        )

        for message in messages:

            if getattr(message, "tool_calls", None):
                for call in message.tool_calls:
                    console.print(
                        f"\n[bold yellow]Action:[/bold yellow] {call['name']}"
                    )
                    console.print(
                        Text(f"Input: {call['args']}")
                    )

            elif getattr(message, "type", "") == "tool":
                observation = format_content(message.content)
                tool_observations.append(observation)

                # Display observations as plain text to avoid
                # interpreting their content as Rich markup.
                console.print("\n[bold green]Observation:[/bold green]")
                console.print(Text(observation))

                # Extract URLs only from actual tool observations.
                source_urls.extend(extract_urls(observation))

        # Remove duplicate source URLs while preserving order.
        source_urls = list(dict.fromkeys(source_urls))

        # Format the model's final answer.
        final_answer = format_content(messages[-1].content)

        # Append real search-result URLs independently of the model.
        final_answer = add_sources(final_answer, source_urls)

        console.print()
        console.print(
            Panel(
                Markdown(final_answer),
                title="Final Answer",
                border_style="green",
                padding=(1, 2),
            )
        )

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Agent execution cancelled by user.[/yellow]"
        )

    except Exception as error:
        console.print(
            f"\n[bold red]An error occurred:[/bold red] {error}"
        )
