import os
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler    # ✔️ valid

# If you already use this pattern in other files:
from config import google_api
GOOGLE_API_KEY = google_api



# === IMPORT YOUR TOOLS HERE ======================================
# Adjust these imports to match your project structure

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
bugx_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1,   
)
# ================================================================


# === REACT SYSTEM PROMPT ========================================
REACT_PROMPT_TEMPLATE = """\
You are BugX, an autonomous AI Software Engineer Agent.

You work inside a local project directory and have access to tools
that let you PLAN, READ, WRITE, RUN, TEST, and SEARCH codebases.

Your job:
- Understand the user’s request.
- Decide which tools to call and in what order.
- Use the tools to inspect and modify the codebase.
- Finish with a clear, useful answer for the user.

High-level tool usage guidelines (IMPORTANT):

- Plan_Generator:
  Use this when the user request is broad or multi-step
  (e.g. "build X project", "add a whole feature", "refactor the app").
  It returns a step-by-step plan you can then execute using other tools.

- Web_Search:
  Use when you need:
    * library / framework docs
    * error explanations
    * install commands
    * examples for unfamiliar tech
  Always prefer this instead of guessing for unknown APIs.

- Meta_Scanner:
  Use when you need an overview of the repo
  (what files/folders exist, sizes, structure) before editing.

- Content_Fetcher:
  Use when you need to READ a file before changing it,
  or to understand existing code/context.

- Create_File:
  Use when you need to create a brand new file with some content
  (e.g. new module, component, config, test file).

- Code_Emitter:
  Use when you want to OVERWRITE or update a file with new content
  (often after generating code with Code_Generator).

- Code_Generator:
  Use when you need to GENERATE or MODIFY code.
  Combine it with Content_Fetcher (to get existing code) and Code_Emitter
  (to write back the new version).

- Shell_Command:
  Use for shell-level tasks inside the project:
    * installing dependencies (pip / npm / etc.)
    * running non-Python commands (npm run, node, docker, etc.)
    * git commands (status, diff, etc.)
  Avoid destructive commands (rm, format, etc.) unless clearly required.

- run_python_file:
  Use specifically when you need to run a Python entrypoint file
  (e.g. "run main.py", "execute this script").

- Test_Runner:
  Use when you need to run the project’s tests (pytest, npm test, etc.)
  to validate changes and see failures.

- File_Delete_Move:
  Use when you need to delete or rename/move files or directories.
  Only use this when refactoring, cleaning up unused files,
  or following explicit user instructions.

General behavior rules:

- Think step by step.
- Prefer reading (Meta_Scanner + Content_Fetcher) BEFORE heavy edits.
- Prefer Plan_Generator for big tasks, then execute plan steps.
- Prefer Web_Search instead of inventing unknown API details.
- Avoid dangerous or destructive changes unless clearly justified.
- After finishing tool calls, give a clear "Final Answer" that:
  * summarizes what you did,
  * mentions key files changed,
  * mentions commands/tests run,
  * lists any remaining TODOs for the user.

You MUST follow the ReAct format:

Thought: you should always think about what to do next
Action: the action to take, must be one of [{tool_names}]
Action Input: the JSON-serializable input to that tool
Observation: the result of the tool

(Repeat Thought/Action/Action Input/Observation as needed.)

When you’re done using tools:

Thought: I now know the final answer
Final Answer: a direct, helpful answer to the user’s question.

Tools:
{tools}

Begin!

Question: {input}
{agent_scratchpad}
"""
# ================================================================
class BugXCallback(BaseCallbackHandler):
    """Callback to print agent's internal reasoning steps & tool outputs."""

    def on_agent_action(self, action, **kwargs):
        print("\n====================== AGENT ACTION ======================")
        print("Tool:", action.tool)
        print("Input:", action.tool_input)

    def on_tool_end(self, output, **kwargs):
        print("\n======================= TOOL OUTPUT =======================")
        print(output)

    def on_text(self, text, **kwargs):
        print("\n======================= AGENT THOUGHT =====================")
        print(text)

# === BUILD PROMPT, AGENT & EXECUTOR ============================
prompt = ChatPromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
# ReAct prompt needs these extra variables
if "tools" not in prompt.input_variables:
    prompt.input_variables.append("tools")
if "tool_names" not in prompt.input_variables:
    prompt.input_variables.append("tool_names")

# List of all tools you want the agent to use
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
# Build agent
agent = create_react_agent(
    llm=bugx_llm,
    tools=BUGX_TOOLS,
    prompt=prompt,
)

bugx_agent = AgentExecutor(
    agent=agent,
    tools=BUGX_TOOLS,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
)


# ================================================================
# 🔥 RUNNER FUNCTION WITH CALLBACK (prints full execution)
# ================================================================
def run_bugx_agent(user_input: str, working_directory: str = "./") -> Dict[str, Any]:
    """
    Run the BugX ReAct agent on a single user input and working directory.

    Returns the full AgentExecutor result dict.
    The final natural-language answer is in result["output"].
    """
    callbacks = [BugXCallback()]

    return bugx_agent.invoke(
        {
            "input": user_input,
            "working_directory": working_directory,
        },
        config={"callbacks": callbacks}
    )



if __name__ == "__main__":
    result = run_bugx_agent(
        "Create a small FastAPI app with one /health endpoint and tests.",
        working_directory=r"E:\-BugX\Test_Project"
    )
    print("\n=== FINAL OUTPUT ===")
    print(result["output"])
