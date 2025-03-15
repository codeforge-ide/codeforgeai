import logging
from ollama import chat, ChatResponse
import os
from codeforgeai.config import load_config  # Add this import statement

class CodeModel:
    def __init__(self, model_name="ollama_code"):
        self.model_name = model_name

    def send_request(self, prompt):
        # Load config to get the latest model name
        config_path = os.path.expanduser("~/.codeforgeai.json")
        config = load_config(config_path)
        
        # If config is provided, use the model name from the config
        if config and config.get("code_model"):
            self.model_name = config["code_model"]
        
        logging.debug(f"CodeModel: Using model: {self.model_name}")
        logging.debug("CodeModel: Sending prompt: %s", prompt)
        
        try:
            response: ChatResponse = chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            logging.debug("CodeModel: Received response: %s", response.message.content)
            return response.message.content
        except Exception as e:
            logging.error(f"Error with model {self.model_name}: {e}")
            return f"Error: {str(e)}"
