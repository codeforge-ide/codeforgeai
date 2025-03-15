import logging
from ollama import chat, ChatResponse
import os

class CodeModel:
    def __init__(self, model_name="ollama_code"):
        self.model_name = model_name
        self._last_config_check = 0

    def send_request(self, prompt):
        # Check if we need to reload the configuration
        config_path = os.path.expanduser("~/.codeforgeai.json")
        
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
