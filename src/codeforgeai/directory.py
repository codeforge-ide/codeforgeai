import os
import json
import subprocess
import logging
from codeforgeai.models.code_model import CodeModel
from codeforgeai.models.general_model import GeneralModel
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
    
    # 1. Prompt AI model for the project’s primary language; store result in .codeforge.json
    language_classification_prompt = config.get(
        "language_classification_prompt",
        "in one word only, what programming language is used in this project tree structure"
    )
    code_model_name = config.get("code_model", "ollama_code")
    code_model = CodeModel(code_model_name)
    language_result = code_model.send_request(f"{language_classification_prompt}\n{tree_output}")
    logging.debug("Directory Analyzer: Language result: %s", language_result)
    language_result_clean = language_result.strip().replace("```", "")
    current_classification["language"] = language_result_clean

    # 2. Detect any 'src' directory and store the relative path in .codeforge.json
    src_path = None
    try:
        # Parse tree_output (JSON) to find a "name": "src"
        tree_data = json.loads(tree_output)
        src_path = find_src_path(tree_data)
        if src_path:
            current_classification["src_directory"] = src_path
        else:
            current_classification["src_directory"] = None
    except Exception as e:
        logging.error("Error finding src path: %s", e)

    # 3. If a README file is found at top-level, read and call general AI
    readme_prompt = config.get(
        "readme_summary_prompt",
        "in one short sentence only, generate a concise summary of this text below, and nothing else"
    )
    readme_path = locate_readme()
    if readme_path:
        try:
            with open(readme_path, encoding="utf-8", errors="ignore") as rf:
                readme_content = rf.read()
            general_model_name = config.get("general_model", "ollama_general")
            general_model = GeneralModel(general_model_name)
            summary_result = general_model.send_request(f"{readme_prompt}\n{readme_content}", config)
            logging.debug("Directory Analyzer: README summary: %s", summary_result)
            current_classification["short_description"] = summary_result.strip().replace("```", "")
        except Exception as e:
            logging.error("Error reading or summarizing README: %s", e)

    # 4. Run git remote -v to get repo info
    remote_info = None
    try:
        remote_output = subprocess.check_output(["git", "remote", "-v"], text=True).strip()
        if remote_output:
            lines = remote_output.splitlines()
            if lines:
                remote_info = lines[0]
    except Exception as e:
        logging.error("Error running git remote -v: %s", e)
    current_classification["repository"] = remote_info if remote_info else "Unknown"

    # 5. Run git config user.name
    author_name = None
    try:
        author_name = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
    except Exception as e:
        logging.error("Error running git config user.name: %s", e)
    current_classification["author"] = author_name if author_name else "Unknown"

    # 6. Run git config user.email
    author_email = None
    try:
        author_email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
    except Exception as e:
        logging.error("Error running git config user.email: %s", e)
    current_classification["author_email"] = author_email if author_email else "Unknown"

    # 7. Parse .gitignore to exclude those files from the tree output, then classify remaining files
    ignored_paths = parse_gitignore()
    adjusted_tree_data = remove_ignored(tree_data, ignored_paths)
    specific_file_classification_prompt = config.get(
        "specific_file_classification",
        "taking the path and content of this file and classify it into either only user code file or project code file or source control file"
    )
    file_classification_data = classify_files(adjusted_tree_data, code_model, specific_file_classification_prompt)
    current_classification["file_classification"] = file_classification_data

    classification_json = current_classification

    # Update .codeforge.json with the refined classification.
    with open(json_path, "w") as f:
        json.dump(classification_json, f, indent=4)
    
    logging.debug("Directory Analyzer: Updated classification saved to .codeforge.json")
    print("Updated classification saved to .codeforge.json")


def find_src_path(tree_json):
    """
    Recursively searches for an item with {'type': 'directory', 'name': 'src'}
    and returns a relative path if found, else None.
    """
    if isinstance(tree_json, list):
        # top-level might be a list with one directory object
        for item in tree_json:
            result = find_src_path(item)
            if result:
                return result
    elif isinstance(tree_json, dict):
        if tree_json.get("type") == "directory":
            name = tree_json.get("name", "")
            if name == "src":
                return "./src"
            contents = tree_json.get("contents", [])
            for c in contents:
                sub = find_src_path(c)
                if sub:
                    # Return path with directory name prefix
                    return os.path.join(f"./{name}", sub)
    return None


def locate_readme():
    """
    Attempts to locate a README file in the working directory (top-level).
    Prioritizes README.md or README.rst or "README" in any case variant.
    """
    candidates = ["README.md", "README.rst", "README"]
    for f in os.listdir("."):
        lower_name = f.lower()
        if lower_name in [c.lower() for c in candidates]:
            return os.path.join(".", f)
    return None


def parse_gitignore():
    """
    Reads .gitignore from the working directory (if present) and returns a list
    of patterns to ignore.
    """
    patterns = []
    if os.path.exists(".gitignore"):
        try:
            with open(".gitignore", encoding="utf-8", errors="ignore") as g:
                for line in g:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            logging.error("Error reading .gitignore: %s", e)
    return patterns


def remove_ignored(tree_json, ignored_patterns):
    """
    Remove items from the tree data that match any pattern in ignored_patterns.
    Very simple check: if file name or directory name in patterns, remove it.
    """
    if isinstance(tree_json, list):
        filtered = []
        for item in tree_json:
            fi = remove_ignored(item, ignored_patterns)
            if fi is not None:
                filtered.append(fi)
        return filtered
    elif isinstance(tree_json, dict):
        name = tree_json.get("name", "")
        # Check if this file/dir is ignored directly
        if any(name == pat for pat in ignored_patterns):
            return None
        if tree_json.get("type") == "directory":
            contents = tree_json.get("contents", [])
            new_contents = remove_ignored(contents, ignored_patterns)
            tree_json["contents"] = new_contents
            return tree_json
        else:
            return tree_json
    return tree_json


def classify_files(tree_data, code_model, prompt):
    """
    Recursively classify each file that remains in tree_data after ignoring. 
    For each file, read its content, call code_model with 'prompt + file content + path', 
    and store classification results in a dictionary like { path: classification }.
    """
    file_class_map = {}
    _classify_walk(tree_data, code_model, prompt, file_class_map, base_path=".")
    return file_class_map


def _classify_walk(node, code_model, prompt, file_class_map, base_path):
    if isinstance(node, dict):
        if node.get("type") == "file":
            fname = node["name"]
            fullpath = os.path.join(base_path, fname)
            # Attempt to read content
            content = ""
            try:
                with open(fullpath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                pass
            # Construct final prompt
            final_prompt = f"{prompt}\nFile path: {fullpath}\nFile content:\n{content}"
            logging.debug("File Classification Prompt: %s", final_prompt[:500])
            result = code_model.send_request(final_prompt)
            classification = result.strip().replace("```", "")
            file_class_map[fullpath] = classification
        elif node.get("type") == "directory":
            dname = node["name"]
            contents = node.get("contents", [])
            new_base = os.path.join(base_path, dname)
            for c in contents:
                _classify_walk(c, code_model, prompt, file_class_map, new_base)
    elif isinstance(node, list):
        for item in node:
            _classify_walk(item, code_model, prompt, file_class_map, base_path)
