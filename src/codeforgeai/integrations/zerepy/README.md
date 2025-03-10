# ZerePy Integration for CodeForgeAI

This integration provides a lightweight client for interacting with ZerePy servers from within CodeForgeAI.

## Features

- Connect to a running ZerePy server
- List available agents
- Load specific agents
- List available connections
- Execute actions on connections
- Send chat messages to agents

## Usage

```python
from codeforgeai.integrations.zerepy.zerepy_integration import ZerePyClient

# Initialize client
client = ZerePyClient("http://localhost:8000")

# Check server status
status = client.server_status()
print(f"Server status: {status}")

# List available agents
agents = client.list_agents()
print(f"Available agents: {agents}")

# Load an agent
response = client.load_agent("example")
print(f"Load agent response: {response}")

# Execute an action
result = client.perform_action(
    connection="twitter",
    action="post-tweet",
    params={"text": "Hello from CodeForgeAI!"}
)
print(f"Action result: {result}")

# Chat with the agent
response = client.chat("Tell me about your capabilities")
print(f"Agent response: {response}")
```

## Helper Functions

The integration also provides helper functions for common tasks:

```python
from codeforgeai.integrations.zerepy.zerepy_integration import is_zerepy_available, execute_zerepy_action

# Check if ZerePy server is available
if is_zerepy_available():
    # Execute an action
    result = execute_zerepy_action(
        connection="openai",
        action="generate-text",
        params={
            "prompt": "Write a short story about AI",
            "system_prompt": "You are a creative writer",
            "model": "gpt-3.5-turbo"
        }
    )
    print(result)
else:
    print("ZerePy server is not available")
```

## Requirements

- ZerePy server running and accessible
- `requests` library installed
