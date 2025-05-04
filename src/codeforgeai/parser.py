import argparse
import logging

def parse_cli(args):
    parser = argparse.ArgumentParser(description="CodeforgeAI AI agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True) # Make command required

    # --- GitHub Copilot Integration ---
    # Ensure 'github' is added to the main subparsers
    github_parser = subparsers.add_parser("github", help="GitHub Copilot integration")
    github_subparsers = github_parser.add_subparsers(dest="github_command", help="GitHub Copilot commands", required=True)
    copilot_parser = github_subparsers.add_parser("copilot", help="Github copilot integration")
    copilot_subparsers = copilot_parser.add_subparsers(dest="copilot_command", help="Copilot commands", required=True)
    copilot_subparsers.add_parser("login", help="Authenticate with GitHub Copilot")
    copilot_subparsers.add_parser("logout", help="Logout from GitHub Copilot")
    copilot_subparsers.add_parser("status", help="Check GitHub Copilot status")
    copilot_subparsers.add_parser("lsp", help="install copilot language server globally")
    inline_parser = copilot_subparsers.add_parser("inline-completion", help="Get inline code completion at a specific position")
    inline_parser.add_argument("--file", required=True, help="Path to the file")
    inline_parser.add_argument("--line", type=int, required=True, help="Line number (0-based)")
    inline_parser.add_argument("--character", type=int, required=True, help="Character position (0-based)")
    panel_parser = copilot_subparsers.add_parser("panel-completion", help="Get panel (multi-line) code completion at a specific position")
    panel_parser.add_argument("--file", required=True, help="Path to the file")
    panel_parser.add_argument("--line", type=int, required=True, help="Line number (0-based)")
    panel_parser.add_argument("--character", type=int, required=True, help="Character position (0-based)")

    # --- Existing Core Commands ---
    # Ensure all other commands are also added to the main subparsers
    analyze_parser = subparsers.add_parser("analyze", help="Analyze current working directory")
    analyze_parser.add_argument("--loop", action="store_true", help="Enable adaptive feedback loop")

    prompt_parser = subparsers.add_parser("prompt", help="Process a user prompt")
    prompt_parser.add_argument("user_prompt", nargs="+", help="User input prompt")

    subparsers.add_parser("config", help="Run configuration checkup")

    subparsers.add_parser("strip", help="Print tree structure after removing gitignored files")

    explain_parser = subparsers.add_parser("explain", help="Explain code in a file")
    explain_parser.add_argument("file_path", help="Relative path to the file to be explained")

    extract_parser = subparsers.add_parser("extract", help="Extract code blocks from file or string")
    extract_parser.add_argument("--file", help="Path to the file to process")
    extract_parser.add_argument("--string", help="Input string containing code blocks")

    format_parser = subparsers.add_parser("format", help="Format code blocks for readability")
    format_parser.add_argument("--file", help="Path to the file to process")
    format_parser.add_argument("--string", help="Input string containing code blocks")

    command_parser = subparsers.add_parser("command", help="Process a command request")
    command_parser.add_argument("user_command", nargs="+", help="User input command")

    edit_parser = subparsers.add_parser("edit", help="Edit code in specified files or folders")
    edit_parser.add_argument("paths", nargs="+", help="Files or directories to edit")
    edit_parser.add_argument("--user_prompt", nargs="+", required=True, help="User prompt for editing")
    edit_parser.add_argument("--allow-ignore", action="store_true", help="Allow explicitly passed directories to be processed even if .gitignore ignores them")

    suggestion_parser = subparsers.add_parser("suggestion", help="Short suggestions from code model at lightning speed")
    suggestion_parser.add_argument("--file", help="File to read code from (defaults to last line unless --line is specified)")
    suggestion_parser.add_argument("--line", type=int, help="Line number to use for suggestion")
    suggestion_parser.add_argument("--string", nargs="*", help="User-provided code snippet for suggestion")
    suggestion_parser.add_argument("--entire", "-E", action="store_true", help="Send entire file content for suggestion (must be typed as one token: --entire)")

    subparsers.add_parser("commit-message", help="Generate commit message with code changes and gitmoji")

    # --- Secret AI Integration ---
    secret_ai_parser = subparsers.add_parser("secret-ai", help="Secret AI SDK integration commands")
    secret_ai_subparsers = secret_ai_parser.add_subparsers(dest="secret_ai_command", help="Secret AI commands", required=True)
    secret_ai_subparsers.add_parser("list-models", help="List available Secret AI models")
    secret_ai_subparsers.add_parser("test-connection", help="Test Secret AI connection")
    secret_ai_chat_parser = secret_ai_subparsers.add_parser("chat", help="Chat with Secret AI")
    secret_ai_chat_parser.add_argument("message", nargs="+", help="Chat message")

    # --- Web3 Integration ---
    web3_parser = subparsers.add_parser("web3", help="Web3 development commands")
    web3_subparsers = web3_parser.add_subparsers(dest="web3_command", help="Web3 commands", required=True)
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
    web3_deps_parser = web3_subparsers.add_parser("install-deps", help="Install web3 dependencies")
    web3_deps_parser.add_argument("--full", action="store_true", help="Install full set of dependencies")

    # --- ZerePy Integration ---
    zerepy_parser = subparsers.add_parser("zerepy", help="ZerePy integration commands")
    zerepy_subparsers = zerepy_parser.add_subparsers(dest="zerepy_command", help="ZerePy commands", required=True)
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

    # --- Solana Integration ---
    solana_parser = subparsers.add_parser("solana", help="Solana blockchain commands")
    solana_subparsers = solana_parser.add_subparsers(dest="solana_command", help="Solana commands", required=True)
    solana_subparsers.add_parser("status", help="Check Solana Agent status")
    balance_parser = solana_subparsers.add_parser("balance", help="Get wallet balance")
    balance_parser.add_argument("--address", help="Optional wallet address (uses agent wallet if not specified)")
    transfer_parser = solana_subparsers.add_parser("transfer", help="Transfer SOL to an address")
    transfer_parser.add_argument("destination", help="Destination wallet address")
    transfer_parser.add_argument("amount", type=float, help="Amount of SOL to transfer")
    transfer_parser.add_argument("--memo", help="Optional memo for the transaction")
    mcp_parser = solana_subparsers.add_parser("mcp", help="Solana MCP commands")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP commands", required=True)
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

    # --- Global Arguments ---
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
    parser.add_argument(
        "--debug", action="store_true", default=False,
        help="Enable debug mode (overrides other verbosity flags)"
    )

    return parser.parse_args(args)
