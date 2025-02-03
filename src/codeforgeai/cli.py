import sys
import logging
import os
from codeforgeai.engine import Engine
from codeforgeai.parser import parse_cli
from codeforgeai.config import ensure_config_prompts

def setup_logging(loglevel):
    import sys
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

def main():
    # Ensure config prompts and other necessary keys are present irrespective of command
    config_path = os.path.join(os.path.expanduser("~"), ".codeforgeai.json")
    ensure_config_prompts(config_path)
    
    args = parse_cli(sys.argv[1:])
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = args.loglevel if args.loglevel is not None else logging.WARNING
    setup_logging(loglevel)
    
    engine = Engine()
    if args.command == "analyze":
        engine.run_analysis()
    elif args.command == "prompt":
        engine.process_prompt(args.user_prompt)
    else:
        print("No valid command provided. Use 'analyze' or 'prompt'.")

if __name__ == "__main__":
    main()
