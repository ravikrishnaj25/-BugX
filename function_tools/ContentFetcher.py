import os

MAX_CHARS = 10000   # Limit the number of characters returned from the file

def Content_Fetcher(working_directory, file_path):
    # Convert paths to absolute paths
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    # --- SAFETY CHECK 1 ---
    # Make sure the file is inside the working directory
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: "{file_path}" is not in the working directory'

    # --- SAFETY CHECK 2 ---
    # Check if the path is actually a file
    if not os.path.isfile(abs_file_path):
        return f'Error: "{file_path}" is not a file'

    # Read the file
    file_content_string = ""
    with open(abs_file_path, "r") as f:
        file_content_string = f.read(MAX_CHARS)

        # If file exceeds MAX_CHARS → add truncation note
        if len(file_content_string) >= MAX_CHARS:
            file_content_string += (
                f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            )

    return file_content_string


#print(Content_Fetcher(r"E:\-BugX", r"app.py"))
