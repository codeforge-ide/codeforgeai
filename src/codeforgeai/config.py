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
    if not os.path.exists(config_path):
        return create_default_config(config_path)
    with open(config_path) as f:
        return json.load(f)
