import os
import json
import logging
import re
import random
import subprocess
from codeforgeai.config import load_config
from codeforgeai.directory import analyze_directory, loop_analyze_directory
from codeforgeai.models.general_model import GeneralModel
from codeforgeai.models.code_model import CodeModel
from codeforgeai.file_manager import apply_changes


# define engine class.
class Engine:
    def __init__(self):
        # Use the config file from the user's home directory
        self.config_path = os.path.expanduser("~/.codeforgeai.json")
        # Always load fresh config directly from the file
        self._refresh_config()
        
    def _refresh_config(self):
        """Reload config from file to ensure we have the latest values"""
        try:
            from codeforgeai.config import load_config  # Ensure load_config is defined locally
            self.config = load_config(self.config_path)
            # Reinitialize models with fresh config values
            self.general_model = GeneralModel(self.config.get("general_model", "ollama_general"))  # Provide default
            self.code_model = CodeModel(self.config.get("code_model", "ollama_code"))  # Provide default
            return self.config
        except Exception as e:
            print(f"Error refreshing config: {e}")
            # Initialize with default models in case of error
            self.config = {}
            self.general_model = GeneralModel()
            self.code_model = CodeModel()
            return {}

    def run_analysis(self):
        self._refresh_config()  # Refresh config before operation
        analyze_directory()

    def run_analysis_loop(self):
        self._refresh_config()  # Refresh config before operation
        print("Starting adaptive feedback loop for directory analysis (Ctrl+C to stop).")
        loop_analyze_directory()

    def process_prompt(self, user_prompt):
        self._refresh_config()  # Refresh config before operation
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
        final_response = self.general_model.send_request(full_code_prompt)
        
        return final_response

    def explain_code(self, file_path):
        self._refresh_config()  # Refresh config before operation
        explain_prompt = self.config.get("explain_code_prompt", "explain the following code in a clear and concise manner")
        
        with open(file_path, "r") as file:
            file_content = file.read()
        
        prompt = f"{explain_prompt}\n\nFile: {file_path}\n\n{file_content}"
        response = self.code_model.send_request(prompt)
        return response

    def generate_commit_message(self, commit_msg):
        """
        Generate a commit message by prepending an emoji based on message content.
        Uses random selection of emojis from gitmoji list.
        """
        try:
            with open(os.path.expanduser("~/.gitmoji/gitmojis.json"), "r", encoding="utf-8") as f:
                gitmojis = json.load(f)
        except Exception as e:
            logging.error(f"Error loading gitmojis.json: {e}")
            return commit_msg

        # The original "intelligent" emoji selection logic is commented out below
        """
        # Extract words from commit message
        msg_words = set(re.findall(r'\w+', commit_msg.lower()))
        
        # Find best matching emoji by comparing words
        best_match = None
        best_score = 0
        
        for item in gitmojis:
            desc = item.get("description", "").lower()
            desc_words = set(re.findall(r'\w+', desc))
            
            # Count shared words
            shared_words = msg_words & desc_words
            score = len(shared_words)
            
            if score > best_score:
                best_score = score
                best_match = item

        # Get emoji character
        if best_match and best_score > 0:
            emoji = best_match.get("emoji", "")
        elif gitmojis:
            # Random emoji if no good match found
            emoji = random.choice(gitmojis).get("emoji", "")
        else:
            emoji = ""
        """

        # New logic: Simply pick a random emoji from the list
        emoji = random.choice(gitmojis).get("emoji", "") if gitmojis else ""

        return f"{emoji} {commit_msg}"

    def process_commit_message(self):
        """Quickly generate a one-sentence commit message with an emoji using only the general model."""
        self._refresh_config()  # Refresh config before operation
        try:
            diff = subprocess.check_output(
                ["git", "diff", "--name-status", "--cached"],
                text=True,
                stderr=subprocess.PIPE
            ).strip()
            if not diff:
                diff = subprocess.check_output(
                    ["git", "diff", "--name-status", "HEAD"],
                    text=True,
                    stderr=subprocess.PIPE
                ).strip()
            if not diff:
                # Check untracked files if no diff found
                untracked = subprocess.check_output(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    text=True,
                    stderr=subprocess.PIPE
                ).strip()
                if untracked:
                    diff = "Untracked files:\n" + untracked
            if not diff:
                return self.generate_commit_message("No changes found")
            commit_message_prompt = self.config.get(
                "commit_message_prompt",
                "Generate a very short and very concise, one sentence commit message for these code changes:"
            )

            # Pass the config to code_model.send_request to ensure it uses the configured values
            full_msg = self.code_model.send_request(f"{commit_message_prompt}\n{diff}", self.config).strip()
            # Extract first sentence only.
            first_sentence = full_msg.split('.')[0].strip()
            if first_sentence and not first_sentence.endswith('.'):
                first_sentence += '.'
            return self.generate_commit_message(first_sentence)
        except Exception as e:
            logging.error(f"Error generating commit message: {e}")
            return self.generate_commit_message("Update code changes")
