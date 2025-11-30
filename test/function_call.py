from function_tools.MetaScanner import Meta_Scanner
from function_tools.CodeEmitter import Code_Emitter
from function_tools.PythonRunner import run_python_file
from function_tools.ContentFetcher import Content_Fetcher
from formatting.ansi_highlighter import highlight_code
from formatting.paginator import paginate_text
from google.genai import types


def detect_missing_imports(code: str):
    missing = []
    if "os." in code and "import os" not in code:
        missing.append("import os")
    if "sys." in code and "import sys" not in code:
        missing.append("import sys")
    if "re." in code and "import re" not in code:
        missing.append("import re")
    return missing


def call_function(working_directory, function_call_part):
    name = function_call_part.name
    args = function_call_part.args

    if name == "Meta_Scanner":
        result = Meta_Scanner(working_directory=working_directory, **args)

    elif name == "Content_Fetcher":
        raw_result = Content_Fetcher(working_directory=working_directory, **args)

        if isinstance(raw_result, dict):
            content = raw_result.get("result", "")
        else:
            content = str(raw_result)

        highlighted = highlight_code(content)
        preview, remainder = paginate_text(highlighted)
        response_text = preview or ""

        if remainder:
            response_text += (
                "\n\n\033[93m[File too long — type 'continue' to load more]\033[0m"
            )

        missing = detect_missing_imports(content)
        if missing:
            response_text += "\n\n\033[91m[Possible Missing Imports]\033[0m\n"
            response_text += "\n".join(f"  - {item}" for item in missing)

        result = {"result": response_text}

    elif name == "Code_Emitter":
        result = Code_Emitter(working_directory=working_directory, **args)

    elif name == "run_python_file":
        result = run_python_file(working_directory=working_directory, **args)

    else:
        result = f"Error: Unknown function '{name}'"

    if isinstance(result, types.Content):
        # Already a Content object—return as-is
        return result

    if isinstance(result, dict):
        response_payload = result
    else:
        response_payload = {"result": result}

    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(
            name=name,
            response=response_payload
        )]
    )

