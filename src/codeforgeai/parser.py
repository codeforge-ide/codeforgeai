import argparse
import logging

def parse_cli(args):
    parser = argparse.ArgumentParser(description="CodeforgeAI AI agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subcommand: analyze working directory
    subparsers.add_parser("analyze", help="Analyze current working directory")
    
    # Subcommand: process a user prompt
    prompt_parser = subparsers.add_parser("prompt", help="Process a user prompt")
    prompt_parser.add_argument("user_prompt", nargs="+", help="User input prompt")
    
    # New subcommand: config checkup
    subparsers.add_parser("config", help="Run configuration checkup")
    
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
