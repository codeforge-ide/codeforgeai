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
