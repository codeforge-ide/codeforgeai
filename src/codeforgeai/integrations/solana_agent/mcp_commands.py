import os
import json
import logging
from typing import Dict, Any, Optional
from codeforgeai.integrations.solana_agent.solana_agent_client import SolanaAgentClient, is_solana_agent_available

_logger = logging.getLogger(__name__)

def check_solana_agent_setup() -> Dict[str, Any]:
    """Check if Solana Agent is properly set up.
    
    Returns:
        Dictionary with setup information
    """
    result = {
        "available": is_solana_agent_available(),
        "env_vars": {
            "SOLANA_RPC_URL": bool(os.environ.get("SOLANA_RPC_URL")),
            "SOLANA_PRIVATE_KEY": bool(os.environ.get("SOLANA_PRIVATE_KEY")),
        }
    }
    
    if result["available"]:
        try:
            client = SolanaAgentClient()
            status = client.get_status()
            result["status"] = status
        except Exception as e:
            _logger.error(f"Error getting Solana Agent status: {e}")
            result["error"] = str(e)
    
    return result

def get_wallet_balance(address: Optional[str] = None) -> Dict[str, Any]:
    """Get the wallet balance.
    
    Args:
        address: Optional address to check balance for
        
    Returns:
        Dictionary with balance information
    """
    if not is_solana_agent_available():
        return {"error": "Solana Agent not available"}
    
    try:
        client = SolanaAgentClient()
        return client.get_balance(address)
    except Exception as e:
        _logger.error(f"Error getting wallet balance: {e}")
        return {"error": str(e)}

def send_transaction(destination: str, amount: float, memo: Optional[str] = None) -> Dict[str, Any]:
    """Send SOL to a destination address.
    
    Args:
        destination: Destination wallet address
        amount: Amount of SOL to send
        memo: Optional memo
        
    Returns:
        Dictionary with transaction information
    """
    if not is_solana_agent_available():
        return {"error": "Solana Agent not available"}
    
    try:
        client = SolanaAgentClient()
        return client.transfer_sol(destination, amount, memo)
    except Exception as e:
        _logger.error(f"Error sending transaction: {e}")
        return {"error": str(e)}

def interact_with_mcp(program_id: str, action_type: str, params: Dict) -> Dict[str, Any]:
    """Interact with a Solana MCP.
    
    Args:
        program_id: The Solana program ID
        action_type: Type of action to perform
        params: Parameters for the action
        
    Returns:
        Dictionary with result information
    """
    if not is_solana_agent_available():
        return {"error": "Solana Agent not available"}
    
    try:
        client = SolanaAgentClient()
        return client.execute_mcp_action(program_id, action_type, params)
    except Exception as e:
        _logger.error(f"Error interacting with MCP: {e}")
        return {"error": str(e)}

def get_mcp_state(program_id: str, account_address: str) -> Dict[str, Any]:
    """Get state from a Solana MCP.
    
    Args:
        program_id: The Solana program ID
        account_address: The account address to read from
        
    Returns:
        Dictionary with account state
    """
    if not is_solana_agent_available():
        return {"error": "Solana Agent not available"}
    
    try:
        client = SolanaAgentClient()
        return client.read_mcp_state(program_id, account_address)
    except Exception as e:
        _logger.error(f"Error getting MCP state: {e}")
        return {"error": str(e)}

def init_mcp_account(program_id: str, space: int, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Initialize a new account for a Solana MCP.
    
    Args:
        program_id: The Solana program ID
        space: Space to allocate for the account (bytes)
        params: Additional parameters
        
    Returns:
        Dictionary with account information
    """
    if not is_solana_agent_available():
        return {"error": "Solana Agent not available"}
    
    try:
        client = SolanaAgentClient()
        return client.create_mcp_account(program_id, space, params)
    except Exception as e:
        _logger.error(f"Error initializing MCP account: {e}")
        return {"error": str(e)}
