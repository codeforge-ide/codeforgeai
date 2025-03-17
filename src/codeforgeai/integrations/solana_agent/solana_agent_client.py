import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union

_logger = logging.getLogger(__name__)

class SolanaAgentClient:
    """Lightweight Solana Agent integration client for CodeForgeAI."""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """Initialize the Solana Agent client.
        
        Args:
            base_url: The base URL for the Solana Agent server (default: http://localhost:3000)
        """
        self.base_url = base_url
        _logger.debug(f"Initializing Solana Agent client with base URL: {base_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the Solana Agent server.
        
        Args:
            method: HTTP method to use (GET, POST, etc.)
            endpoint: API endpoint to call
            data: Optional data to send with the request
            
        Returns:
            Response from the API as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f"Error making request to Solana Agent: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict:
        """Get the status of the Solana Agent.
        
        Returns:
            Dictionary with agent status
        """
        return self._make_request("GET", "/status")
    
    def get_balance(self, address: Optional[str] = None) -> Dict:
        """Get SOL balance for an address.
        
        Args:
            address: Optional Solana address (uses agent's address if None)
            
        Returns:
            Balance information
        """
        params = {}
        if address:
            params["address"] = address
        return self._make_request("GET", "/balance", params)
    
    def transfer_sol(self, destination: str, amount: float, memo: Optional[str] = None) -> Dict:
        """Transfer SOL to a destination address.
        
        Args:
            destination: Destination wallet address
            amount: Amount of SOL to send
            memo: Optional memo to include
            
        Returns:
            Transaction information
        """
        data = {
            "destination": destination,
            "amount": amount
        }
        if memo:
            data["memo"] = memo
        
        return self._make_request("POST", "/transfer", data)
    
    def execute_mcp_action(self, program_id: str, action_type: str, params: Dict) -> Dict:
        """Execute a Solana MCP action.
        
        Args:
            program_id: The Solana program ID
            action_type: Type of action to perform
            params: Parameters for the action
            
        Returns:
            Result of the MCP action
        """
        data = {
            "program_id": program_id,
            "action_type": action_type,
            "params": params
        }
        return self._make_request("POST", "/mcp/execute", data)
    
    def read_mcp_state(self, program_id: str, account_address: str) -> Dict:
        """Read state from a Solana MCP.
        
        Args:
            program_id: The Solana program ID
            account_address: The account address to read from
            
        Returns:
            Account state data
        """
        data = {
            "program_id": program_id,
            "account_address": account_address
        }
        return self._make_request("POST", "/mcp/read", data)
    
    def create_mcp_account(self, program_id: str, space: int, params: Optional[Dict] = None) -> Dict:
        """Create a new account for a Solana MCP.
        
        Args:
            program_id: The Solana program ID
            space: Space to allocate for the account (bytes)
            params: Additional parameters for account creation
            
        Returns:
            New account information
        """
        data = {
            "program_id": program_id,
            "space": space
        }
        if params:
            data["params"] = params
        
        return self._make_request("POST", "/mcp/create-account", data)


def is_solana_agent_available(base_url: str = "http://localhost:3000") -> bool:
    """Check if the Solana Agent is available.
    
    Args:
        base_url: The base URL for the Solana Agent server
        
    Returns:
        True if the Solana Agent is available, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/status", timeout=3)
        return response.status_code == 200
    except Exception:
        return False
