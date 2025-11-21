from function_tools.MetaScanner import Meta_Scanner
from function_tools.CodeEmitter import Code_Emitter
from function_tools.PythonRunner import run_python_file
from function_tools.ContentFetcher import Content_Fetcher
from google.genai import types



def call_function(working_directory, function_call_part):
    name = function_call_part.name
    args = function_call_part.args

    if name == "Meta_Scanner":
        result = Meta_Scanner(working_directory=working_directory, **args)

    elif name == "Content_Fetcher":
        result = Content_Fetcher(working_directory=working_directory, **args)

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

