"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = codeforgeai.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import json
import logging
import os
import sys
import re
from codeforgeai.config import load_config   # <-- Added import

from codeforgeai import __version__
from codeforgeai.engine import Engine as CodeforgeEngine
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.models.code_model import CodeModel

__author__ = "nathfavour"
__copyright__ = "nathfavour"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# Define a function to get models based on current config
def get_models():
    config_path = os.path.expanduser("~/.codeforgeai.json")
    try:
        config = load_config(config_path)
        general_model = GeneralModel(config.get("general_model", "ollama_general"))  # Provide default
        code_model = CodeModel(config.get("code_model", "ollama_code"))  # Provide default
        return general_model, code_model, config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default models in case of error
        return GeneralModel(), CodeModel(), {}

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from codeforgeai.skeleton import fib`,
# when using this Python module as a library.


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a


# ---- New Functions for CodeforgeAI ----
def create_default_config(config_path):
    default_config = {
        "general_model": "ollama_general",
        "general_prompt": "based on the below prompt and without returning anything else, restructure it so that it is strictly understandable to a coding ai agent with json output for file changes:",
        "code_model": "ollama_code",
        "code_prompt": "in very clear, concise manner, solve the below request:"
    }
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)
    return default_config

def load_config(config_path):
    if not os.path.exists(config_path):
        return create_default_config(config_path)
    with open(config_path) as f:
        return json.load(f)

def call_general_ai(prompt, config=None):
    general_model, _, _ = get_models()
    response = general_model.send_request(prompt, config)
    return response

def call_code_ai(prompt):
    _, code_model, _ = get_models()
    response = code_model.send_request(prompt)
    return response

def execute_changes(changes):
    print("Executing changes:")
    print(changes)
    # Placeholder: process JSON output and update files accordingly


# process prompting
def process_prompt(user_prompt):
    # Get fresh config each time the function is called
    _, _, config = get_models()
    combined_prompt = " ".join(user_prompt)
    
    # Finetune the prompt using the general AI model.
    finetune_prompt = config.get("prompt_finetune_prompt",
        "in a clear and concise manner, rephrase the following prompt to be more understandable to a coding ai agent, return the rephrased prompt and nothing else:")
    full_finetune_prompt = f"{finetune_prompt}\n\n{combined_prompt}"
    finetuned_response = call_general_ai(full_finetune_prompt, config)
    
    # Use the finetuned response to prompt the code AI model.
    final_response = call_code_ai(finetuned_response)
    print(final_response)

def explain_code(file_path):
    # Get fresh config each time the function is called
    _, _, config = get_models()
    explain_prompt = config.get("explain_code_prompt", "explain the following code in a clear and concise manner")
    
    with open(file_path, "r") as file:
        file_content = file.read()
    
    prompt = f"{explain_prompt}\n\nFile: {file_path}\n\n{file_content}"
    response = call_code_ai(prompt)
    return response

def extract_code_blocks(text):
    """Return a list of code blocks found between triple backticks."""
    pattern = r"```(.*?)```"
    blocks = re.findall(pattern, text, flags=re.DOTALL)
    return blocks

def format_code_blocks(text, separator):
    """Extract and format code blocks:
       - Remove a single-word first line if present (language descriptor).
       - Join code blocks with a separator (a number of newlines).
    """
    blocks = extract_code_blocks(text)
    formatted_blocks = []
    for block in blocks:
        lines = block.splitlines()
        if lines and " " not in lines[0].strip():
            # Remove first line assuming it's a language descriptor.
            lines = lines[1:]
        formatted_blocks.append("\n".join(lines))
    sep_str = "\n" * separator
    return sep_str.join(formatted_blocks)


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="CodeforgeAI AI agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze current working directory")
    analyze_parser.add_argument("--loop", action="store_true", help="Enable adaptive feedback loop")

    prompt_parser = subparsers.add_parser("prompt", help="Process a user prompt")
    prompt_parser.add_argument("user_prompt", nargs="+", help="User input prompt")

    subparsers.add_parser("config", help="Run configuration checkup")

    # Add strip subcommand
    subparsers.add_parser("strip", help="Print tree structure after removing gitignored files")

    # Add explain subcommand
    explain_parser = subparsers.add_parser("explain", help="Explain the code in the given file")
    explain_parser.add_argument("file_path", help="Path to the file to be explained")

    # Add extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract code blocks from file or string")
    extract_parser.add_argument("--file", help="Path to the file to process")
    extract_parser.add_argument("--string", help="Input string containing code blocks")

    # New subcommand: format
    format_parser = subparsers.add_parser("format", help="Format code blocks for readability")
    format_parser.add_argument("--file", help="Path to the file to process")
    format_parser.add_argument("--string", help="Input string containing code blocks")

    # New subcommand: command
    command_parser = subparsers.add_parser("command", help="Process a command request")
    command_parser.add_argument("user_command", nargs="+", help="User input command")

    # New subcommand: edit
    edit_parser = subparsers.add_parser("edit", help="Edit code in specified files or folders")
    edit_parser.add_argument("paths", nargs="+", help="Files or directories to edit")
    edit_parser.add_argument("--user_prompt", nargs="+", required=True, help="User prompt for editing")
    # Added --allow-ignore
    edit_parser.add_argument("--allow-ignore", action="store_true",
                             help="Allow explicitly passed directories to be processed even if .gitignore ignores them")

    # New subcommand: suggestion
    suggestion_parser = subparsers.add_parser("suggestion", help="Short suggestions from code model at lightning speed")
    suggestion_parser.add_argument("--file", help="File to read code from (defaults to last line unless --line is specified)")
    suggestion_parser.add_argument("--line", type=int, help="Line number to use for suggestion")
    suggestion_parser.add_argument("--string", nargs="*", help="User-provided code snippet for suggestion")
    # New optional flag
    suggestion_parser.add_argument("--entire", "-E", action="store_true",
                                   help="Send entire file content for suggestion (must be typed as one token: --entire)")

    # New subcommand: commit-message
    commit_parser = subparsers.add_parser("commit-message", help="Generate commit message with code changes and gitmoji")
    
    # NEW: Secret AI SDK integration subcommands
    secret_ai_parser = subparsers.add_parser("secret-ai", help="Secret AI SDK integration commands")
    secret_ai_subparsers = secret_ai_parser.add_subparsers(dest="secret_ai_command", help="Secret AI commands")
    
    # Secret AI subcommands
    secret_ai_subparsers.add_parser("list-models", help="List available Secret AI models")
    secret_ai_subparsers.add_parser("test-connection", help="Test Secret AI connection")
    secret_ai_chat_parser = secret_ai_subparsers.add_parser("chat", help="Chat with Secret AI")
    secret_ai_chat_parser.add_argument("message", nargs="+", help="Chat message")
    
    # NEW: Web3 subcommands
    web3_parser = subparsers.add_parser("web3", help="Web3 development commands")
    web3_subparsers = web3_parser.add_subparsers(dest="web3_command", help="Web3 commands")
    
    # Web3 subcommands
    scaffold_parser = web3_subparsers.add_parser("scaffold", help="Scaffold a new web3 project")
    scaffold_parser.add_argument("project_name", help="Name of the project")
    scaffold_parser.add_argument("--type", choices=["dapp", "smart-contract", "token", "nft"], default="dapp", help="Project type")
    scaffold_parser.add_argument("--output", help="Output directory")
    
    analyze_contract_parser = web3_subparsers.add_parser("analyze-contract", help="Analyze a smart contract")
    analyze_contract_parser.add_argument("contract_file", help="Path to the smart contract")
    
    gas_parser = web3_subparsers.add_parser("estimate-gas", help="Estimate gas costs for a smart contract")
    gas_parser.add_argument("contract_file", help="Path to the smart contract")
    
    tests_parser = web3_subparsers.add_parser("generate-tests", help="Generate tests for a smart contract")
    tests_parser.add_argument("contract_file", help="Path to the smart contract")
    tests_parser.add_argument("--output", help="Output directory for tests")
    
    web3_subparsers.add_parser("check-env", help="Check web3 development environment")
    
    # Web3 - install dependencies
    web3_deps_parser = web3_subparsers.add_parser("install-deps", help="Install web3 dependencies")
    web3_deps_parser.add_argument("--full", action="store_true", help="Install full set of dependencies")

    # NEW: ZerePy integration subcommands
    zerepy_parser = subparsers.add_parser("zerepy", help="ZerePy integration commands")
    zerepy_subparsers = zerepy_parser.add_subparsers(dest="zerepy_command", help="ZerePy commands")
    
    # ZerePy subcommands
    zerepy_subparsers.add_parser("status", help="Check ZerePy server status")
    zerepy_subparsers.add_parser("list-agents", help="List available ZerePy agents")
    
    zerepy_load_parser = zerepy_subparsers.add_parser("load-agent", help="Load a ZerePy agent")
    zerepy_load_parser.add_argument("agent_name", help="Name of the agent to load")
    
    zerepy_action_parser = zerepy_subparsers.add_parser("action", help="Execute a ZerePy action")
    zerepy_action_parser.add_argument("connection", help="Connection name")
    zerepy_action_parser.add_argument("action", help="Action name")
    zerepy_action_parser.add_argument("--params", help="Action parameters in JSON format")
    
    zerepy_chat_parser = zerepy_subparsers.add_parser("chat", help="Chat with a ZerePy agent")
    zerepy_chat_parser.add_argument("message", nargs="+", help="Chat message")

    # NEW: Solana MCP subcommands
    solana_parser = subparsers.add_parser("solana", help="Solana blockchain commands")
    solana_subparsers = solana_parser.add_subparsers(dest="solana_command", help="Solana commands")
    
    # Solana subcommands
    solana_subparsers.add_parser("status", help="Check Solana Agent status")
    
    balance_parser = solana_subparsers.add_parser("balance", help="Get wallet balance")
    balance_parser.add_argument("--address", help="Optional wallet address (uses agent wallet if not specified)")
    
    transfer_parser = solana_subparsers.add_parser("transfer", help="Transfer SOL to an address")
    transfer_parser.add_argument("destination", help="Destination wallet address")
    transfer_parser.add_argument("amount", type=float, help="Amount of SOL to transfer")
    transfer_parser.add_argument("--memo", help="Optional memo for the transaction")
    
    # MCP specific commands
    mcp_parser = solana_subparsers.add_parser("mcp", help="Solana MCP commands")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP commands")
    
    interact_parser = mcp_subparsers.add_parser("interact", help="Interact with an MCP")
    interact_parser.add_argument("program_id", help="Program ID of the MCP")
    interact_parser.add_argument("action_type", help="Type of action to perform")
    interact_parser.add_argument("--params", help="Parameters as JSON string")
    
    state_parser = mcp_subparsers.add_parser("state", help="Get state from an MCP")
    state_parser.add_argument("program_id", help="Program ID of the MCP")
    state_parser.add_argument("account_address", help="Account address to read from")
    
    init_account_parser = mcp_subparsers.add_parser("init-account", help="Initialize a new MCP account")
    init_account_parser.add_argument("program_id", help="Program ID of the MCP")
    init_account_parser.add_argument("space", type=int, help="Space to allocate for the account (bytes)")
    init_account_parser.add_argument("--params", help="Optional parameters as JSON string")

    parser.add_argument(
        "-v", "--verbose",
        dest="loglevel", help="set loglevel to INFO",
        action="store_const", const=logging.INFO
    )
    parser.add_argument(
        "-vv", "--very-verbose",
        dest="loglevel", help="set loglevel to DEBUG",
        action="store_const", const=logging.DEBUG
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Parse command line arguments and execute commands."""
    # Define config_path before parsing to ensure it's available for all code paths
    config_path = os.path.expanduser("~/.codeforgeai.json")
    
    args = parse_args(args)
    loglevel = args.loglevel if args.loglevel is not None else logging.WARNING
    setup_logging(loglevel)
    _logger.debug("Starting CodeforgeAI...")

    # Load fresh config directly from file - don't use cached values
    if args.command == "config":
        from codeforgeai.config import ensure_config_prompts
        # Ensure we're loading directly from the file, not from any cached values
        config = ensure_config_prompts(config_path)
        print("Configuration checkup complete. Current configuration:")
        print(json.dumps(config, indent=4))
        return
    
    # Get fresh config for all operations - don't use cached values
    general_model, code_model, config = get_models()

    if args.command == "config":
        from codeforgeai.config import ensure_config_prompts
        config = ensure_config_prompts(config_path)
        print("Configuration checkup complete. Current configuration:")
        print(json.dumps(config, indent=4))
        return
    
    if args.command == "analyze":
        # Instead of calling the dummy function,
        # call Engine().run_analysis() to leverage the code AI model
        eng = CodeforgeEngine()
        eng.run_analysis()
    elif args.command == "prompt":
        process_prompt(args.user_prompt)
    elif args.command == "strip":
        from codeforgeai.directory import strip_directory
        strip_directory()
        return
    elif args.command == "explain":
        eng = CodeforgeEngine()
        explanation = eng.explain_code(args.file_path)
        print(explanation)
    elif args.command == "extract":
        # read from file if present, else use string
        if args.file:
            with open(args.file, "r") as f:
                content = f.read()
            blocks = extract_code_blocks(content)
            json_output = json.dumps(blocks, indent=4)
            with open(args.file, "w") as f:
                f.write(json_output)
            print("Extracted code blocks written to file as JSON.")
        elif args.string:
            blocks = extract_code_blocks(args.string)
            print(json.dumps(blocks, indent=4))
        else:
            print("No file or string provided for extraction.")
        return
    elif args.command == "format":
        # Load format_line_separator from config
        from codeforgeai.config import load_config
        # Use the same config_path used in skeleton
        config_path = os.path.expanduser("~/.codeforgeai.json")
        config_data = load_config(config_path)
        separator = config_data.get("format_line_separator", 1)
        if args.file:
            with open(args.file, "r") as f:
                content = f.read()
            formatted = format_code_blocks(content, separator)
            with open(args.file, "w") as f:
                f.write(formatted)
            print("Formatted code blocks written to file.")
        elif args.string:
            formatted = format_code_blocks(args.string, separator)
            print(formatted)
        else:
            print("No file or string provided for formatting.")
        return
    elif args.command == "command":
        # Get user command as string
        user_input = " ".join(args.user_command)
        
        # Stage 1: Prompt general model with code_or_command prompt.
        code_or_command_prompt = config.get("code_or_command", 
            "reply with either code or command only; is the below request best satisfied with a code response or command response:")
        full_prompt = f"{code_or_command_prompt}\n{user_input}"
        response = call_general_ai(full_prompt, config)
        
        # Check if 'command' appears before 'code'
        pos_command = response.lower().find("command")
        pos_code = response.lower().find("code")
        if pos_command != -1 and (pos_code == -1 or pos_command < pos_code):
            # Stage 2: Prompt the code model with command_agent_prompt and the same user input.
            command_agent_prompt = config.get("command_agent_prompt", 
                "one for each line and nothing else, return a list of commands that can be executed to achieve the below request, and nothing else:")
            final_prompt = f"{command_agent_prompt}\n{user_input}"
            final_response = call_code_ai(final_prompt)
            print(final_response)
        else:
            print("The request was not classified as a command.")
        return
    elif args.command == "edit":
        from codeforgeai.directory import parse_gitignore, should_ignore
        from codeforgeai.engine import Engine
        _logger.debug("Edit command: Starting file collection...")
        ignore_patterns = parse_gitignore()

        # Modified gather_files to handle allow_ignore
        def gather_files(paths, allow_ignore=False):
            collected = []
            for p in paths:
                abs_p = os.path.abspath(p)
                _logger.debug(f"Processing path: {abs_p}")

                if os.path.isfile(abs_p):
                    if not should_ignore(abs_p, ignore_patterns):
                        collected.append(abs_p)
                        _logger.debug(f"Added file: {abs_p}")
                elif os.path.isdir(abs_p):
                    # If allow_ignore is set, add directory itself
                    if allow_ignore and not abs_p in collected:
                        collected.append(abs_p)
                        _logger.debug(f"Allowed directory: {abs_p}")

                    for root, dirs, files in os.walk(abs_p):
                        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]
                        for f in files:
                            fp = os.path.join(root, f)
                            if not should_ignore(fp, ignore_patterns):
                                collected.append(fp)
                                _logger.debug(f"Added file: {fp}")
            return collected

        try:
            files_to_edit = gather_files(args.paths, args.allow_ignore)
            _logger.debug(f"Found {len(files_to_edit)} files to process")
            
            # Convert to relative paths and sort
            rel_paths = sorted([os.path.relpath(fp, os.getcwd()) for fp in files_to_edit])
            user_edit_prompt = " ".join(args.user_prompt)
            edit_finetune_prompt = config.get("edit_finetune_prompt", 
                "attend to the below prompt, editing the provided code and returning nothing but the edited code:")

            eng = Engine()
            _logger.debug("Initialized Engine for processing")

            for rel_path in rel_paths:
                _logger.debug(f"Processing file: {rel_path}")
                try:
                    with open(rel_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    combined_prompt = f"{edit_finetune_prompt}\n{user_edit_prompt}\n{rel_path}\n{content}"
                    _logger.debug(f"Sending request to AI model for {rel_path}")
                    
                    response = eng.code_model.send_request(combined_prompt)
                    _logger.debug(f"Received response from AI model for {rel_path}")
                    
                    edited_code = format_code_blocks(response, separator=config.get("format_line_separator", 1))
                    out_path = f"{rel_path}.codeforgedit"
                    
                    with open(out_path, "w", encoding="utf-8") as outf:
                        outf.write(edited_code)
                    print(f"Edited code saved to: {out_path}")
                except Exception as e:
                    _logger.error(f"Error processing {rel_path}: {e}")
                    continue
            
            _logger.debug("Edit command: Completed processing all files")
        except Exception as e:
            _logger.error(f"Edit command failed: {e}")
    elif args.command == "suggestion":
        suggestion_prompt = config.get("suggestion_prompt", "Provide a short suggestion:")
        input_code = None

        if args.string:
            # User-provided code snippet
            input_code = " ".join(args.string)
            suggestion_response = call_code_ai(f"{suggestion_prompt}\n{input_code}")
            suggested_code = format_code_blocks(suggestion_response, 1)
            print(suggested_code)
            return
        elif args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if args.entire:
                    entire_content = "".join(lines)
                    # Use entire_suggestion_prompt if available, else fallback to suggestion_prompt
                    entire_suggestion_prompt = config.get("entire_suggestion_prompt", suggestion_prompt)
                    suggestion_response = call_code_ai(f"{entire_suggestion_prompt}\n{entire_content}")
                    suggested_output = format_code_blocks(suggestion_response, 1)
                    # New check to align first line
                    original_first_line = lines[0].rstrip("\n")
                    splitted_suggested = suggested_output.splitlines()
                    if original_first_line in splitted_suggested:
                        first_match_index = splitted_suggested.index(original_first_line)
                        splitted_suggested = splitted_suggested[first_match_index:]
                        suggested_output = "\n".join(splitted_suggested)

                    out_path = f"{args.file}.cfsuggestions"
                    with open(out_path, "w", encoding="utf-8") as outf:
                        outf.write(suggested_output)
                    print(f"Suggestion applied to {out_path}")
                else:
                    # File-based suggestion
                    target_line_index = args.line - 1 if args.line else len(lines) - 1
                    if target_line_index < 0 or target_line_index >= len(lines):
                        print("Invalid line number for suggestion.")
                        return

                    # Use the target line
                    target_line = lines[target_line_index].rstrip("\n")
                    suggestion_response = call_code_ai(f"{suggestion_prompt}\n{target_line}")
                    suggested_line = format_code_blocks(suggestion_response, 1).strip("\n")

                    # Replace just the target line
                    lines[target_line_index] = f"{suggested_line}\n"

                    # Save modified content
                    out_path = f"{args.file}.cfsuggestions"
                    with open(out_path, "w", encoding="utf-8") as outf:
                        outf.writelines(lines)

                    print(f"Suggestion applied to {out_path}")
            except Exception as e:
                _logger.error(f"Error handling suggestion for {args.file}: {e}")
        else:
            print("No input provided for suggestion (use --string or --file).")
        return
    elif args.command == "commit-message":
        eng = CodeforgeEngine()
        commit_msg = eng.process_commit_message()
        print(commit_msg)
        return
    # NEW: Handle Secret AI commands
    elif args.command == "secret-ai":
        handle_secret_ai_commands(args)
    # NEW: Handle Web3 commands
    elif args.command == "web3":
        handle_web3_commands(args)
    # NEW: Handle ZerePy commands
    elif args.command == "zerepy":
        handle_zerepy_commands(args)
        return
    # NEW: Handle Solana commands
    elif args.command == "solana":
        handle_solana_commands(args)
    else:
        print("No valid command provided. Use 'analyze', 'prompt', 'strip', 'config', 'explain', or 'edit'.")


# Add handler functions for Secret AI and Web3 commands
def handle_secret_ai_commands(args):
    """Handle Secret AI SDK integration commands"""
    import codeforgeai.utils as utils
    
    # Import inside function to avoid circular imports
    try:
        from codeforgeai.integrations.secret_ai.secret_ai_integration import SecretAIModel, list_secret_ai_models
    except ImportError:
        print("Error: Secret AI SDK integration not available. Install required packages.")
        return
    
    if args.secret_ai_command == "list-models":
        models = list_secret_ai_models()
        if models:
            print("Available Secret AI models:")
            for i, model in enumerate(models, 1):
                print(f"{i}. {model}")
        else:
            print("No Secret AI models available. Check your credentials.")
    
    elif args.secret_ai_command == "test-connection":
        if not utils.check_secret_ai_credentials():
            print("Error: Secret AI API key not found. Set the CLAIVE_AI_API_KEY environment variable.")
            return
            
        model = SecretAIModel()
        model_info = model.get_model_info()
        
        if not model_info["current_model"]:
            print("Error: Could not connect to Secret AI. Check your credentials.")
        else:
            print(f"Connected to Secret AI successfully.")
            print(f"Current model: {model_info['current_model']}")
            print(f"Available models: {', '.join(model_info['available_models'])}")
    
    elif args.secret_ai_command == "chat":
        if not utils.check_secret_ai_credentials():
            print("Error: Secret AI API key not found. Set the CLAIVE_AI_API_KEY environment variable.")
            return
            
        message = " ".join(args.message)
        model = SecretAIModel()
        response = model.send_request(message)
        print("\nSecret AI response:")
        print(response)
    
    else:
        print("Invalid Secret AI command. Use 'codeforgeai secret-ai --help' to see available commands.")

def handle_web3_commands(args):
    """Handle Web3 development commands"""
    import codeforgeai.utils as utils
    
    # Import inside function to avoid circular imports
    try:
        from codeforgeai.integrations.secret_ai.web3_commands import (
            scaffold_web3_project, 
            analyze_smart_contract,
            estimate_gas_costs,
            generate_web3_tests
        )
    except ImportError:
        print("Error: Web3 integration not available. Install required packages.")
        return
    
    if args.web3_command == "scaffold":
        result = scaffold_web3_project(
            project_name=args.project_name,
            project_type=args.type,
            output_dir=args.output
        )
        print(result)
    
    elif args.web3_command == "analyze-contract":
        result = analyze_smart_contract(args.contract_file)
        print(utils.format_smart_contract_analysis(result))
    
    elif args.web3_command == "estimate-gas":
        result = estimate_gas_costs(args.contract_file)
        print(result)
    
    elif args.web3_command == "generate-tests":
        tests = generate_web3_tests(args.contract_file)
        
        if "error" in tests:
            print(f"Error: {tests['error']}")
            return
            
        output_dir = args.output or os.path.dirname(args.contract_file) or os.getcwd()
        tests_dir = os.path.join(output_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        
        for test_file, content in tests.items():
            file_path = os.path.join(tests_dir, os.path.basename(test_file))
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Generated test file: {file_path}")
    
    elif args.web3_command == "check-env":
        env_status = utils.check_web3_dev_environment()
        print("Web3 Development Environment:")
        for tool, status in env_status.items():
            print(f"- {tool}: {status}")
    
    elif args.web3_command == "install-deps":
        install_type = "full" if args.full else "minimal" 
        result = utils.install_web3_dependencies(install_type)
        print(result)
    
    else:
        print("Invalid web3 command. Use 'codeforgeai web3 --help' to see available commands.")

# Add handler function for ZerePy commands
def handle_zerepy_commands(args):
    """Handle ZerePy integration commands"""
    import json
    
    # Import inside function to avoid circular imports
    try:
        from codeforgeai.integrations.zerepy.zerepy_integration import ZerePyClient, is_zerepy_available
    except ImportError:
        print("Error: ZerePy integration not available. Install required packages.")
        return
    
    if not is_zerepy_available():
        print("Error: ZerePy server is not available. Make sure it's running.")
        return
        
    client = ZerePyClient()
    
    if args.zerepy_command == "status":
        status = client.server_status()
        print("ZerePy Server Status:")
        print(json.dumps(status, indent=2))
        
    elif args.zerepy_command == "list-agents":
        agents = client.list_agents()
        print("Available ZerePy Agents:")
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent}")
            
    elif args.zerepy_command == "load-agent":
        response = client.load_agent(args.agent_name)
        print(f"Load agent response: {json.dumps(response, indent=2)}")
        
    elif args.zerepy_command == "action":
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format for parameters")
                return
                
        result = client.perform_action(args.connection, args.action, params)
        print("Action result:")
        print(json.dumps(result, indent=2))
        
    elif args.zerepy_command == "chat":
        message = " ".join(args.message)
        response = client.chat(message)
        print("\nZerePy Agent Response:")
        print(response)
    
    else:
        print("Invalid ZerePy command. Use 'codeforgeai zerepy --help' to see available commands.")

# Add handler function for Solana commands
def handle_solana_commands(args):
    """Handle Solana blockchain commands"""
    
    # Import inside function to avoid circular imports
    try:
        from codeforgeai.integrations.solana_agent import (
            check_solana_agent_setup,
            get_wallet_balance,
            send_transaction,
            interact_with_mcp,
            get_mcp_state,
            init_mcp_account
        )
    except ImportError:
        print("Error: Solana Agent integration not available. Install required packages.")
        return
    
    if args.solana_command == "status":
        status = check_solana_agent_setup()
        if status["available"]:
            print("✅ Solana Agent is running")
            if "status" in status:
                print(f"Network: {status['status'].get('network', 'unknown')}")
                print(f"Agent address: {status['status'].get('address', 'unknown')}")
        else:
            print("❌ Solana Agent is not available")
            print("\nEnvironment variables:")
            for var, exists in status.get("env_vars", {}).items():
                symbol = "✓" if exists else "✗"
                print(f"  {symbol} {var}")
            print("\nMake sure the Solana Agent is running on http://localhost:3000")
            print("To install the agent, follow the instructions in the documentation.")
    
    elif args.solana_command == "balance":
        result = get_wallet_balance(args.address)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Address: {result.get('address', 'unknown')}")
            print(f"Balance: {result.get('balance', 0)} SOL")
    
    elif args.solana_command == "transfer":
        result = send_transaction(args.destination, args.amount, args.memo)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Transaction successful!")
            print(f"Transaction ID: {result.get('signature', 'unknown')}")
            print(f"From: {result.get('sender', 'unknown')}")
            print(f"To: {result.get('destination', 'unknown')}")
            print(f"Amount: {args.amount} SOL")
    
    elif args.solana_command == "mcp":
        if args.mcp_command == "interact":
            try:
                params = json.loads(args.params) if args.params else {}
            except json.JSONDecodeError:
                print("Error: Invalid JSON for parameters")
                return
                
            result = interact_with_mcp(args.program_id, args.action_type, params)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"MCP interaction successful!")
                print(json.dumps(result, indent=2))
        
        elif args.mcp_command == "state":
            result = get_mcp_state(args.program_id, args.account_address)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"MCP State:")
                print(json.dumps(result.get("state", {}), indent=2))
        
        elif args.mcp_command == "init-account":
            try:
                params = json.loads(args.params) if args.params else None
            except json.JSONDecodeError:
                print("Error: Invalid JSON for parameters")
                return
                
            result = init_mcp_account(args.program_id, args.space, params)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"MCP account initialized successfully!")
                print(f"Account address: {result.get('address', 'unknown')}")
                print(f"Program ID: {args.program_id}")
        else:
            print("Invalid MCP command. Use --help to see available commands.")
    else:
        print("Invalid Solana command. Use --help to see available commands.")

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m codeforgeai.skeleton 42
    #
    run()
