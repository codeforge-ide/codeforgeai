import os
import json

def create_default_config(config_path):
    default_config = {
        "general_model": "ollama_general",
        "general_prompt": "based on the below prompt and without returning anything else, restructure it so that it is strictly understandable to a coding ai agent with json output for file changes:",
        "code_model": "ollama_code",
        "code_prompt": "in very clear, concise manner, solve the below request:",
        "directory_classification_prompt": "take this tree structure and help to better classify the files into actual useful user code files, useless template files and ignorable files, and source control files. return the classification in a json format like specified and return nothing else",
        "debug": False  # default debug flag
    }
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)
    return default_config

def load_config(config_path):
    default_config = {
        "general_model": "ollama_general",
        "general_prompt": "based on the below prompt and without returning anything else, restructure it so that it is strictly understandable to a coding ai agent with json output for file changes:",
        "code_model": "ollama_code",
        "code_prompt": "in very clear, concise manner, solve the below request:",
        "directory_classification_prompt": "take this tree structure and help to better classify the files into actual useful user code files, useless template files and ignorable files, and source control files. return the classification in a json format like specified and return nothing else",
        "debug": False
    }
    if not os.path.exists(config_path):
        return create_default_config(config_path)
    with open(config_path) as f:
        config = json.load(f)
    updated = False
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
            updated = True
    if updated:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    return config

def ensure_config_prompts(config_path):
    """Ensure that all necessary prompt keys exist in the config.
    If a key is missing, append it with a default value.
    """
    additional_defaults = {
        "language_classification_prompt": "in one word only, what programming language is used in this project tree structure",
        "readme_summary_prompt": "in one short sentence only, generate a concise summary of this text below, and nothing else",
        "specific_file_classification": "taking the path and content of this file and classify it into either only user code file or project code file or source control file"
    }
    config = load_config(config_path)
    updated = False
    for key, value in additional_defaults.items():
        if key not in config:
            config[key] = value
            updated = True
    if updated:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    return config
