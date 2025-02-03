import os
import json
import subprocess
import logging
import time
from codeforgeai.models.code_model import CodeModel
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.config import load_config

def analyze_directory():
    json_path = ".codeforge.json"
    
    try:
        # Run tree in current working directory
        tree_output = subprocess.check_output(
            ["tree", "-J"], text=True, cwd=os.getcwd()
        )
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
    ignored_paths = parse_gitignore()  # robust patterns
    # Convert JSON tree to data
    try:
        tree_data = json.loads(tree_output)
    except:
        tree_data = []
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
    Reads .gitignore in the current working directory. 
    Returns a list of patterns that can be directories or files.
    """
    patterns = []
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, encoding="utf-8", errors="ignore") as g:
                for line in g:
                    line = line.strip()
                    # Ignore comments or empty lines
                    if not line or line.startswith("#"):
                        continue
                    patterns.append(line)
        except Exception as e:
            logging.error("Error reading .gitignore: %s", e)
    return patterns


def remove_ignored(tree_json, ignored_patterns):
    """
    Remove items from tree data matching .gitignore patterns.
    - If pattern is a directory name or ends with '/', ignore that directory recursively.
    - If pattern is a file name or wildcard, ignore matching file(s).
    """
    if isinstance(tree_json, list):
        result = []
        for item in tree_json:
            filtered = remove_ignored(item, ignored_patterns)
            if filtered is not None:
                result.append(filtered)
        return result
    elif isinstance(tree_json, dict):
        name = tree_json.get("name", "")
        typ = tree_json.get("type", "")
        # Check if item is ignored based on patterns
        if is_ignored(name, typ, ignored_patterns):
            return None
        if typ == "directory":
            contents = tree_json.get("contents", [])
            new_contents = remove_ignored(contents, ignored_patterns)
            tree_json["contents"] = new_contents
        return tree_json
    return tree_json


def is_ignored(name, node_type, patterns):
    """
    Helper to decide if a file/directory matches any pattern in the .gitignore list.
    """
    for pat in patterns:
        if pat.endswith("/"):
            # Directory pattern
            if node_type == "directory" and name == pat.rstrip("/"):
                return True
        else:
            # File pattern or direct name
            # Very basic matching:
            if name == pat:
                return True
            if pat.startswith("*") and name.endswith(pat.lstrip("*")):
                return True
    return False


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


def loop_analyze_directory():
    file_mod_times = {}
    while True:
        # 1. Refresh classification
        try:
            analyze_directory()
        except Exception as e:
            logging.error("Error during analyze_directory: %s", e)

        # 2. Load .codeforge.json robustly
        try:
            with open(".codeforge.json") as f:
                classification = json.load(f)
        except Exception as e:
            logging.error("Error loading .codeforge.json: %s", e)
            classification = {}

        updated = False
        file_class_map = classification.get("file_classification", {})
        keys_to_remove = []

        # 3. Iterate over classified files to check modifications and correct paths
        for fpath in list(file_class_map.keys()):
            # Ensure file path is relative to current working directory
            rel_path = os.path.relpath(fpath, os.getcwd())
            if rel_path != fpath:
                file_class_map[rel_path] = file_class_map.pop(fpath)
                fpath = rel_path
                updated = True
            try:
                if os.path.exists(fpath):
                    mtime = os.path.getmtime(fpath)
                    if fpath not in file_mod_times:
                        file_mod_times[fpath] = mtime
                    elif mtime != file_mod_times[fpath]:
                        # Files with frequent edits are reclassified as user code
                        file_class_map[fpath] = "user code file"
                        file_mod_times[fpath] = mtime
                        updated = True
                else:
                    logging.warning("File not found; removing classification for: %s", fpath)
                    keys_to_remove.append(fpath)
                    updated = True
            except Exception as e:
                logging.error("Error checking file %s: %s", fpath, e)

        for key in keys_to_remove:
            file_class_map.pop(key, None)

        # 4. Scan for new files not yet classified; mark them as "unclassified"
        try:
            for root, _, files in os.walk("."):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_full = os.path.relpath(full_path, os.getcwd())
                    if rel_full not in file_class_map:
                        file_class_map[rel_full] = "unclassified"
                        updated = True
        except Exception as e:
            logging.error("Error scanning for new files: %s", e)

        if updated:
            classification["file_classification"] = file_class_map
            try:
                with open(".codeforge.json", "w") as fw:
                    json.dump(classification, fw, indent=4)
                logging.debug("Updated .codeforge.json with new classifications.")
            except Exception as e:
                logging.error("Error writing updated .codeforge.json: %s", e)

        print("Feedback loop iteration complete. Press Ctrl+C to exit.")
        time.sleep(5)
