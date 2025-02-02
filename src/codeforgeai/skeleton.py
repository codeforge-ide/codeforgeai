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

from codeforgeai import __version__

__author__ = "nathfavour"
__copyright__ = "nathfavour"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


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

def analyze_working_directory():
    # Dummy analysis of current directory
    analysis = {
        "useful": ["file1.py", "file2.js"],
        "useless": [".gitignore"],
        "control": [".git"]
    }
    with open(".codeforge.json", "w") as f:
        json.dump(analysis, f, indent=4)
    print("Analysis saved to .codeforge.json")

def call_general_ai(prompt, config):
    print("Calling general AI model with prompt:")
    print(prompt)
    # Placeholder: integrate with ollama CLI and python ollama library

def call_code_ai(prompt):
    print("Calling code AI model with prompt:")
    print(prompt)
    # Placeholder: integrate with ollama CLI and python ollama library

def execute_changes(changes):
    print("Executing changes:")
    print(changes)
    # Placeholder: process JSON output and update files accordingly

def process_prompt(user_prompt):
    config_path = os.path.join(os.path.expanduser("~"), "codeforgeai.json")
    config = load_config(config_path)
    combined_prompt = " ".join(user_prompt)
    call_general_ai(combined_prompt, config)
    # For demonstration, using dummy responses
    general_response = "{}"
    call_code_ai(general_response)
    code_response = "{}"
    execute_changes(code_response)


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
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    loglevel = args.loglevel if args.loglevel is not None else logging.WARNING
    setup_logging(loglevel)
    _logger.debug("Starting CodeforgeAI...")

    # Ensure config exists in home directory
    config_path = os.path.join(os.path.expanduser("~"), "codeforgeai.json")
    load_config(config_path)

    if args.command == "analyze":
        analyze_working_directory()
    elif args.command == "prompt":
        process_prompt(args.user_prompt)
    else:
        print("No valid command provided. Use 'analyze' or 'prompt'.")


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
