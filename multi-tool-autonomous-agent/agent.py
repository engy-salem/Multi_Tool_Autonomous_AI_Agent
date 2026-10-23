
import os
import re

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import web_search, calculate, read_local_file


# ==========================================
# 1. DEFINE THE TOOLS
# ==========================================

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


# ==========================================
# 2. FORMAT MESSAGE CONTENT
# ==========================================

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


# ==========================================
# 3. EXTRACT URLS
# ==========================================

def extract_urls(text):
    """Extract unique URLs from plain text and Markdown links."""

    # Extract URLs used as Markdown link destinations.
    markdown_urls = re.findall(
        r"\]\(\s*<?(https?://[^)\s>]+)>?\s*\)",
        text,
    )

    # Extract ordinary URLs, including URLs inside Markdown brackets.
    plain_urls = re.findall(
        r"https?://[^\s<>\"']+",
        text,
    )

    urls = []

    for url in markdown_urls + plain_urls:
        url = url.rstrip(".,;:!?")

        # Remove trailing Markdown delimiters.
        while url.endswith(")") and url.count("(") < url.count(")"):
            url = url[:-1]

        while url.endswith("]") and url.count("[") < url.count("]"):
            url = url[:-1]

        if url and url not in urls:
            urls.append(url)

    return urls


# ==========================================
# 4. CLEAN THE FINAL ANSWER
# ==========================================

def clean_final_answer(text):
    """Convert Markdown links into plain URLs and remove malformed wrapping."""

    # Convert normal Markdown links:
    # [Python Downloads](https://www.python.org/downloads/)
    # into:
    # https://www.python.org/downloads/
    text = re.sub(
        r"\[([^\]]*)\]\(\s*(https?://[^)\s]+)\s*\)",
        r"\2",
        text,
    )

    # Remove escaped Markdown asterisks.
    text = text.replace(r"\*", "*")

    # Remove square brackets wrapping a URL.
    text = re.sub(
        r"\[(https?://[^\]\s]+)\]",
        r"\1",
        text,
    )

    # Remove leftover escaped brackets.
    text = text.replace(r"\[", "[")
    text = text.replace(r"\]", "]")
    text = text.replace(r"\(", "(")
    text = text.replace(r"\)", ")")

    return text.strip()


# ==========================================
# 5. CREATE THE RESEARCH AGENT
# ==========================================

def create_research_agent():
    """Initialize the language model and autonomous agent."""

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
- web_search_tool: Search the internet.
- calculator_tool: Perform safe mathematical calculations.
- file_reader_tool: Read files from the project workspace.

Instructions:
1. Select tools appropriate to the user's request.
2. Use tools for external information, calculations, and file contents.
3. Use multiple tools for compound tasks when appropriate.
4. Base answers on actual tool results.
5. Organize answers with clear headings and bullet points.
6. Use the exact URLs returned by the web search tool.
7. Never invent facts, calculations, or sources.
8. Explain clearly when a tool returns an error.
9. Keep answers concise and organized.
10. When providing a URL, write the URL as plain text.
11. Do not wrap URLs inside Markdown link syntax.
12. Do not place extra brackets or parentheses around URLs.
13. Clearly distinguish verified information from information
    that has not been verified.
""",
    )

    return agent


# ==========================================
# 6. COLLECT SOURCES
# ==========================================

def collect_source_urls(messages):
    """Collect unique URLs from tool results and the final answer."""

    source_urls = []

    for message in messages:

        # Collect URLs from tool observations.
        if getattr(message, "type", "") == "tool":
            observation = format_content(message.content)

            for url in extract_urls(observation):
                if url not in source_urls:
                    source_urls.append(url)

    # Also collect URLs from the final answer.
    if messages:
        final_answer = format_content(messages[-1].content)

        for url in extract_urls(final_answer):
            if url not in source_urls:
                source_urls.append(url)

    return source_urls


# ==========================================
# 7. DISPLAY SOURCES
# ==========================================

def display_sources(source_urls):
    """Display source URLs separately as plain text."""

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)

    if not source_urls:
        print("No URLs were extracted from the agent messages.")
        return

    for index, url in enumerate(source_urls, start=1):
        print(f"{index}. {url}")


# ==========================================
# 8. RUN THE AGENT
# ==========================================

if __name__ == "__main__":

    try:
        agent = create_research_agent()

        print("=" * 60)
        print("MULTI-TOOL AUTONOMOUS AI AGENT")
        print("=" * 60)

        question = input("\nEnter your question: ").strip()

        if not question:
            print("Please enter a question.")
            raise SystemExit(1)

        # Run the agent.
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
        observations = []

        # ----------------------------------
        # Display the execution trace.
        # ----------------------------------

        print("\n" + "=" * 60)
        print("EXECUTION TRACE")
        print("=" * 60)

        for message in messages:

            # Display the tools selected by the agent.
            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:
                for call in tool_calls:
                    print(f"\nAction: {call.get('name', 'Unknown tool')}")
                    print(f"Input: {call.get('args', {})}")

            # Display the returned results.
            if getattr(message, "type", "") == "tool":
                observation = format_content(message.content)
                observations.append(observation)

                print("\nObservation:")
                print(observation)

        # ----------------------------------
        # Prepare the final answer.
        # ----------------------------------

        final_answer = format_content(messages[-1].content)

        # Extract sources before cleaning the answer.
        source_urls = collect_source_urls(messages)

        # Clean malformed Markdown links in the answer.
        final_answer = clean_final_answer(final_answer)

        # ----------------------------------
        # Display the final answer.
        # ----------------------------------

        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        print(final_answer or "The agent returned an empty answer.")

        # ----------------------------------
        # Display sources separately.
        # ----------------------------------

        display_sources(source_urls)

        # ----------------------------------
        # Debug information if no sources exist.
        # ----------------------------------

        if not source_urls:
            print("\nDEBUG: No URLs were found.")

            if observations:
                for index, observation in enumerate(
                    observations,
                    start=1,
                ):
                    print(f"\nTool result {index}:")
                    print(observation[:2000])
            else:
                print("No tool observations were returned.")

    except KeyboardInterrupt:
        print("\nAgent execution cancelled.")

    except Exception as error:
        print(f"\nAn error occurred: {error}")
