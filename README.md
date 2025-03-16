# 🔧 CodeforgeAI

![CodeforgeAI](https://img.shields.io/badge/CodeforgeAI-v0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## 🚀 Overview

CodeforgeAI is a powerful command-line tool that leverages AI to assist developers in their workflow. With a variety of commands and integration capabilities, it helps you analyze, generate, and improve code efficiently.

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Commands Overview](#-commands-overview)
- [Core Features](#-core-features)
- [AI Models & Integration](#-ai-models--integration)
- [Web3 Development Tools](#-web3-development-tools)
- [Vyper Smart Contract Development](#-vyper-smart-contract-development)
- [Advanced Usage](#-advanced-usage)
- [Contributing](#-contributing)
- [License](#-license)
- [Integrations](#-integrations)

## 🔌 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Ollama (for local AI models)



### Step-by-Step Installation

1. **Clone the repository:**

```bash
git clone https://github.com/codeforge-ide/codeforgeai.git
cd codeforgeai
```

2. **Install the package in development mode:**

```bash
pip install -e .
```

This command installs the package in "editable" mode, which means changes to the source code will be immediately reflected without needing to reinstall.

3. **Verify installation:**

```bash
codeforgeai --help
```

You should see the help message with available commands.

## ⚙️ Configuration

CodeforgeAI uses a configuration file stored at `~/.codeforgeai.json`. The first time you run a command, this file will be created with default settings.

### View Current Configuration

```bash
codeforgeai config
```

### Key Configuration Options

- `general_model`: The AI model for general prompts (default: "tinyllama")
- `code_model`: The AI model for code-specific tasks (default: "qwen2.5-coder:0.5b")
- `format_line_separator`: Number of newlines between extracted code blocks (default: 5)

You can manually edit the config file to customize these settings.

## 📜 Commands Overview

CodeforgeAI offers a rich set of commands for various development tasks:

### Basic Commands

| Command | Description |
|---------|-------------|
| `analyze` | Analyze the current working directory |
| `prompt` | Process a user prompt with AI |
| `config` | Run configuration checkup |
| `strip` | Print tree structure after removing gitignored files |
| `explain` | Explain code in a given file |
| `edit` | Edit code in specified files or folders |
| `extract` | Extract code blocks from file or string |
| `format` | Format code blocks for readability |
| `command` | Process a command request |
| `suggestion` | Get quick code suggestions |
| `commit-message` | Generate a commit message with gitmoji |

### Secret AI Integration

| Command | Description |
|---------|-------------|
| `secret-ai list-models` | List available Secret AI models |
| `secret-ai test-connection` | Test Secret AI connection |
| `secret-ai chat` | Chat with Secret AI |

### Web3 Development

| Command | Description |
|---------|-------------|
| `web3 scaffold` | Scaffold a new web3 project |
| `web3 analyze-contract` | Analyze a smart contract |
| `web3 estimate-gas` | Estimate gas costs for a smart contract |
| `web3 generate-tests` | Generate tests for a smart contract |
| `web3 check-env` | Check web3 development environment |
| `web3 install-deps` | Install web3 dependencies |

### Vyper Smart Contracts

| Command | Description |
|---------|-------------|
| `vyper compile` | Compile a Vyper smart contract |
| `vyper analyze` | Analyze a Vyper smart contract |
| `vyper check` | Check if Vyper is installed |

## 🔍 Core Features

### 🔄 Project Analysis

Analyze your entire project structure and understand its composition:

```bash
codeforgeai analyze
```

This will examine your project and create a `.codeforge.json` file with metadata about your codebase.

For continuous monitoring, use:

```bash
codeforgeai analyze --loop
```

### 💬 AI Prompting

Get AI assistance for coding tasks:

```bash
codeforgeai prompt "Create a function to calculate Fibonacci numbers"
```

### 📝 Code Explanation

Get explanations for code in a file:

```bash
codeforgeai explain path/to/file.py
```

### ✏️ Code Editing

Edit files according to a prompt:

```bash
codeforgeai edit src/ --user_prompt "Add error handling to all functions"
```

To include directories that might be gitignored:

```bash
codeforgeai edit build/ --user_prompt "Fix deprecated API calls" --allow-ignore
```

### 💡 Code Suggestions

Get quick code suggestions:

```bash
# For a specific line in a file
codeforgeai suggestion --file app.py --line 42

# For the entire file
codeforgeai suggestion --file app.py --entire

# For a code snippet
codeforgeai suggestion --string "def factorial(n):"
```

### 📊 Git Integration

Generate commit messages automatically:

```bash
codeforgeai commit-message
```

## 🧠 AI Models & Integration

CodeforgeAI works with various AI models:

### Local Models (via Ollama)

By default, CodeforgeAI uses local models through Ollama:
- `tinyllama` for general prompts
- `qwen2.5-coder:0.5b` for code-specific tasks

### Secret AI SDK Integration

For advanced capabilities, CodeforgeAI integrates with Secret AI:

```bash
# Set your API key
export CLAIVE_AI_API_KEY=your_api_key_here

# Test connection
codeforgeai secret-ai test-connection

# List available models
codeforgeai secret-ai list-models

# Chat with Secret AI
codeforgeai secret-ai chat "How do I implement WebSockets in Node.js?"
```

## ⛓️ Web3 Development Tools

CodeforgeAI includes specialized tools for Web3 development:

### Scaffold Projects

```bash
# Create a basic dApp
codeforgeai web3 scaffold my-dapp

# Create an NFT project
codeforgeai web3 scaffold my-nft --type nft

# Create a token project in a specific directory
codeforgeai web3 scaffold my-token --type token --output ~/projects
```

### Smart Contract Analysis

```bash
codeforgeai web3 analyze-contract contracts/Token.sol
```

### Gas Estimation

```bash
codeforgeai web3 estimate-gas contracts/Token.sol
```

### Test Generation

```bash
codeforgeai web3 generate-tests contracts/Token.sol --output tests/
```

### Environment Check

```bash
codeforgeai web3 check-env
```

### Install Dependencies

```bash
# Minimal dependencies
codeforgeai web3 install-deps

# Full development environment
codeforgeai web3 install-deps --full
```

## 🐍 Vyper Smart Contract Development

CodeforgeAI includes specialized tools for building smart contracts using the Vyper language:

### Check Vyper Installation

Check if the Vyper compiler is installed on your system:

```bash
codeforgeai vyper check
```

### Compile Vyper Contracts

Compile a Vyper smart contract:

```bash
# Basic compilation (outputs ABI by default)
codeforgeai vyper compile contracts/SimpleAuction.vy

# Compile to get bytecode
codeforgeai vyper compile contracts/SimpleAuction.vy -f bytecode

# Compile with optimization for gas efficiency
codeforgeai vyper compile contracts/SimpleAuction.vy --optimize gas

# Compile for specific EVM version
codeforgeai vyper compile contracts/SimpleAuction.vy --evm-version paris
```

### Analyze Vyper Contracts

Analyze a Vyper contract for features and patterns:

```bash
codeforgeai vyper analyze contracts/SimpleAuction.vy
```

This will detect common contract types like auctions, tokens, voting systems, and crowdfunding contracts based on the code patterns found in the examples.

### Vyper Contract Examples

The tool comes with several example Vyper contracts demonstrating common patterns:

- Simple open auction
- Blind auction
- Safe remote purchases
- Crowdfunding
- Voting systems
- Company stock management

These examples show Vyper's focus on security and simplicity in smart contract development.

## 🔄 Advanced Usage

### Command Processing

Determine if a request should be handled as code or terminal commands:

```bash
codeforgeai command "set up a React project with TypeScript"
```

### Code Format Processing

Extract code blocks from files or strings:

```bash
codeforgeai extract --file response.md
```

Format code blocks for better readability:

```bash
codeforgeai format --file extracted_code.txt
```

### Directory Structure Analysis

View your project structure without gitignored files:

```bash
codeforgeai strip
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Thanks to all contributors and users of CodeforgeAI
- [Ollama](https://github.com/ollama/ollama) for local AI model support
- [Secret AI SDK](https://docs.scrt.network/secret-network-documentation/claive-ai/introduction) for advanced AI capabilities
- The open-source community for inspiration and tools

## Integrations

### ZerePy Integration

CodeForgeAI includes a lightweight integration with ZerePy, allowing you to interact with ZerePy agents and services directly from your CodeForgeAI workflows.

With this integration, you can:

- Connect to ZerePy servers
- List and load ZerePy agents
- Execute agent actions
- Interact with ZerePy connections (Twitter, OpenAI, Ethereum, etc.)
- Send chat messages to agents

To use the ZerePy integration:

```python
from codeforgeai.integrations.zerepy.zerepy_integration import ZerePyClient

# Initialize client
client = ZerePyClient()

# List available agents
agents = client.list_agents()

# Load an agent
client.load_agent("example")

# Execute an action
client.perform_action(
    connection="openai",
    action="generate-text",
    params={
        "prompt": "Write documentation for my code",
        "system_prompt": "You are a technical writer",
        "model": "gpt-4"
    }
)
```

For more details, see the [ZerePy integration documentation](src/codeforgeai/integrations/zerepy/README.md).
