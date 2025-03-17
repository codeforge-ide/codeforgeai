# Solana Agent MCP Integration for CodeForgeAI

This integration provides a lightweight client for interacting with Solana blockchain and Message Compute Programs (MCPs) from within CodeForgeAI.

## What is MCP?

**Message Compute Program (MCP)** is a revolutionary paradigm for blockchain development on Solana. Unlike traditional smart contracts:

- **Message-Oriented**: MCPs focus on processing messages rather than managing state directly
- **Modular Architecture**: Encourages better separation of concerns and more maintainable code
- **Reduced Attack Surface**: By separating logic from state, security risks are minimized
- **Improved Performance**: More efficient execution model with optimized processing

MCPs represent the next evolution in blockchain programming, making Solana development more accessible and robust.

## Features

- Check Solana Agent status and configuration
- Get wallet balances
- Send SOL transactions
- Interact with MCPs (Message Compute Programs)
- Read MCP state
- Create new MCP accounts

## Usage

```bash
# Check Solana Agent status
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

## Python API

```python
from codeforgeai.integrations.solana_agent import SolanaAgentClient

# Initialize client
client = SolanaAgentClient()

# Check balance
balance = client.get_balance()
print(f"Balance: {balance.get('balance')} SOL")

# Send transaction
result = client.transfer_sol(
    destination="8ZUczUAUZbMbRFL4JgKMS9sHxwZXBAZGG3WQ4MaQULKZ",
    amount=0.01,
    memo="Payment for services"
)
print(f"Transaction ID: {result.get('signature')}")

# Interact with MCP
response = client.execute_mcp_action(
    program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    action_type="transfer",
    params={"destination": "8ZUczU...", "amount": 1000}
)
```

## Requirements

- Solana Agent running and accessible (default: http://localhost:3000)
- Environment variables:
  - SOLANA_RPC_URL: RPC endpoint for Solana network
  - SOLANA_PRIVATE_KEY: Private key for the agent wallet
