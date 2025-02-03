import sys
import logging
import os
from codeforgeai.engine import Engine
from codeforgeai.parser import parse_cli
from codeforgeai.config import ensure_config_prompts, load_config
import json

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
    
    engine = Engine()
    if args.command == "analyze":
        if getattr(args, "loop", False):
            engine.run_analysis_loop()
        else:
            engine.run_analysis()
    elif args.command == "prompt":
        response = engine.process_prompt(args.user_prompt)
        print(response)
    elif args.command == "explain":
        explanation = engine.explain_code(args.file_path)
        print(explanation)
    else:
        print("No valid command provided. Use 'analyze', 'prompt', 'strip', 'config', or 'explain'.")

if __name__ == "__main__":
    main()
