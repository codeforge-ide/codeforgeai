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
        self.config_path = os.path.join(home, "codeforgeai.json")
        self.config = load_config(self.config_path)
        self.general_model = GeneralModel(self.config.get("general_model", "ollama_general"))
        self.code_model = CodeModel(self.config.get("code_model", "ollama_code"))

    def run_analysis(self):
        analyze_directory()

    def process_prompt(self, user_prompt):
        prompt_text = " ".join(user_prompt)
        general_response = self.general_model.send_request(prompt_text, self.config)
        code_response = self.code_model.send_request(general_response)
        apply_changes(code_response)
