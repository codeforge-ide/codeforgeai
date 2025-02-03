import os
import json
import subprocess
import logging  # new import
from codeforgeai.models.code_model import CodeModel
from codeforgeai.config import load_config

def analyze_directory():
    json_path = ".codeforge.json"
    
    # Run the tree command to get the directory structure in JSON format.
    try:
        tree_output = subprocess.check_output(["tree", "-J"], text=True)
        logging.debug("Directory Analyzer: Tree output: %s", tree_output)
    except Exception as e:
        logging.error("Error running tree command: %s", e)
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
    directory_prompt = config["directory_classification_prompt"]
    
    full_prompt = f"{directory_prompt}\n{combined_message}"
    logging.debug("Directory Analyzer: Full prompt to code model: %s", full_prompt)
    
    # Retrieve the code model name from config and call the model via ollama.
    code_model_name = config.get("code_model", "ollama_code")
    code_model = CodeModel(code_model_name)
    classification_result = code_model.send_request(full_prompt)
    logging.debug("Directory Analyzer: Classification result: %s", classification_result)
    
    # Check if the response is empty or whitespace.
    if not classification_result.strip():
        logging.debug("Received empty response from code model; falling back to current classification.")
        classification_json = current_classification
    else:
        try:
            # Remove markdown code block markers if present.
            result = classification_result.strip()
            if result.startswith("```json"):
                result = result[len("```json"):].strip()
                if result.endswith("```"):
                    result = result[:-3].strip()
            classification_json = json.loads(result)
        except Exception as e:
            logging.error("Error parsing classification result: %s", e)
            classification_json = current_classification
    
    # Update .codeforge.json with the refined classification.
    with open(json_path, "w") as f:
        json.dump(classification_json, f, indent=4)
    
    logging.debug("Directory Analyzer: Updated classification saved to .codeforge.json")
    print("Updated classification saved to .codeforge.json")
