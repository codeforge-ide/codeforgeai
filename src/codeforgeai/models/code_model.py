import logging
from ollama import chat, ChatResponse  # updated import

class CodeModel:
    def __init__(self, model_name="ollama_code"):
        self.model_name = model_name

    def send_request(self, prompt):
        logging.debug("CodeModel: Sending prompt: %s", prompt)
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        logging.debug("CodeModel: Received response: %s", response.message.content)
        return response.message.content
