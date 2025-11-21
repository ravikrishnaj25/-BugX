import os
from google.genai import types


def Meta_Scanner(working_directory, directory=None):
    # Convert working directory to absolute
    abs_working_dir = os.path.abspath(working_directory)

    # If no directory given, inspect working_directory itself
    if directory is None:
        abs_directory = abs_working_dir
    else:
        abs_directory = os.path.abspath(directory)

    # Validate directory
    if not os.path.isdir(abs_directory):
        return f"Error: '{abs_directory}' is not a valid directory"

    final_response = ""

    try:
        contents = os.listdir(abs_directory)
    except Exception as e:
        return f"Error reading directory: {e}"

    for content in contents:
        content_path = os.path.join(abs_directory, content)
        is_dir = os.path.isdir(content_path)

        try:
            size = os.path.getsize(content_path)
        except:
            size = 0

        final_response += (
            f"{content} → size: {size} bytes, is_dir: {is_dir}\n"
        )

    return final_response

#print(Meta_Scanner("E:\-BugX"))

schema_meta_scanner = types.FunctionDeclaration(
    name="Meta_Scanner",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

"""

Example
.env → size: 54 bytes, is_dir: False
.git → size: 4096 bytes, is_dir: True
.gitignore → size: 11 bytes, is_dir: False
app.py → size: 955 bytes, is_dir: False
config.py → size: 466 bytes, is_dir: False
LICENSE → size: 1070 bytes, is_dir: False
requirements.txt → size: 43 bytes, is_dir: False
tools → size: 0 bytes, is_dir: True
venv → size: 0 bytes, is_dir: True
__pycache__ → size: 0 bytes, is_dir: True
"""