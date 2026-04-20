"""Server-Sent Events formatting utilities."""
from __future__ import annotations


def format_sse(data: str, event: str | None = None) -> str:
    """
    Format a string as an SSE message.

    Args:
        data: JSON string payload.
        event: Optional event type name.

    Returns:
        Formatted SSE string ready to yield from a Flask generator.
    """
    lines = []
    if event:
        lines.append(f"event: {event}")
    lines.append(f"data: {data}")
    lines.append("")   # blank line = end of message
    lines.append("")
    return "\n".join(lines)
