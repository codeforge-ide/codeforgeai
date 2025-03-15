# setup

integration with codeforge and zerepy.














Skip to main content
ZerePy Logo
ZerePy
Documentation
Changelog
GitHub

Introduction
Installation Guide
Configuration Guide
Using ZerePy
Creating Custom Agents
Server Mode
Using ZerePy
Using ZerePy
This guide covers the main features and commands available in ZerePy.

Platform Capabilities
Social Platforms
Twitter/X Integration
Post tweets using AI-generated prompts
Read timeline with configurable count settings
Reply to tweets in your timeline
Like tweets in your timeline
Farcaster Features
Post new casts
Reply to existing casts
Like and requote casts
Read timeline content
Retrieve cast replies and threads
Discord Integration
Send messages to channels
React to messages
Read channel history
Manage server interactions
Handle direct messages
Manage roles and permissions
Echochambers Integration
Post new messages to rooms
Generate contextual replies
Read and analyze room history
Access room information and topics
Blockchain Features
Solana Integration
Send SOL transactions
Monitor wallet balance
Track transaction history
Interact with SPL tokens
Ethereum Integration
Send ETH transactions
Send ERC-20 tokens
Check wallet balances
Get token information
Get configured address
Execute token swaps
Support multiple EVM networks
Custom gas settings
Contract interactions
Sonic Integration
Send S transactions
Monitor wallet balance
Track transaction history
Interact with ERC-20 tokens
Execute token swaps on Sonic DEX
Custom slippage settings
Token lookup by ticker
GOAT Integration
Execute blockchain transactions with AI validation
Manage onchain wallets and assets
Interact with DeFi protocols:
Uniswap swaps and liquidity
Token transfers and approvals
Price checks via CoinGecko
Monitor market data through DexScreener
Support for multiple EVM networks
Transaction validation and risk assessment
AI/ML Features
XAI Language Model
128k context length support
Function calling capabilities
System prompt support
OpenAI/Anthropic SDK compatibility
Advanced language understanding
Context-aware responses
GOAT Features
AI-powered transaction validation
Risk assessment for DeFi operations
Market analysis using DexScreener data
Automated decision-making for:
Token swaps
Liquidity provision
Asset management
Context-aware transaction planning
Real-time price monitoring and alerts
Allora Integration
Access to decentralized inference models
Custom model selection
Inference parameter control
Chain-specific model deployment
LLM Integrations
Hyperbolic Features
Access to Meta-Llama models
Advanced text generation
Custom temperature settings
Token length control
Galadriel Features
OpenAI-compatible API interface
Support for verified model access
Optional fine-tuning capabilities
System prompt support
Custom model selection
Together AI Features
Multi-model access
Custom inference settings
Fine-tuning support
Optimized prompting
Adjustable context window
Groq Features
Ultra-fast inference
LLM-optimized performance
High scalability
Low-latency execution
AI Service Features
Perplexity Integration
Execute web searches with AI-powered reasoning
Access Perplexity's Sonar API for enhanced search capabilities
Example Usage:

# Perform a search query using Perplexity
agent-action perplexity search "What are the latest developments in AI technology?"


The search action supports:

Custom model selection (defaults to "sonar-reasoning-pro")
Detailed response generation with AI reasoning
Error handling for failed searches
CLI Command Reference
ZerePy provides a comprehensive set of CLI commands. Use help to see all available commands at any time.

Agent Management
list-agents - Display all available agents
load-agent - Load a specific agent for use
agent-loop - Start the agent's autonomous behavior
agent-action - Execute a single agent action
chat - Start an interactive chat session with the agent
Connection Management
list-connections - Show all available platform connections
list-actions - Display available actions for a specific connection
configure-connection - Set up a new platform connection
Additional Commands
help [command] - Get detailed help for a specific command
exit or quit - Exit the ZerePy CLI
clear or cls - Clear the terminal environment
Blockchain Commands
Common Commands (All Chains)
Check native token balance:
get-eth-balance (Ethereum)
get-sonic-balance (Sonic)
get-balance (Solana)
Get token data by ticker: get-token-by-ticker
Send native tokens:
send-eth (Ethereum)
send-sonic (Sonic)
transfer (Solana)
EVM Chain Commands (Ethereum & Sonic)
Send tokens:
send-eth-token (Ethereum)
send-sonic-token (Sonic)
Get wallet address: get-address
Chain-Specific Commands
Solana Only
trade - Swap tokens using Jupiter
stake - Stake SOL
get-tps - Get current network TPS
get-token-by-address - Get token data by address
Sonic Only
swap-sonic - Swap tokens on DEX with custom slippage control
Note: EVM chains (Ethereum and Sonic) follow similar command patterns, just replace "eth" with "sonic" in the command name. For example: send-eth-token on Ethereum becomes send-sonic-token on Sonic chain.

EVM Integration
Send native transactions (ETH/MATIC)
Send ERC-20 tokens
Check wallet balances
Get token information
Execute token swaps
Support multiple networks (Ethereum, Polygon)
Custom gas settings
Contract interactions
Example Usage Flows
Basic Usage Flow
Start ZerePy
Use list-connections to check available platforms
Configure required connections using configure-connection [platform]:
# LLM Providers
configure-connection [openai|anthropic|eternalai|xai|ollama|hyperbolic|together|groq]

# Social Platforms
configure-connection [twitter|farcaster|discord|echochambers]

# Blockchain
configure-connection [solana|evm|sonic]

# Additional Tools
configure-connection goat    # for onchain actions
configure-connection allora  # for inference


Load your agent with load-agent
Start autonomous behavior with agent-loop
Interactive Usage
Load your agent
Use chat to interact directly with the agent
Use agent-action to trigger specific behaviors
Monitoring
The agent will log its actions and thought process
Use Ctrl+C to safely stop the agent loop at any time
Check the console output for success/failure messages
Server Mode Features
RESTful API endpoints
Remote agent control
Status monitoring
Action execution
Connection management
Starting Server Mode
python main.py --server --host 0.0.0.0 --port 8000

Available Endpoints
GET / - Server status
GET /agents - List agents
POST /agents/{name}/load - Load agent
GET /connections - List connections
POST /agent/action - Execute action
Python Client Example
from src.server.client import ZerePyClient

client = ZerePyClient("http://localhost:8000")

# List available agents
agents = client.list_agents()

# Load an agent
client.load_agent("example")

# Execute an action
client.perform_action(
    connection="twitter",
    action="post-tweet",
    params={"text": "Hello from ZerePy!"}
)

Edit this page
Previous
Configuration Guide
Next
Creating Custom Agents
Platform Capabilities
Social Platforms
Blockchain Features
AI/ML Features
LLM Integrations
AI Service Features
CLI Command Reference
Agent Management
Connection Management
Additional Commands
Blockchain Commands
Example Usage Flows
Basic Usage Flow
Interactive Usage
Monitoring
Server Mode Features
Docs
Tutorial
Community
Discord
X
More
Blog
GitHub
Copyright © 2025 Blorm Inc.












































































