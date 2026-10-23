
import os
import re

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import web_search, calculate, read_local_file


# --------------------------------
# 1. Define the tools
# --------------------------------

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


# --------------------------------
# 2. Format message content
# --------------------------------

def format_content(content):
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


# --------------------------------
# 3. Extract URLs from text
# --------------------------------

def extract_urls(text):
    # Find URLs in plain text and Markdown links
    pattern = r"https?://[^\s<>\"']+"
    matches = re.findall(pattern, text)

    urls = []

    for url in matches:
        # Remove Markdown and sentence punctuation from the end
        url = url.rstrip(".,;:!?)]}")

        if url and url not in urls:
            urls.append(url)

    return urls


# --------------------------------
# 4. Create the agent
# --------------------------------

def create_research_agent():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. "
            "Set it as an environment variable."
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
- calculator_tool: Perform safe calculations.
- file_reader_tool: Read files from the workspace.

Instructions:
1. Choose tools appropriate for the user's request.
2. Use tools for external information, calculations, and files.
3. Use multiple tools for compound tasks when appropriate.
4. Base answers on actual tool results.
5. Use clear Markdown headings and bullet points.
6. Include relevant URLs returned by the web search tool.
7. Never invent facts, URLs, or sources.
8. Explain clearly when a tool returns an error.
9. Keep answers organized and concise.
""",
    )


# --------------------------------
# 5. Run the agent
# --------------------------------

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

        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        })

        messages = response["messages"]
        all_observations = []
        source_urls = []

        # Show tool calls and collect their results
        print("\n" + "=" * 60)
        print("EXECUTION TRACE")
        print("=" * 60)

        for message in messages:

            # Display each tool call
            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:
                for call in tool_calls:
                    print(f"\nAction: {call.get('name', 'Unknown tool')}")
                    print(f"Input: {call.get('args', {})}")

            # Display tool output and extract URLs
            if getattr(message, "type", "") == "tool":
                observation = format_content(message.content)
                all_observations.append(observation)

                print("\nObservation:")
                print(observation)

                found_urls = extract_urls(observation)

                for url in found_urls:
                    if url not in source_urls:
                        source_urls.append(url)

        # Get the final answer
        final_answer = format_content(messages[-1].content)

        # Search the final answer for additional URLs
        for url in extract_urls(final_answer):
            if url not in source_urls:
                source_urls.append(url)

        # Display the answer
        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)
        print(final_answer)

        # Display the collected source URLs separately
        print("\n" + "=" * 60)
        print("SOURCES")
        print("=" * 60)

        if source_urls:
            for index, url in enumerate(source_urls, start=1):
                print(f"{index}. {url}")
        else:
            print("No URLs were extracted from the agent messages.")

            # Diagnostic output to help identify the issue
            print("\nDEBUG: Checking the tool observations...")

            if all_observations:
                for index, observation in enumerate(
                    all_observations, start=1
                ):
                    print(f"\nTool result {index}:")
                    print(observation[:2000])
            else:
                print("No tool observations were returned.")

    except KeyboardInterrupt:
        print("\nAgent execution cancelled.")

    except Exception as error:
        print(f"\nAn error occurred: {error}")
