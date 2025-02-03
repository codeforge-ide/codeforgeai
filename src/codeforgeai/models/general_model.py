from ollama import chat, ChatResponse  # updated import

class GeneralModel:
    def __init__(self, model_name="ollama_general"):
        self.model_name = model_name

    def send_request(self, prompt, config):
        print(f"Using {self.model_name} with prompt:")
        print(prompt)
        response: ChatResponse = chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response.message.content
