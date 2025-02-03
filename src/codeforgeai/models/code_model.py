import ollama  # new import

class CodeModel:
    def __init__(self, model_name="ollama_code"):
        self.model_name = model_name

    def send_request(self, prompt):
        print(f"Using {self.model_name} with prompt:")
        print(prompt)
        response = ollama.generate(model=self.model_name, prompt=prompt)  # integrated call
        return response
