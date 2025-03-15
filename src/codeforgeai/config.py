import os
import json

def create_default_config(config_path):
    default_config = {
        "general_model": "tinyllama",
        "general_prompt": "based on the below prompt and without returning anything else, restructure it so that it is strictly understandable to a coding ai agent with json output for file changes:",
        "code_model": "qwen2.5-coder:0.5b",
        "code_prompt": "in very clear, concise manner, solve the below request:",
        "directory_classification_prompt": "Given the complete tree structure below as valid JSON, recursively process every single file and directory (based on its relative path) that is present. For each node, assign exactly one classification: 'useful' for files and directories that developers interact with, 'useless' for build, template, or temporary files and directories, and 'source' for source control or related files. For every node, return an object with the keys: 'type' (either 'file' or 'directory'), 'name', 'contents' (an array of child entries for directories, or file details for files), and a new key 'classification' that holds one of 'useful', 'useless', or 'source'. Ensure every file and directory from the input is included exactly once with one classification. Return only valid JSON with this structure and nothing else.",
        "debug": False,
        "format_line_separator": 5,
        
        "gitmoji_prompt": "reply only with a single emoji character that best fits the below commit message, and nothing else.",

        "commit_message_prompt": "Generate a very short and very concise, one sentence commit message for these code changes, and nothng else. ",

        "edit_finetune_prompt": "edit this code according to the below prompt and return nothing but the edited code",
        "code_or_command": "reply with either code or command only; is the below request best satisfied with a code response or command response:",
        "command_agent_prompt": "one for each line and nothing else, return a list of commands that can be executed to achieve the below request, and nothing else:",
        "prompt_finetune_prompt": "in a clear and concise manner, rephrase the following prompt to be more understandable to a coding ai agent, return the rephrased prompt and nothing else",
        "language_classification_prompt": "in one word only, what programming language is used in this project tree structure",
        "readme_summary_prompt": "in one short sentence only, generate a concise summary of this text below, and nothing else",
        "specific_file_classification": "taking the path and content of this file and classify it into either only user code file or project code file or source control file",
        "improve_code_prompt": "given this block of code, improve the code generally and return nothing but the improved code:"
    }
    # Expand the user directory
    config_path = os.path.expanduser(config_path)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)
    return default_config

def load_config(config_path):
    """Load config from file or create with defaults if not exists"""
    config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        # Create basic structure
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        basic_config = {"general_model": "tinyllama", "code_model": "qwen2.5-coder:0.5b"}
        with open(config_path, "w") as f:
            json.dump(basic_config, f, indent=4)
        # Let ensure_config_prompts fill in the rest
        return ensure_config_prompts(config_path)
    
    # File exists, load it
    with open(config_path) as f:
        return json.load(f)

def ensure_config_prompts(config_path):
    """Ensure that all necessary prompt keys exist in the config.
    If a key is missing, append it with a default value.
    """
    # First load the current config (or create if not exists)
    config = load_config(config_path)
    
    # Get the defaults that should be present
    default_config = {
        # Move all these defaults from the hardcoded load_config function to here
        "general_model": "tinyllama",
        "general_prompt": "based on the below prompt and without returning anything else, restructure it so that it is strictly understandable to a coding ai agent with json output for file changes:",
        "code_model": "qwen2.5-coder:0.5b",
        "code_prompt": "in very clear, concise manner, solve the below request:",
        "directory_classification_prompt": "Given the complete tree structure below as valid JSON, recursively process every single file and directory (based on its relative path) that is present. For each node, assign exactly one classification: 'useful' for files and directories that developers interact with, 'useless' for build, template, or temporary files and directories, and 'source' for source control or related files. For every node, return an object with the keys: 'type' (either 'file' or 'directory'), 'name', 'contents' (an array of child entries for directories, or file details for files), and a new key 'classification' that holds one of 'useful', 'useless', or 'source'. Ensure every file and directory from the input is included exactly once with one classification. Return only valid JSON with this structure and nothing else.",
        "debug": False,
        "format_line_separator": 5,
        "gitmoji_prompt": "reply only with a single emoji character that best fits the below commit message, and nothing else.",
        "commit_message_prompt": "Generate a very short and very concise, one sentence commit message for these code changes, and nothng else. ",
        "entire_suggestion_prompt": "generate a very short and quick suggestion/completion for this code block, keeping the exact structure intact.",
        "edit_finetune_prompt": "edit this code according to the below prompt and return nothing but the edited code",
        "suggestion_prompt": "generate a very short and quick suggestion/completion for this code block",
        "code_or_command": "reply with either code or command only; is the below request best satisfied with a code response or command response:",
        "command_agent_prompt": "one for each line and nothing else, return a list of commands that can be executed to achieve the below request, and nothing else:",
        "prompt_finetune_prompt": "in a clear and concise manner, rephrase the following prompt to be more understandable to a coding ai agent, return the rephrased prompt and nothing else",
        "language_classification_prompt": "in one word only, what programming language is used in this project tree structure",
        "readme_summary_prompt": "in one short sentence only, generate a concise summary of this text below, and nothing else",
        "specific_file_classification": "taking the path and content of this file and classify it into either only user code file or project code file or source control file",
        "improve_code_prompt": "given this block of code, improve the code generally and return nothing but the improved code:",
        "explain_code_prompt": "explain the following code in a clear and concise manner"
    }
    
    # Check if any defaults are missing and add them
    updated = False
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
            updated = True
    
    # Write back if changes were made
    if updated:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    
    return config
