import sys
import logging
from codeforgeai.engine import Engine
from codeforgeai.parser import parse_cli

def setup_logging(loglevel):
    import sys
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

def main():
    args = parse_cli(sys.argv[1:])
    # Use --debug flag to override loglevel if set
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
