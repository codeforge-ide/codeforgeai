import os
import logging
from typing import List, Dict, Any, Optional, Union
import json

# Import Secret AI SDK
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret

_logger = logging.getLogger(__name__)

class SecretAIModel:
    """Secret AI model integration for CodeForgeAI."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize Secret AI model integration.
        
        Args:
            api_key: Secret AI API key (defaults to CLAIVE_AI_API_KEY env var)
            model_name: Optional model name to use (defaults to first available)
        """
        self.api_key = api_key or os.environ.get("CLAIVE_AI_API_KEY")
        if not self.api_key:
            _logger.warning("No Secret AI API key found. Set CLAIVE_AI_API_KEY env var.")
        
        self.secret_client = Secret()
        self.available_models = self._get_available_models()
        self.model_name = model_name or (self.available_models[0] if self.available_models else None)
        self.llm = self._initialize_llm() if self.model_name else None
    
    def _get_available_models(self) -> List[str]:
        """Get available Secret AI models."""
        try:
            return self.secret_client.get_models()
        except Exception as e:
            _logger.error(f"Failed to retrieve Secret AI models: {e}")
            return []
    
    def _initialize_llm(self) -> Optional[ChatSecret]:
        """Initialize the Secret AI LLM with the selected model."""
        if not self.model_name:
            return None
            
        try:
            urls = self.secret_client.get_urls(model=self.model_name)
            if not urls:
                _logger.error(f"No URLs available for model {self.model_name}")
                return None
                
            return ChatSecret(
                base_url=urls[0],
                model=self.model_name,
                temperature=1.0
            )
        except Exception as e:
            _logger.error(f"Failed to initialize Secret AI LLM: {e}")
            return None
    
    def send_request(self, prompt: str) -> str:
        """Send a request to the Secret AI model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response as a string
        """
        if not self.llm:
            return "Error: Secret AI LLM not initialized. Check your API key and available models."
            
        try:
            messages = [
                ("system", "You are a helpful AI assistant for a developer using CodeForgeAI."),
                ("human", prompt),
            ]
            response = self.llm.invoke(messages, stream=False)
            return response.content
        except Exception as e:
            _logger.error(f"Error calling Secret AI: {e}")
            return f"Error calling Secret AI: {e}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available Secret AI models.
        
        Returns:
            Dictionary with model information
        """
        models = self.available_models
        return {
            "available_models": models,
            "current_model": self.model_name,
            "has_api_key": bool(self.api_key)
        }

def list_secret_ai_models() -> List[str]:
    """List available Secret AI models.
    
    Returns:
        List of available model names
    """
    try:
        secret_client = Secret()
        return secret_client.get_models()
    except Exception as e:
        _logger.error(f"Error listing Secret AI models: {e}")
        return []

def get_web3_contract_analysis(contract_address: str, chain_id: str) -> str:
    """Analyze a web3 smart contract using Secret AI.
    
    Args:
        contract_address: Ethereum contract address
        chain_id: Chain ID for the contract
        
    Returns:
        Analysis of the contract
    """
    model = SecretAIModel()
    if not model.llm:
        return "Error: Could not initialize Secret AI model."
        
    prompt = f"""Analyze the smart contract at address {contract_address} on chain {chain_id}.
    Provide information about:
    - Contract purpose
    - Key functions
    - Security considerations
    - Gas optimization opportunities
    """
    
    return model.send_request(prompt)

def generate_web3_boilerplate(project_type: str) -> Dict[str, str]:
    """Generate web3 boilerplate code using Secret AI.
    
    Args:
        project_type: Type of project (e.g., 'dapp', 'smart-contract', 'token')
        
    Returns:
        Dictionary of file paths and their content
    """
    model = SecretAIModel()
    if not model.llm:
        return {"error": "Could not initialize Secret AI model."}
    
    prompt = f"""Generate boilerplate code for a {project_type} web3 project.
    Include:
    - Main smart contract(s)
    - Deployment script
    - Basic frontend interaction (if applicable)
    - README with setup instructions
    
    Format the response as a JSON object with file paths as keys and file content as values.
    """
    
    response = model.send_request(prompt)
    try:
        # Try to parse JSON from the response
        # This might need refinement depending on how the model formats responses
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx >= 0 and end_idx > 0:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        return {"error": "Could not parse JSON from model response", "response": response}
    except Exception as e:
        return {"error": str(e), "response": response}
