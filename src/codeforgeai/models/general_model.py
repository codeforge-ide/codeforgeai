import logging
from ollama import chat, ChatResponse

class GeneralModel:
    def __init__(self, model_name="ollama_general"):
        self.model_name = model_name

    def send_request(self, prompt, config=None):
        logging.debug("GeneralModel: Sending prompt: %s", prompt)
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        logging.debug("GeneralModel: Received response: %s", response.message.content)
        return response.message.content
