import sys
import logging
import os
from codeforgeai.engine import Engine
from codeforgeai.parser import parse_cli
from codeforgeai.config import ensure_config_prompts
import json
import argparse  # <-- Ensure argparse is imported if not already

def setup_logging(loglevel):
    import sys
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

def parse_cli(args):
    parser = argparse.ArgumentParser(description="CodeforgeAI AI agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze current working directory")
    analyze_parser.add_argument("--loop", action="store_true", help="Enable adaptive feedback loop")
    
    prompt_parser = subparsers.add_parser("prompt", help="Process a user prompt")
    prompt_parser.add_argument("user_prompt", nargs="+", help="User input prompt")
    
    subparsers.add_parser("config", help="Run configuration checkup")
    subparsers.add_parser("strip", help="Print tree structure after removing gitignored files")
    subparsers.add_parser("commit-message", help="Generate commit message with gitmoji")
    
    # Add Vyper subcommand
    vyper_parser = subparsers.add_parser("vyper", help="Work with Vyper smart contracts")
    vyper_subparsers = vyper_parser.add_subparsers(dest="vyper_command", help="Available Vyper commands")
    
    # Compile command
    compile_parser = vyper_subparsers.add_parser("compile", help="Compile a Vyper smart contract")
    compile_parser.add_argument("file_path", help="Path to the Vyper contract file")
    compile_parser.add_argument("-f", "--format", choices=["abi", "bytecode", "bytecode_runtime", "ir", "asm", "source_map", "method_identifiers"], 
                               default="abi", help="Output format (default: abi)")
    compile_parser.add_argument("--optimize", choices=["none", "gas", "codesize"], 
                               help="Optimization mode: none, gas, or codesize")
    compile_parser.add_argument("--evm-version", help="Target EVM version")
    
    # Analyze command
    analyze_parser = vyper_subparsers.add_parser("analyze", help="Analyze a Vyper smart contract")
    analyze_parser.add_argument("file_path", help="Path to the Vyper contract file")
    
    # Check command
    vyper_subparsers.add_parser("check", help="Check if Vyper is installed")
    
    parser.add_argument("-v", "--verbose", dest="loglevel", help="set loglevel to INFO",
                        action="store_const", const=logging.INFO)
    parser.add_argument("-vv", "--very-verbose", dest="loglevel", help="set loglevel to DEBUG",
                        action="store_const", const=logging.DEBUG)
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Enable debug mode (overrides other verbosity flags)")
    return parser.parse_args(args)

def main():
    config_path = os.path.join(os.path.expanduser("~"), ".codeforgeai.json")
    args = parse_cli(sys.argv[1:])
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = args.loglevel if args.loglevel is not None else logging.WARNING
    setup_logging(loglevel)
    
    if args.command == "config":
        config = ensure_config_prompts(config_path)
        print("Configuration checkup complete. Current configuration:")
        print(json.dumps(config, indent=4))
        return
    
    if args.command == "strip":
        from codeforgeai.directory import strip_directory
        strip_directory()
        return
    
    if args.command == "github":
        if getattr(args, "github_command", None) == "copilot":
            from codeforgeai.integrations.github_copilot import copilot as copilot_lsp
            copilot_cmd = getattr(args, "copilot_command", None)
            if copilot_cmd == "lsp":
                copilot_lsp.install_copilot_language_server()
            elif copilot_cmd == "login":
                copilot_lsp.copilot_login()
            elif copilot_cmd == "logout":
                copilot_lsp.copilot_logout()
            elif copilot_cmd == "status":
                copilot_lsp.copilot_status()
            elif copilot_cmd == "inline-completion":
                copilot_lsp.copilot_lsp_inline_completion(args.file, args.line, args.character)
            elif copilot_cmd == "panel-completion":
                copilot_lsp.copilot_lsp_panel_completion(args.file, args.line, args.character)
            else:
                print("Invalid copilot subcommand. Use --help to see available commands.")
            return
        else:
            print("Invalid github subcommand. Use --help to see available commands.")
            return
    # Ensure config prompts are loaded

    engine = Engine()
    
    # Handle existing commands
    if args.command == "analyze":
        if getattr(args, "loop", False):
            engine.run_analysis_loop()
        else:
            engine.run_analysis()
    elif args.command == "prompt":
        response = engine.process_prompt(args.user_prompt)
        print(response)
    elif args.command == "commit-message":
        commit_message = engine.process_commit_message()
        print(commit_message)
    elif args.command == "explain":
        explanation = engine.explain_code(args.file_path)
        print(explanation)
    
    # NEW: Handle Secret AI commands
    elif args.command == "secret-ai":
        handle_secret_ai_commands(args)
    
    # NEW: Handle Web3 commands
    elif args.command == "web3":
        handle_web3_commands(args)
    
    # Handle Vyper commands
    elif args.command == "vyper":
        handle_vyper_commands(args)
    
    else:
        print("No valid command provided. Run with --help for available commands.")

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
        print("Invalid Secret AI command. Use --help to see available commands.")

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
    
    else:
        print("Invalid web3 command. Use --help to see available commands.")

def handle_vyper_commands(args):
    """Handle Vyper smart contract development commands"""
    
    try:
        from codeforgeai.integrations.vyper import compile_contract, check_vyper_installed, analyze_contract
    except ImportError:
        print("Error: Vyper integration not available. Check if the module is properly installed.")
        return
    
    if args.vyper_command == "compile":
        result = compile_contract(args.file_path, args.format, args.optimize, args.evm_version)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
            
        print(f"Contract compiled successfully!")
        if isinstance(result["output"], dict):
            print(json.dumps(result["output"], indent=2))
        else:
            print(result["output"])
            
    elif args.vyper_command == "analyze":
        result = analyze_contract(args.file_path)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
            
        print(f"Analysis of {os.path.basename(args.file_path)}:")
        print(f"Contract Type: {result.get('contract_type', 'Unknown')}")
        print("\nFeatures detected:")
        for feature, present in result.get('features', {}).items():
            status = "✓" if present else "✗"
            print(f"  {status} {feature.replace('_', ' ').replace('has ', '')}")
    
    elif args.vyper_command == "check":
        result = check_vyper_installed()
        
        if result["installed"]:
            print(f"Vyper is installed. Version: {result['version']}")
        else:
            print("Vyper is not installed or not in the PATH.")
            print("To install Vyper, follow the instructions at: https://docs.vyperlang.org/en/latest/installing-vyper.html")
    
    else:
        print("Invalid Vyper command. Use --help to see available commands.")

if __name__ == "__main__":
    main()
