import os
import json
import subprocess
from codeforgeai.models.code_model import CodeModel
from codeforgeai.config import load_config

def analyze_directory():
    json_path = ".codeforge.json"
    
    # Run the tree command to get the directory structure in JSON format.
    try:
        tree_output = subprocess.check_output(["tree", "-J"], text=True)
    except Exception as e:
        print("Error running tree command:", e)
        tree_output = "{}"
    
    # Read existing classification from .codeforge.json if available.
    try:
        with open(json_path) as f:
            current_classification = json.load(f)
    except Exception:
        current_classification = {}
    
    combined_message = (
        f"Tree output:\n{tree_output}\n\n"
        f"Current classification:\n{json.dumps(current_classification, indent=2)}"
    )
    
    # Load configuration from the home directory (config path: ~/.codeforgeai.json).
    config_path = os.path.join(os.path.expanduser("~"), ".codeforgeai.json")
    config = load_config(config_path)
    
    # Get the directory classification prompt from config.
    directory_prompt = config.get(
        "directory_classification_prompt",
        "take this tree structure and help to better classify the files into actual useful user code files, useless template files and ignorable files, and source control files. return the classification in a json format like specified and return nothing else"
    )
    
    full_prompt = f"{directory_prompt}\n{combined_message}"
    
    # Retrieve the code model name from config and call the model via ollama.
    code_model_name = config.get("code_model", "ollama_code")
    code_model = CodeModel(code_model_name)
    classification_result = code_model.send_request(full_prompt)
    
    try:
        classification_json = json.loads(classification_result)
    except Exception as e:
        print("Error parsing classification result:", e)
        classification_json = current_classification
    
    # Update .codeforge.json with the refined classification.
    with open(json_path, "w") as f:
        json.dump(classification_json, f, indent=4)
    
    print("Updated classification saved to .codeforge.json")
