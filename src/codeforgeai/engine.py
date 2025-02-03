import os
import json
from codeforgeai.config import load_config
from codeforgeai.directory import analyze_directory
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.models.code_model import CodeModel
from codeforgeai.file_manager import apply_changes

class Engine:
    def __init__(self):
        home = os.path.expanduser("~")
        # Updated config path to use a leading dot
        self.config_path = os.path.join(home, ".codeforgeai.json")
        self.config = load_config(self.config_path)
        self.general_model = GeneralModel(self.config.get("general_model", "ollama_general"))
        self.code_model = CodeModel(self.config.get("code_model", "ollama_code"))

    def run_analysis(self):
        analyze_directory()

    def process_prompt(self, user_prompt):
        raw_prompt = " ".join(user_prompt)
        general_catalyst = self.config.get("general_prompt", "")
        full_general_prompt = f"{general_catalyst}\n{raw_prompt}"
        general_response = self.general_model.send_request(full_general_prompt, self.config)
        code_catalyst = self.config.get("code_prompt", "")
        full_code_prompt = f"{code_catalyst}\n{general_response}"
        code_response = self.code_model.send_request(full_code_prompt)
        apply_changes(code_response)
