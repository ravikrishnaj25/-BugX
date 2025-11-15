
from config import llm, get_prompt_tokens, get_response_tokens
import sys

# sys.argv - variable in a list of strings representing all the command line arguments passed to the string
# sys.argv[0] = file name(goblin.py)


def bugx():
    
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

    prompt = sys.argv[1]

    response = llm.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents= prompt
    )

    print(response.text)
    print(get_prompt_tokens(response))
    print(get_response_tokens(response))

bugx()