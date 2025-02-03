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
