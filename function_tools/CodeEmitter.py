import os
from google.genai import types


def Code_Emitter(working_directory, file_path, content):
    # Convert to absolute paths
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    # --- SAFETY CHECK 1: Prevent directory escape ---
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: "{file_path}" is not in the working directory'

    # --- Ensure parent directories exist ---
    parent_dir = os.path.dirname(abs_file_path)
    if not os.path.isdir(parent_dir):
        try:
            os.makedirs(parent_dir)
        except Exception as e:
            return f'Could not create parent dirs: "{parent_dir}" → {e}'

    # --- Write the file ---
    try:
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" '
            f'({len(content)} characters)'
        )
    except Exception as e:
        return f'Failed to write to file "{file_path}": {e}'

#print(Code_Emitter(r"E:\-BugX", r"test.txt","Hello I am Ravikrishna"))


schema_code_emitter = types.FunctionDeclaration(
    name="Code_Emitter",
    description="Writes a file inside the working directory safely.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path of the file to write inside the working directory."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Text content to write into the file."
            ),
        },
        required=["file_path", "content"]
    ),
)
