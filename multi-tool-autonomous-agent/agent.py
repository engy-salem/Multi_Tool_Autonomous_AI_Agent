
import os

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import web_search, calculate, read_local_file


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
# 3. Create the language model and agent
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
        1. Select the appropriate tool based on the user's request.
        2. Use tools instead of guessing when external information,
           calculations, or local file contents are needed.
        3. For multi-step tasks, use multiple tools when appropriate.
        4. Base your final answer on the actual tool results.
        5. Present a clear, concise final answer using Markdown.
        6. Use headings, bullet points, and numbered lists when useful.
        7. When using web search results, include relevant source titles
           and their exact URLs in the final answer.
        8. Distinguish retrieved information from assumptions.
        9. Never claim a tool succeeded if it returned an error.
        10. Never invent URLs, facts, or sources.
        11. Avoid unnecessary repetition and keep the answer readable.
        """
    )

    return agent


# --------------------------------------------------
# 4. Run the agent
# --------------------------------------------------

if __name__ == "__main__":
    try:
        agent = create_research_agent()

        question = input("Enter your question: ").strip()

        if not question:
            print("Please enter a question.")
            raise SystemExit(1)

        response = agent.invoke({
            "messages": [
                {"role": "user", "content": question}
            ]
        })

        # Display tool execution trace.
        print("\n" + "=" * 60)
        print("TOOL EXECUTION TRACE")
        print("=" * 60)

        for message in response["messages"]:

            if getattr(message, "tool_calls", None):
                for call in message.tool_calls:
                    print(f"\nAction: {call['name']}")
                    print(f"Input: {call['args']}")

            elif getattr(message, "type", "") == "tool":
                print("\nObservation:")
                print(format_content(message.content))

        # Display final answer.
        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        final_content = response["messages"][-1].content
        print(format_content(final_content))

        print("\n" + "=" * 60)

    except KeyboardInterrupt:
        print("\nAgent execution cancelled by user.")

    except Exception as error:
        print(f"\nAn error occurred: {error}")
