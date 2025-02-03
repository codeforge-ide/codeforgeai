import ollama  # new import

class GeneralModel:
    def __init__(self, model_name="ollama_general"):
        self.model_name = model_name

    def send_request(self, prompt, config):
        print(f"Using {self.model_name} with prompt:")
        print(prompt)
        response = ollama.generate(model=self.model_name, prompt=prompt)  # integrated call
        return response
