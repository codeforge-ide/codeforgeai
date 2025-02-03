import os
import json

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
