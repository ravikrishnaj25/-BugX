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


def print_banner():
    CYAN = "\033[96m"
    RESET = "\033[0m"

    print(CYAN + r"""
        --[[
    __________ ____ ___  ____________  ___
    \______   \    |   \/  _____/\   \/  /
    |    |  _/    |   /   \  ___ \     / 
    |    |   \    |  /\    \_\  \/     \ 
    |______  /______/  \______  /___/\  \
            \/                 \/      \_/
    --]]
    ========================================
              BUGX 🐞 Coding Agent
    ========================================
    """ + RESET)


def run_llm(prompt):
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    tools = types.Tool(
        function_declarations=[
            schema_meta_scanner,
            schema_code_emitter,
            schema_python_runner,
            schema_content_fetcher
        ]
    )

    response = llm.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_prompt
        )
    )

    if response.candidates:
        for candidate in response.candidates:
            if candidate and candidate.content:
                messages.append(candidate.content)

    if response.function_calls:
        for function_call_part in response.function_calls:
            result = call_function(os.getcwd(), function_call_part)
            print(result)
    else:
        print(response.text)


def bugx():

    print_banner()
    cwd = os.getcwd()

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

    while True:
        print("\n")
        print(CYAN + "╭──────────────────────────────────────────╮" + RESET)
        print(CYAN + "│                🐞 BUGX MENU              │" + RESET)
        print(CYAN + "├──────────────────────────────────────────┤" + RESET)
        print(f"│ 1. {GREEN}Ask BUGX a question (LLM mode){RESET}")
        print(f"│ 2. {YELLOW}Change working directory{RESET}")
        print(f"│ 3. {BLUE}Show current working directory{RESET}")
        print(f"│ 4. {RED}Exit BUGX (cry silently){RESET}")
        print(CYAN + "╰──────────────────────────────────────────╯" + RESET)

        choice = input(GREEN + "✨ Choose your destiny: " + RESET).strip()

        if choice == "1":
            print("\n" + CYAN + "💬 Chat mode activated. Spill your bugs..." + RESET)
            prompt = input(YELLOW + ">>> What can BUGX fix today? " + RESET)
            run_llm(prompt)

        elif choice == "2":
            print("\n" + CYAN + "📂 Directory teleportation initiated..." + RESET)
            new_dir = input(">>> Enter new directory path: ")

            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                print(GREEN + f"🟢 Teleported to: {new_dir}" + RESET)
            else:
                print(RED + "❌ Directory not found. It probably ran away." + RESET)

        elif choice == "3":
            print("\n" + GREEN + "🔍 Current Working Directory:" + RESET)
            print(BLUE + f"📂 {os.getcwd()}" + RESET)

        elif choice == "4":
            print("\n" + RED + "👋 Exiting BUGX... Deleting 0 bugs and 1000 hopes." + RESET)
            print(YELLOW + "✨ See ya, code warrior!" + RESET)
            break

        else:
            print(RED + "⚠️ Invalid choice. Even BUGX can't debug this input." + RESET)



bugx()
