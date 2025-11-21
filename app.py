
from config import llm, get_prompt_tokens, get_response_tokens
import sys
from google.genai import types
import function_call
from prompts import system_prompt
from function_tools.MetaScanner import schema_meta_scanner
from function_tools.CodeEmitter import schema_code_emitter
from function_tools.PythonRunner import schema_python_runner
from function_tools.ContentFetcher import schema_content_fetcher
from function_call import call_function
import os

# sys.argv - variable in a list of strings representing all the command line arguments passed to the string
# sys.argv[0] = file name(goblin.py)


def bugx():

    #working_dir = "E:\-BugX"
    
    verbose_flag = False   


    # when no user_prompt
    if len(sys.argv) < 2:
        RED = "\033[91m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

        print(CYAN + "====================================================" + RESET)
        print()
        print(RED + "You had ONE job: pass an argument. Try again 🫠" + RESET)
        print()
        print(CYAN + "====================================================" + RESET)


        sys.exit(1)
        return

    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True


    prompt = sys.argv[1]

    # managing conversation History
    messages = [
        types.Content(role="user", parts = [types.Part(text=prompt)]),
        ] # used to store the previous user messages in the history

    tools = types.Tool(
    function_declarations=[
        schema_meta_scanner,schema_code_emitter,schema_python_runner,schema_content_fetcher
    ]
    )

    response = llm.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents= messages,
        config=types.GenerateContentConfig(
                        tools=[tools], system_instruction=system_prompt)
    )
    

    #print(response.text)

    if response is None or response.usage_metadata is None:
        print(CYAN + "====================================================" + RESET)
        print()
        print(RED + "LLM ghosted you. Message left on seen 👻" + RESET)
        print()
        print(CYAN + "====================================================" + RESET)

       
        return 

    if verbose_flag:
        print(get_prompt_tokens(response))
        print(get_response_tokens(response))

    if response.function_calls:
        print(response.function_calls)
        for function_call_part in response.function_calls:
            result = call_function(os.getcwd(), function_call_part)
            print(result)
    else:
        # No function calls — print normal text response
        print(response.text)

bugx()