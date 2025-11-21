import os
import subprocess

def run_python_file(working_directory: str, file_path: str):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    # Validate location
    if not abs_file_path.startswith(abs_working_dir):
        return f"Error: '{file_path}' is not in the working directory"

    # Validate file exists
    if not os.path.isfile(abs_file_path):
        return f"Error: '{file_path}' is not a file"

    # Validate Python file
    if not file_path.endswith(".py"):
        return f"Error: '{file_path}' is not a Python file."

    try:
        output = subprocess.run(
            ["python3", abs_file_path],
            cwd=abs_working_dir,
            timeout=30,
            capture_output=True,
            text=True
        )

        # Create formatted output string
        final_string = f"""
            STDOUT:
            {output.stdout}
            STDERR:
            {output.stderr}
            """

        # Handle no output
        if output.stdout == "" and output.stderr == "":
            final_string = "No output produced.\n"

        # Append return code if non-zero
        if output.returncode != 0:
            final_string += f"Process exited with code {output.returncode}\n"

        return final_string

    except Exception as e:
        return f"Error: executing Python file: {e}"
