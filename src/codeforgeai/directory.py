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

def strip_directory(return_data=False):
    """Get tree structure with clean relative paths, no gitignored files."""
    try:
        tree_output = subprocess.check_output(
            ["tree", "-J"], text=True, cwd=os.getcwd()
        )
        tree_data = json.loads(tree_output)
    except Exception as e:
        logging.error("Error running tree command: %s", e)
        return [] if return_data else None

    def clean_path(path):
        """Convert path to pure relative form (a/b/c)."""
        return os.path.normpath(path).lstrip("./")

    def filter_tree(node, parent=""):
        if isinstance(node, list):
            return [f for f in (filter_tree(item, parent) for item in node) if f]
        
        if isinstance(node, dict):
            name = node.get("name", "")
            path = os.path.join(parent, name) if parent else name
            clean = clean_path(path)
            
            if should_ignore(clean, parse_gitignore()):
                return None
            
            node["name"] = clean
            if node.get("type") == "directory":
                contents = node.get("contents", [])
                node["contents"] = filter_tree(contents, clean)
            return node
        return node

    filtered_tree = filter_tree(tree_data)
    if return_data:
        return filtered_tree
    print(json.dumps(filtered_tree, indent=4))

def analyze_directory():
    """Analyze directory using stripped tree data."""
    json_path = ".codeforge.json"
    config_path = os.path.join(os.path.expanduser("~"), ".codeforgeai.json")
    config = load_config(config_path)
    
    # Get stripped tree data
    stripped_data = strip_directory(return_data=True)
    
    # Initialize or load existing classification
    try:
        with open(json_path) as f:
            classification = json.load(f)
    except:
        classification = {}
    
    def collect_files(node, files=None):
        """Get all file paths from stripped tree."""
        if files is None:
            files = []
        if isinstance(node, list):
            for item in node:
                collect_files(item, files)
        elif isinstance(node, dict):
            if node.get("type") == "file":
                files.append(node["name"])
            elif node.get("type") == "directory":
                for child in node.get("contents", []):
                    collect_files(child, files)
        return files

    # Get all files from stripped tree
    all_files = collect_files(stripped_data)
    
    # Initialize file classifications if not present
    if "file_classification" not in classification:
        classification["file_classification"] = {}
    
    # Classify each file individually
    code_model = CodeModel(config.get("code_model", "ollama_code"))
    specific_prompt = config.get("specific_file_classification")
    
    for filepath in all_files:
        if filepath not in classification["file_classification"]:
            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                prompt = f"{specific_prompt}\nFile path: {filepath}\nContent:\n{content}"
                result = code_model.send_request(prompt).strip()
                classification["file_classification"][filepath] = result
                # Save after each classification
                with open(json_path, "w") as f:
                    json.dump(classification, f, indent=4)
            except Exception as e:
                logging.error(f"Error classifying {filepath}: {e}")
    
    # Update other metadata
    classification["src_directory"] = "src" if os.path.exists("src") else None
    classification["language"] = "Python"  # From tree analysis
    # ...rest of metadata updates (author, etc)...
    
    with open(json_path, "w") as f:
        json.dump(classification, f, indent=4)

def loop_analyze_directory():
    """Run analyze_directory periodically, checking for changes."""
    config = load_config(os.path.join(os.path.expanduser("~"), ".codeforgeai.json"))
    interval = config.get("analyze_interval", 5)  # Default 5 seconds
    
    while True:
        try:
            # Get current files
            current_files = set(collect_files(strip_directory(return_data=True)))
            
            # Get classified files
            try:
                with open(".codeforge.json") as f:
                    classification = json.load(f)
                classified_files = set(classification.get("file_classification", {}).keys())
            except:
                classified_files = set()
            
            # If there are differences, run analysis
            if current_files != classified_files:
                analyze_directory()
            
            time.sleep(interval)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error in analysis loop: {e}")
            time.sleep(interval)

def collect_files(node, files=None):
    """Helper to get all file paths from tree structure."""
    if files is None:
        files = []
    if isinstance(node, list):
        for item in node:
            collect_files(item, files)
    elif isinstance(node, dict):
        if node.get("type") == "file":
            files.append(node["name"])
        elif node.get("type") == "directory":
            for child in node.get("contents", []):
                collect_files(child, files)
    return files

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
