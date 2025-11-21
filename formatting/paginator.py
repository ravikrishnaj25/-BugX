def paginate_text(text: str, max_lines: int = 200):
    """
    Split text into preview and remainder based on max_lines threshold.
    Returns (preview, remainder). Remainder is None if not needed.
    """
    if not isinstance(text, str):
        return "", None

    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text, None

    preview = "\n".join(lines[:max_lines])
    remainder = "\n".join(lines[max_lines:])
    return preview, remainder


