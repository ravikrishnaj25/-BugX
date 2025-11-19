
from config import llm, get_prompt_tokens, get_response_tokens
import sys
from google.genai import types

# sys.argv - variable in a list of strings representing all the command line arguments passed to the string
# sys.argv[0] = file name(goblin.py)


def bugx():
    
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

    if len(sys.argv) == 3 and sys.arg[2] == "--verbose":
        verbose_flag = True


    prompt = sys.argv[1]

    # managing conversation History
    messages = [
        types.Content(role="user", parts = [types.Part(text=prompt)]),
        ] # used to store the previous user messages in the history


    response = llm.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents= messages
    )

    print(response.text)

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

bugx()