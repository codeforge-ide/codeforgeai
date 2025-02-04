import os
import json
import logging
import re            # <-- Added import
import random        # <-- Added import
from codeforgeai.config import load_config
from codeforgeai.directory import analyze_directory, loop_analyze_directory
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.models.code_model import CodeModel
from codeforgeai.file_manager import apply_changes

class Engine:
    def __init__(self):
        # Use the config file from the user's home directory
        self.config_path = os.path.expanduser("~/.codeforgeai.json")
        self.config = load_config(self.config_path)
        self.general_model = GeneralModel(self.config.get("general_model"))
        self.code_model = CodeModel(self.config.get("code_model"))

    def run_analysis(self):
        analyze_directory()

    def run_analysis_loop(self):
        print("Starting adaptive feedback loop for directory analysis (Ctrl+C to stop).")
        loop_analyze_directory()

    def process_prompt(self, user_prompt):
        raw_prompt = " ".join(user_prompt)
        finetune_catalyst = self.config.get(
            "prompt_finetune_prompt",
            "in a clear and concise manner, rephrase the following prompt to be more understandable to a coding ai agent, return the rephrased prompt and nothing else:"
        )
        full_finetune_prompt = f"{finetune_catalyst}\n{raw_prompt}"
        finetuned_response = self.general_model.send_request(full_finetune_prompt, self.config)
        
        if not finetuned_response:
            finetuned_response = raw_prompt
            
        code_prompt = self.config.get("code_prompt", "")
        full_code_prompt = f"{code_prompt}\n{finetuned_response}"
        final_response = self.code_model.send_request(full_code_prompt)
        
        return final_response

    def explain_code(self, file_path):
        explain_prompt = self.config.get("explain_code_prompt", "explain the following code in a clear and concise manner")
        
        with open(file_path, "r") as file:
            file_content = file.read()
        
        prompt = f"{explain_prompt}\n\nFile: {file_path}\n\n{file_content}"
        response = self.code_model.send_request(prompt)
        return response

    # ---- New Commit-Message Methods ----
    def generate_commit_message(self, commit_msg):
        """
        Generate a commit message by prepending an emoji.
        Loads gitmoji definitions from /home/nathfavour/.gitmoji/gitmojis.json and selects
        an emoji based on matching words from the commit message. If no match is found, selects randomly.
        """
        try:
            with open("/home/nathfavour/.gitmoji/gitmojis.json", "r", encoding="utf-8") as f:
                gitmojis = json.load(f)
        except Exception:
            gitmojis = []
        # Process words in commit message
        words = re.findall(r'\w+', commit_msg.lower())
        best_match = None
        best_count = 0
        for item in gitmojis:
            desc = item.get("description", "").lower()
            desc_words = re.findall(r'\w+', desc)
            count = sum(1 for w in desc_words if w in words)
            if count > best_count:
                best_count = count
                best_match = item
        if best_match and best_count > 0:
            emoji_char = best_match.get("emoji", "")
        elif gitmojis:
            emoji_char = random.choice(gitmojis).get("emoji", "")
        else:
            emoji_char = ""
        return f"{emoji_char} {commit_msg}"

    def process_commit_message(self):
        """
        Process commit message generation.
        Uses the commit_message_prompt from config to request a commit message from the code model,
        then generates the final commit message using generate_commit_message.
        """
        commit_prompt = self.config.get("commit_message_prompt", "Generate commit message:")
        commit_msg = self.code_model.send_request(commit_prompt)
        return self.generate_commit_message(commit_msg)
