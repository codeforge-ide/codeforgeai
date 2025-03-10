import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union

_logger = logging.getLogger(__name__)

class ZerePyClient:
    """Lightweight ZerePy integration client for CodeForgeAI."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the ZerePy client.
        
        Args:
            base_url: The base URL for the ZerePy server (default: http://localhost:8000)
        """
        self.base_url = base_url
        _logger.debug(f"Initializing ZerePy client with base URL: {base_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the ZerePy server.
        
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
            _logger.error(f"Error making request to ZerePy server: {e}")
            return {"error": str(e)}
    
    def server_status(self) -> Dict:
        """Check the status of the ZerePy server.
        
        Returns:
            Server status information
        """
        return self._make_request("GET", "/")
    
    def list_agents(self) -> List[str]:
        """List available agents.
        
        Returns:
            List of available agent names
        """
        response = self._make_request("GET", "/agents")
        return response.get("agents", [])
    
    def load_agent(self, agent_name: str) -> Dict:
        """Load a specific agent.
        
        Args:
            agent_name: Name of the agent to load
            
        Returns:
            Response indicating success or failure
        """
        return self._make_request("POST", f"/agents/{agent_name}/load")
    
    def list_connections(self) -> Dict:
        """List available connections.
        
        Returns:
            Dictionary of available connections
        """
        return self._make_request("GET", "/connections")
    
    def perform_action(self, connection: str, action: str, params: Dict) -> Dict:
        """Execute an action on a specific connection.
        
        Args:
            connection: Name of the connection
            action: Name of the action to perform
            params: Parameters for the action
            
        Returns:
            Result of the action execution
        """
        data = {
            "connection": connection,
            "action": action,
            "params": params
        }
        return self._make_request("POST", "/agent/action", data)
    
    def chat(self, message: str) -> str:
        """Send a chat message to the agent.
        
        Args:
            message: Message to send
            
        Returns:
            Response from the agent
        """
        data = {"message": message}
        response = self._make_request("POST", "/agent/chat", data)
        return response.get("response", "")


def is_zerepy_available() -> bool:
    """Check if ZerePy server is available.
    
    Returns:
        True if ZerePy server is available, False otherwise
    """
    try:
        client = ZerePyClient()
        status = client.server_status()
        return "error" not in status
    except Exception:
        return False


def execute_zerepy_action(connection: str, action: str, params: Dict) -> Dict:
    """Helper function to execute a ZerePy action.
    
    Args:
        connection: Name of the connection (e.g., 'twitter', 'openai')
        action: Name of the action to perform
        params: Parameters for the action
        
    Returns:
        Result of the action execution
    """
    try:
        client = ZerePyClient()
        return client.perform_action(connection, action, params)
    except Exception as e:
        _logger.error(f"Failed to execute ZerePy action: {e}")
        return {"error": str(e)}
