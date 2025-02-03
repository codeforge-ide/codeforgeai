class CodeModel:
    def __init__(self, model_name="ollama_code"):
        self.model_name = model_name

    def send_request(self, prompt):
        print(f"Using {self.model_name} with prompt:")
        print(prompt)
        # Placeholder: Integrate with ollama CLI and python ollama library
        return "{}"  # Dummy JSON output
