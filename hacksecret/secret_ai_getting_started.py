from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret

secret_client = Secret()
# Get all the models registered with the smart contracts
models = secret_client.get_models()
# For the chosen model you may obtain a list of LLM instance URLs to connect to
urls = secret_client.get_urls(model=models[0])
# You previosly exported the env var CLAIVE_AI_API_KEY=YOUR-API-KEY
secret_ai_llm = ChatSecret(
base_url=urls[0], # in this case we choose to access the first url in the list

model=models[0], # your selected model

temperature=1.
)
# Define your messages you want to send to the confidential LLM for processing
messages = [
(
      "system",
      "You are my therapist. Help me with my issues.",
),
("human", "I miss my cat."),
]
# Invoke the llm
response = secret_ai_llm.invoke(messages, stream=False)
print(response.content)