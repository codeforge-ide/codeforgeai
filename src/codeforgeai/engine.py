import os
import json
import logging  # new import
from codeforgeai.config import load_config
from codeforgeai.directory import analyze_directory, loop_analyze_directory
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

    def run_analysis_loop(self):
        print("Starting adaptive feedback loop for directory analysis (Ctrl+C to stop).")
        loop_analyze_directory()

    def process_prompt(self, user_prompt):
        raw_prompt = " ".join(user_prompt)
        finetune_catalyst = self.config.get("prompt_finetune_prompt", "in a clear and concise manner, rephrase the following prompt to be more understandable to a coding ai agent, return the rephrased prompt and nothing else:")
        full_finetune_prompt = f"{finetune_catalyst}\n{raw_prompt}"
        finetuned_response = self.general_model.send_request(full_finetune_prompt, self.config)
        logging.debug("Engine: Finetuned response: %s", finetuned_response)
        
        code_catalyst = self.config.get("code_prompt", "")
        full_code_prompt = f"{code_catalyst}\n{finetuned_response}"
        code_response = self.code_model.send_request(full_code_prompt)
        logging.debug("Engine: Code response: %s", code_response)
        apply_changes(code_response)

    def explain_code(self, file_path):
        explain_prompt = self.config.get("explain_code_prompt", "explain the following code in a clear and concise manner")
        
        with open(file_path, "r") as file:
            file_content = file.read()
        
        prompt = f"{explain_prompt}\n\nFile: {file_path}\n\n{file_content}"
        response = self.code_model.send_request(prompt)
        return response
