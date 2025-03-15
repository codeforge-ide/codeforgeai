import logging
from ollama import chat, ChatResponse
import os

class GeneralModel:
    def __init__(self, model_name="ollama_general"):
        self.model_name = model_name
        self._last_config_check = 0

    def send_request(self, prompt, config=None):
        # If config is provided, check if we need to use a different model
        if config and "general_model" in config:
            self.model_name = config.get("general_model")
            
        logging.debug(f"GeneralModel: Using model: {self.model_name}")
        logging.debug("GeneralModel: Sending prompt: %s", prompt)
        
        try:
            response: ChatResponse = chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            logging.debug("GeneralModel: Received response: %s", response.message.content)
            return response.message.content
        except Exception as e:
            logging.error(f"Error with model {self.model_name}: {e}")
            return f"Error: {str(e)}"
