import re


def highlight_code(code: str) -> str:
    """
    Apply simple ANSI-based syntax highlighting to code strings.
    """
    if not isinstance(code, str):
        return ""

    KEY = "\033[95m"
    FUN = "\033[94m"
    STR = "\033[92m"
    COM = "\033[90m"
    RES = "\033[0m"

    highlighted = code

    # Strings
    highlighted = re.sub(
        r'(\".*?\"|\'.*?\')',
        lambda m: f"{STR}{m.group(0)}{RES}",
        highlighted,
        flags=re.DOTALL,
    )

    # Comments
    highlighted = re.sub(
        r"#.*",
        lambda m: f"{COM}{m.group(0)}{RES}",
        highlighted,
    )

    # Functions
    highlighted = re.sub(
        r"\bdef (\w+)",
        lambda m: f"def {FUN}{m.group(1)}{RES}",
        highlighted,
    )

    # Classes
    highlighted = re.sub(
        r"\bclass (\w+)",
        lambda m: f"class {KEY}{m.group(1)}{RES}",
        highlighted,
    )

    return highlighted


