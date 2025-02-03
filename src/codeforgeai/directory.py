import os
import json

def analyze_directory():
    # Dummy function: In a real-world scenario, classify files by .gitignore etc.
    analysis = {
        "useful": ["file1.py", "file2.js"],
        "useless": [".gitignore"],
        "control": [".git"]
    }
    with open(".codeforge.json", "w") as f:
        json.dump(analysis, f, indent=4)
    print("Directory analysis saved to .codeforge.json")
