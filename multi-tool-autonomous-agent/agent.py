
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from tools import web_search, calculate, read_local_file


console = Console()


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
    """Read a TXT, Markdown, or CSV file from the project workspace."""
    return read_local_file(filename)


tools = [
    web_search_tool,
    calculator_tool,
    file_reader_tool,
]


# --------------------------------------------------
# 2. Format model and tool output
# --------------------------------------------------

def format_content(content):
    """Convert model or tool output into readable text."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])

        return "\n".join(parts) if parts else str(content)

    return str(content)


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

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        You are a helpful autonomous research assistant.

        Available tools:
        - web_search_tool: Search the internet.
        - calculator_tool: Perform mathematical calculations.
        - file_reader_tool: Read files from the project workspace.

        Instructions:
        1. Choose tools appropriate to the user's request.
        2. Use tools instead of guessing when external information,
           calculations, or local file contents are needed.
        3. For multi-step tasks, use multiple tools when appropriate.
        4. Base your final answer on actual tool results.
        5. Use clear Markdown headings and bullet points.
        6. Include relevant source titles and exact URLs from search results.
        7. Never invent facts, URLs, or sources.
        8. Never claim a tool succeeded if it returned an error.
        9. Keep the final answer concise and readable.
        """
    )

    return agent


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

        # Display tool execution trace.
        console.print()
        console.print(
            Panel(
                "[bold]Tool calls and results[/bold]",
                border_style="cyan",
                expand=False,
            )
        )

        for message in response["messages"]:

            if getattr(message, "tool_calls", None):
                for call in message.tool_calls:
                    console.print(
                        f"\n[bold yellow]Action:[/bold yellow] {call['name']}"
                    )
                    console.print(
                        f"[bold]Input:[/bold] {call['args']}"
                    )

            elif getattr(message, "type", "") == "tool":
                console.print("[bold green]Observation:[/bold green]")
                console.print(format_content(message.content))

        # Display the final answer as rendered Markdown.
        final_content = format_content(
            response["messages"][-1].content
        )

        console.print()
        console.print(
            Panel(
                Markdown(final_content),
                title="[bold green]Final Answer[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Agent execution cancelled by user.[/yellow]")

    except Exception as error:
        console.print(
            f"\n[bold red]An error occurred:[/bold red] {error}"
        )
