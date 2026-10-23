
import ast
import math
import operator
from pathlib import Path

from ddgs import DDGS


# Project workspace: files the agent is allowed to read
WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 1. Web Search Tool
# --------------------------------------------------
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return titles, URLs, and snippets."""
    try:
        results = list(DDGS().text(query, max_results=max_results))

        if not results:
            return "No search results were found."

        formatted_results = []

        for i, result in enumerate(results, start=1):
            formatted_results.append(
                f"Result {i}\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"URL: {result.get('href', 'N/A')}\n"
                f"Snippet: {result.get('body', 'N/A')}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Web search failed: {type(e).__name__}: {e}"


# --------------------------------------------------
# 2. Safe Calculator Tool
# --------------------------------------------------
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent is too large.")

        result = _ALLOWED_OPERATORS[type(node.op)](left, right)

    elif isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        result = _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.operand)
        )

    else:
        raise ValueError("Unsupported mathematical expression.")

    if isinstance(result, (int, float)):
        if not math.isfinite(result) or abs(result) > 1e100:
            raise ValueError("Result is outside the allowed range.")

    return result


def calculate(expression: str) -> str:
    """Safely calculate a mathematical expression without eval()."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return f"{expression} = {result}"

    except Exception as e:
        return f"Calculation failed: {e}"


# --------------------------------------------------
# 3. Local File Reader Tool
# --------------------------------------------------
def read_local_file(filename: str) -> str:
    """Read a TXT, Markdown, or CSV file from the workspace only."""
    allowed_extensions = {".txt", ".md", ".csv"}

    try:
        requested_path = (WORKSPACE / filename).resolve()

        # Prevent access to files outside the workspace.
        requested_path.relative_to(WORKSPACE.resolve())

        if requested_path.suffix.lower() not in allowed_extensions:
            return "Error: This file type is not allowed."

        if not requested_path.is_file():
            return "Error: File not found."

        max_bytes = 100_000

        with requested_path.open("rb") as file:
            content = file.read(max_bytes + 1)

        if len(content) > max_bytes:
            return "Error: File exceeds the 100 KB limit."

        return content.decode("utf-8-sig")

    except ValueError:
        return "Error: Access outside the workspace is not allowed."

    except UnicodeDecodeError:
        return "Error: File must contain valid UTF-8 text."

    except OSError as e:
        return f"File reading failed: {e}"

