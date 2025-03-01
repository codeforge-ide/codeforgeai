import os
import logging
from typing import List, Dict, Any, Optional
import json

# Import Secret AI SDK
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret

_logger = logging.getLogger(__name__)

class SecretAIModel:
    """Secret AI model integration for CodeForgeAI."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.environ.get("CLAIVE_AI_API_KEY")
        if not self.api_key:
            _logger.warning("No Secret AI API key found. Set CLAIVE_AI_API_KEY env var.")
        
        self.secret_client = Secret()
        self.available_models = self._get_available_models()
        self.model_name = model_name or (self.available_models[0] if self.available_models else None)
        self.llm = self._initialize_llm() if self.model_name else None
    
    def _get_available_models(self) -> List[str]:
        try:
            return self.secret_client.get_models()
        except Exception as e:
            _logger.error(f"Failed to retrieve Secret AI models: {e}")
            return []
    
    def _initialize_llm(self) -> Optional[ChatSecret]:
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
        models = self.available_models
        return {
            "available_models": models,
            "current_model": self.model_name,
            "has_api_key": bool(self.api_key)
        }

def list_secret_ai_models() -> List[str]:
    try:
        secret_client = Secret()
        return secret_client.get_models()
    except Exception as e:
        _logger.error(f"Error listing Secret AI models: {e}")
        return []
