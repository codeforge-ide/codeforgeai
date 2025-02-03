import os
import json
import subprocess
import logging
import time
import fnmatch
from pathlib import Path
from codeforgeai.models.code_model import CodeModel
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.config import load_config

def parse_gitignore():
    """Robust .gitignore parsing that handles all pattern types."""
    patterns = []
    gitignore = os.path.join(os.getcwd(), '.gitignore')
    if os.path.exists(gitignore):
        with open(gitignore, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle directory patterns
                    if line.endswith('/'):
                        patterns.append(line[:-1])  # Remove trailing slash
                    # Handle file patterns
                    else:
                        patterns.append(line)
    return patterns

def should_ignore(path, patterns):
    """
    Check if a path matches any gitignore pattern.
    Handles both files and directories properly.
    """
    path = os.path.normpath(path)
    is_dir = os.path.isdir(path)

    for pattern in patterns:
        # Directory-specific matching
        if pattern.endswith('/'):
            if is_dir and (fnmatch.fnmatch(path, pattern[:-1]) or 
                          any(fnmatch.fnmatch(part, pattern[:-1]) 
                              for part in path.split(os.sep))):
                return True
        # File pattern matching
        else:
            if fnmatch.fnmatch(path, pattern) or \
               any(fnmatch.fnmatch(part, pattern) 
                   for part in path.split(os.sep)):
                return True
            # Handle *.ext patterns
            if pattern.startswith('*'):
                if path.endswith(pattern[1:]):
                    return True
    return False

def get_relative_path(path):
    """Convert any path to be relative to current working directory."""
    try:
        return os.path.relpath(path, os.getcwd())
    except ValueError:
        return path

def analyze_directory():
    json_path = ".codeforge.json"
    ignored_patterns = parse_gitignore()
    
    try:
        # Run tree in current working directory
        tree_output = subprocess.check_output(
            ["tree", "-J", "--gitignore"], 
            text=True, 
            cwd=os.getcwd()
        )
        tree_data = json.loads(tree_output)
    except Exception as e:
        logging.error("Error running tree command: %s", e)
        tree_data = []

    # Early gitignore filtering
    def filter_tree(node, parent="."):
        if isinstance(node, list):
            return [n for n in node if n is not None]
        
        if isinstance(node, dict):
            path = os.path.join(parent, node.get("name", ""))
            rel_path = get_relative_path(path)
            
            if should_ignore(rel_path, ignored_patterns):
                return None
            
            if node.get("type") == "directory":
                filtered_contents = []
                for child in node.get("contents", []):
                    filtered = filter_tree(child, path)
                    if filtered is not None:
                        filtered_contents.append(filtered)
                node["contents"] = filtered_contents
            return node
        return node

    filtered_tree = filter_tree(tree_data)

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
        src_path = find_src_path(filtered_tree)
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
    adjusted_tree_data = remove_ignored(tree_data, ignored_paths, parent=".")
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


def remove_ignored(tree_json, ignored_patterns, parent="."):
    """
    Remove items from tree data matching .gitignore patterns.
    - If pattern is a directory name or ends with '/', ignore that directory recursively.
    - If pattern is a file name or wildcard, ignore matching file(s).
    """
    if isinstance(tree_json, list):
        filtered = []
        for item in tree_json:
            r = remove_ignored(item, ignored_patterns, parent)
            if r is not None:
                filtered.append(r)
        return filtered
    elif isinstance(tree_json, dict):
        name = tree_json.get("name", "")
        typ = tree_json.get("type", "")
        full_path = os.path.join(parent, name)
        if is_ignored(full_path, typ, ignored_patterns):
            return None
        if typ == "directory":
            contents = tree_json.get("contents", [])
            tree_json["contents"] = remove_ignored(contents, ignored_patterns, full_path)
        return tree_json
    return tree_json


def is_ignored(full_path, node_type, patterns):
    """
    Check if full_path (relative to cwd) matches any pattern in .gitignore.
    """
    base_name = os.path.basename(full_path)
    for pat in patterns:
        # Directory pattern
        if pat.endswith("/"):
            if node_type == "directory" and base_name == pat.rstrip("/"):
                return True
            # If pattern is a subfolder wildcard, e.g. "build/" in "build/something"
            if pat.rstrip("/") in full_path and node_type == "directory":
                return True
        else:
            # Exact file match
            if base_name == pat:
                return True
            # Simple wildcard: "*something"
            if pat.startswith("*") and full_path.endswith(pat.lstrip("*")):
                return True
            # Pattern anywhere in path
            if pat in full_path:
                return True
    return False


def classify_files(tree_data, code_model, prompt):
    """Classify files with proper path handling."""
    file_class_map = {}
    ignored_patterns = parse_gitignore()

    def walk(node, parent="."):
        if isinstance(node, dict):
            name = node.get("name", "")
            path = os.path.join(parent, name)
            rel_path = get_relative_path(path)
            
            if should_ignore(rel_path, ignored_patterns):
                return

            if node.get("type") == "file":
                try:
                    with open(rel_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    final_prompt = f"{prompt}\nFile path: {rel_path}\nContent:\n{content}"
                    result = code_model.send_request(final_prompt)
                    file_class_map[rel_path] = result.strip().replace("```", "")
                except Exception as e:
                    logging.error(f"Error processing file {rel_path}: {e}")
            
            elif node.get("type") == "directory":
                for child in node.get("contents", []):
                    walk(child, path)

    for item in tree_data:
        walk(item)
    
    return file_class_map


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

def strip_directory():
    """
    Prints the tree structure after removing all files/directories matching .gitignore rules.
    """
    try:
        tree_output = subprocess.check_output(
            ["tree", "-J"],
            text=True,
            cwd=os.getcwd()
        )
        tree_data = json.loads(tree_output)
    except Exception as e:
        logging.error("Error running tree command: %s", e)
        return

    ignored_patterns = parse_gitignore()
    
    def filter_tree(node, parent="."):
        if isinstance(node, list):
            filtered = []
            for item in node:
                f = filter_tree(item, parent)
                if f is not None:
                    filtered.append(f)
            return filtered
        elif isinstance(node, dict):
            path = os.path.join(parent, node.get("name", ""))
            rel_path = get_relative_path(path)
            if should_ignore(rel_path, ignored_patterns):
                return None
            if node.get("type") == "directory":
                contents = node.get("contents", [])
                node["contents"] = filter_tree(contents, path)
            return node
        return node

    filtered_tree = filter_tree(tree_data)
    print(json.dumps(filtered_tree, indent=4))
