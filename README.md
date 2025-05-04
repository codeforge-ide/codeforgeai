# 🔧 CodeforgeAI

![CodeforgeAI](https://img.shields.io/badge/CodeforgeAI-v0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-orange)

## 🚀 Overview

CodeforgeAI is a powerful command-line developer tool that leverages AI to assist developers in their workflow. With a variety of commands and integration capabilities, it helps you analyze, generate, and improve code efficiently.

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Commands Overview](#-commands-overview)
- [Core Features](#-core-features)
- [AI Models & Integration](#-ai-models--integration)
- [Web3 Development Tools](#-web3-development-tools)
- [Solana MCP Integration](#-solana-mcp-integration)
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

### Step-by-Step Installation of package codeforgeai
To install CodeforgeAI, follow these steps:

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

## 🚀 Solana MCP Integration

CodeforgeAI now supports the revolutionary **Model Context Protocol (MCP)** paradigm for Solana blockchain development! MCPs represent the next evolution in blockchain programming.

### MCP Commands

Interact with Solana MCPs directly from the command line:

```bash
# Check Solana Agent status and configuration
codeforgeai solana status

# Check wallet balance
codeforgeai solana balance
codeforgeai solana balance --address <WALLET_ADDRESS>

# Send SOL transaction
codeforgeai solana transfer <DESTINATION_ADDRESS> <AMOUNT> --memo "Optional memo"

# Interact with an MCP
codeforgeai solana mcp interact <PROGRAM_ID> <ACTION_TYPE> --params '{"key": "value"}'

# Get MCP state
codeforgeai solana mcp state <PROGRAM_ID> <ACCOUNT_ADDRESS>

# Initialize MCP account
codeforgeai solana mcp init-account <PROGRAM_ID> <SPACE> --params '{"owner": true}'
```

### Python API for MCPs

Build MCP-powered applications using our Python API:

```python
from codeforgeai.integrations.solana_agent import SolanaAgentClient

# Initialize client
client = SolanaAgentClient()

# Check balance
balance = client.get_balance()
print(f"SOL Balance: {balance.get('balance')}")

# Interact with MCP
response = client.execute_mcp_action(
    program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    action_type="transfer",
    params={"destination": "8ZUczU...", "amount": 1000}
)

# Read MCP state
state = client.read_mcp_state(
    program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    account_address="8ZUczUAUZbMbRFL4JgKMS9sHxwZXBAZGG3WQ4MaQULKZ"
)

print(f"Token Balance: {state.get('state', {}).get('balance')}")
```

For more information, see the [Solana Agent MCP integration docs](src/codeforgeai/integrations/solana_agent/README.md).

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

## 🤖 GitHub Copilot Integration

CodeforgeAI now features robust, modular integration with GitHub Copilot via the Copilot Language Server Protocol (LSP). This enables advanced AI code completion, suggestions, and authentication directly from the CLI or any GUI/IDE that wraps the CLI.

### Copilot Subcommands

| Command | Description |
|---------|-------------|
| `github copilot lsp` | Install the Copilot language server globally (requires pnpm, yarn, or npm) |
| `github copilot login` | Authenticate with GitHub Copilot (opens browser for OAuth) |
| `github copilot logout` | Logout from GitHub Copilot |
| `github copilot status` | Check Copilot authentication and connection status |
| `github copilot inline-completion --file <file> --line <line> --character <character>` | Get inline code completion at a specific position |
| `github copilot panel-completion --file <file> --line <line> --character <character>` | Get panel (multi-line) code completion at a specific position |

#### Usage Examples (CLI)

```bash
# Install Copilot language server globally
codeforgeai github copilot lsp

# Authenticate with Copilot (follow browser instructions)
codeforgeai github copilot login

# Logout from Copilot
codeforgeai github copilot logout

# Check Copilot status
codeforgeai github copilot status

# Get inline completion for a file at line 10, character 5
codeforgeai github copilot inline-completion --file app.py --line 10 --character 5

# Get panel completion for a file at line 20, character 0
codeforgeai github copilot panel-completion --file main.py --line 20 --character 0
```

#### Usage in IDEs/GUI

- Any IDE or GUI that can call these CLI subcommands can leverage Copilot's AI completions and authentication.
- For Flutter or Electron-based GUIs, simply invoke the relevant subcommand and parse the output for completions or status.
- The Copilot LSP client is modular and can be imported in Python for direct integration in custom tools.

#### Programmatic Usage (Python)

```python
from codeforgeai.integrations.github_copilot import copilot

# Authenticate with Copilot
copilot.copilot_login()

# Get inline completion
result = copilot.CopilotLSPClient().inline_completion('app.py', 10, 5)
print(result)
```

> **Note:** The Copilot LSP integration is fully modular and can be extended for advanced IDE features, such as real-time completions, document sync, and more.