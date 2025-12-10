import os
from typing import Any, Dict
from google.api_core.exceptions import ResourceExhausted

# LangChain 1.0+ Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent  # <--- New Standard API
from langchain_core.messages import HumanMessage

# API Key
from config import google_api, rotate_api_key, get_api_key, get_all_api_keys
GOOGLE_API_KEY = google_api

# === IMPORT YOUR TOOLS HERE ======================================
# (Keep your existing tool imports exactly as they were)
from function_tools.CodeEmitter import Code_Emitter
from function_tools.ContentFetcher import Content_Fetcher
from function_tools.MetaScanner import Meta_Scanner
from function_tools.PythonRunner import run_python_file
from function_tools.FileCreator import Create_File
from function_tools.OsHandler import Shell_Command
from function_tools.Refactor import File_Delete_Move
from function_tools.Validation import Test_Runner
from function_tools.WebSearch import Web_Search
from function_tools.PlannerTool import Plan_Generator
from function_tools.CodeGenerator import Code_Generator
# ================================================================

# === LLM (Gemini) ===============================================
def create_llm_with_current_key():
    """Create a new LLM instance with the current API key"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=get_api_key(),
        temperature=0.1,
    )

bugx_llm = create_llm_with_current_key()
# ================================================================

# === TOOL LIST ==================================================
BUGX_TOOLS = [
    Plan_Generator,
    Web_Search,
    Meta_Scanner,
    Content_Fetcher,
    Create_File,
    Code_Emitter,
    Code_Generator,
    Shell_Command,
    run_python_file,
    Test_Runner,
    File_Delete_Move,
]

# === SYSTEM PROMPT ==============================================
# In LangChain 1.0, we pass the system prompt string directly to create_agent.
# We no longer need manual {agent_scratchpad} placeholders.
SYSTEM_PROMPT = """\
You are BugX, an autonomous AI Software Engineer Agent.

You work inside a local project directory and have access to tools
that let you PLAN, READ, WRITE, RUN, TEST, and SEARCH codebases.

High-level tool usage guidelines:
- Plan_Generator: Use for broad tasks (e.g. "build X", "refactor app").
- Web_Search: Use for docs, errors, library examples.
- Meta_Scanner: Use to see file structure/sizes.
- Content_Fetcher: READ files before editing.
- Create_File: Create NEW files.
- Code_Emitter: OVERWRITE/UPDATE existing files.
- Code_Generator: Generate code logic.
- Shell_Command: Install deps, git commands. Avoid destructive commands.
- run_python_file: Execute entrypoint scripts.
- Test_Runner: Run pytest/npm test.

General behavior rules:
1. Think step by step.
2. Always read code (Content_Fetcher) before modifying it.
3. After finishing, provide a clear "Final Answer" summarizing actions.
"""

# === CREATE AGENT (LangChain 1.0+ Graph API) ====================
# create_agent builds a compiled graph. No AgentExecutor is needed.
def create_agent_with_current_llm():
    """Create a new agent with the current LLM instance"""
    return create_agent(
        model=bugx_llm,
        tools=BUGX_TOOLS,
        system_prompt=SYSTEM_PROMPT
    )

agent = create_agent_with_current_llm()
# ================================================================

# === RUNNER FUNCTION ============================================
def run_bugx_agent(user_input: str, working_directory: str = "./") -> Dict[str, Any]:
    """
    Runs the BugX agent using the LangChain 1.0 Graph API with API key rotation.
    Automatically rotates to alternate API keys when quota is exceeded.
    """
    global bugx_llm, agent
    original_cwd = os.getcwd()
    max_retries = len(get_all_api_keys())
    attempt = 0
    
    try:
        # 1. Switch to target directory
        if os.path.exists(working_directory):
            os.chdir(working_directory)
            print(f"moved to: {working_directory}")
        
        # 2. Invoke the agent with retry logic for quota errors
        while attempt < max_retries:
            try:
                # The new API expects a dictionary with "messages"
                result = agent.invoke({
                    "messages": [HumanMessage(content=user_input)]
                })

                # 3. Extract output
                # result["messages"][-1] is the final AI response
                final_output = result["messages"][-1].content
                return {"output": final_output}
                
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota error
                if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in str(type(e).__name__):
                    attempt += 1
                    if attempt < max_retries:
                        print(f"\n[API QUOTA EXCEEDED] Rotating to alternate API key (attempt {attempt+1}/{max_retries})...")
                        try:
                            new_key = rotate_api_key()
                            print(f"[INFO] Now using API key: {new_key[:20]}...")
                            # Recreate LLM and agent with new key
                            bugx_llm = create_llm_with_current_key()
                            agent = create_agent_with_current_llm()
                        except ValueError as ve:
                            return {"output": f"Critical Error: {str(ve)}"}
                    else:
                        return {"output": f"Critical Error: All API keys exhausted quota limits. {str(e)}"}
                else:
                    # Not a quota error, return the error
                    return {"output": f"Critical Error: {str(e)}"}

    except Exception as e:
        return {"output": f"Critical Error: {str(e)}"}
    finally:
        # 4. Cleanup: return to original directory
        os.chdir(original_cwd)

# ================================================================

if __name__ == "__main__":
    # Ensure test path exists
    test_path = r"E:\-BugX\Test_Project"
    if not os.path.exists(test_path):
        os.makedirs(test_path)

    print("Starting Agent...")
    result = run_bugx_agent(
        "Create me a simple todo app in Python without using any web frameworks.",
        working_directory=test_path
    )

    print("\n=== FINAL OUTPUT ===")
    print(result["output"])