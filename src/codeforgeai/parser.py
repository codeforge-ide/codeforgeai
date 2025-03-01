import argparse
import logging

def parse_cli(args):
    parser = argparse.ArgumentParser(description="CodeforgeAI AI agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subcommand: analyze working directory
    analyze_parser = subparsers.add_parser("analyze", help="Analyze current working directory")
    analyze_parser.add_argument("--loop", action="store_true", help="Enable adaptive feedback loop")
    
    # Subcommand: process a user prompt
    prompt_parser = subparsers.add_parser("prompt", help="Process a user prompt")
    prompt_parser.add_argument("user_prompt", nargs="+", help="User input prompt")
    
    # Subcommand: configuration checkup
    subparsers.add_parser("config", help="Run configuration checkup")
    
    # New subcommand: strip gitignored files from tree structure
    subparsers.add_parser("strip", help="Print tree structure after removing gitignored files")
    
    # New subcommand: explain code
    explain_parser = subparsers.add_parser("explain", help="Explain code in a file")
    explain_parser.add_argument("file_path", help="Relative path to the file to be explained")
    
    # NEW: Secret AI SDK integration subcommands
    secret_ai_parser = subparsers.add_parser("secret-ai", help="Secret AI SDK integration commands")
    secret_ai_subparsers = secret_ai_parser.add_subparsers(dest="secret_ai_command", help="Secret AI commands")
    
    # Secret AI - list models
    secret_ai_subparsers.add_parser("list-models", help="List available Secret AI models")
    
    # Secret AI - test connection
    secret_ai_subparsers.add_parser("test-connection", help="Test Secret AI connection")
    
    # Secret AI - chat
    secret_ai_chat_parser = secret_ai_subparsers.add_parser("chat", help="Chat with Secret AI")
    secret_ai_chat_parser.add_argument("message", nargs="+", help="Chat message")
    
    # NEW: Web3 subcommands
    web3_parser = subparsers.add_parser("web3", help="Web3 development commands")
    web3_subparsers = web3_parser.add_subparsers(dest="web3_command", help="Web3 commands")
    
    # Web3 - scaffold project
    web3_scaffold_parser = web3_subparsers.add_parser("scaffold", help="Scaffold a new web3 project")
    web3_scaffold_parser.add_argument("project_name", help="Name of the project")
    web3_scaffold_parser.add_argument("--type", choices=["dapp", "smart-contract", "token", "nft"], 
                                    default="dapp", help="Project type")
    web3_scaffold_parser.add_argument("--output", help="Output directory")
    
    # Web3 - analyze contract
    web3_analyze_parser = web3_subparsers.add_parser("analyze-contract", help="Analyze a smart contract")
    web3_analyze_parser.add_argument("contract_file", help="Path to the smart contract")
    
    # Web3 - estimate gas
    web3_gas_parser = web3_subparsers.add_parser("estimate-gas", help="Estimate gas costs for a smart contract")
    web3_gas_parser.add_argument("contract_file", help="Path to the smart contract")
    
    # Web3 - generate tests
    web3_tests_parser = web3_subparsers.add_parser("generate-tests", help="Generate tests for a smart contract")
    web3_tests_parser.add_argument("contract_file", help="Path to the smart contract")
    web3_tests_parser.add_argument("--output", help="Output directory for tests")
    
    # Web3 - check environment
    web3_subparsers.add_parser("check-env", help="Check web3 development environment")
    
    # Web3 - install dependencies
    web3_deps_parser = web3_subparsers.add_parser("install-deps", help="Install web3 dependencies")
    web3_deps_parser.add_argument("--full", action="store_true", help="Install full set of dependencies")
    
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
    # New debug flag that overrides loglevel
    parser.add_argument(
        "--debug", action="store_true", default=False,
        help="Enable debug mode (overrides other verbosity flags)"
    )
    return parser.parse_args(args)
