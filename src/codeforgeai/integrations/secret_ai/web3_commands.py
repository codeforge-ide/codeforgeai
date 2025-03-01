import os
import json
import logging
from typing import Dict, Any, Optional
import subprocess

from codeforgeai.integrations.secret_ai.secret_ai_integration import SecretAIModel

_logger = logging.getLogger(__name__)

def scaffold_web3_project(project_name: str, project_type: str, output_dir: Optional[str] = None) -> str:
    if not output_dir:
        output_dir = os.getcwd()
        
    project_dir = os.path.join(output_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Generate project files using SecretAI
    model = SecretAIModel()
    if not model.llm:
        return "Error: Could not initialize Secret AI model."
    
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
        # Parse JSON from the response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx >= 0 and end_idx > 0:
            json_str = response[start_idx:end_idx]
            files = json.loads(json_str)
            
            # Write files to disk
            for file_path, content in files.items():
                full_path = os.path.join(project_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w") as f:
                    f.write(content)
                    
            return f"Web3 project created at {project_dir}"
        else:
            return f"Error: Could not parse AI response as JSON"
    except Exception as e:
        _logger.error(f"Error processing AI response: {e}")
        return f"Error creating project: {str(e)}"

def analyze_smart_contract(contract_file: str) -> str:
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return f"Error: Contract file {contract_file} not found"
        
    model = SecretAIModel()
    if not model.llm:
        return "Error: Could not initialize Secret AI model."
    
    prompt = f"""Analyze this smart contract code:
    
    ```solidity
    {contract_code}
    ```
    
    Provide:
    1. Security analysis - identify potential vulnerabilities
    2. Gas optimization suggestions
    3. Code quality assessment
    4. Architectural recommendations
    """
    
    return model.send_request(prompt)

def estimate_gas_costs(contract_file: str) -> str:
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return f"Error: Contract file {contract_file} not found"
        
    model = SecretAIModel()
    if not model.llm:
        return "Error: Could not initialize Secret AI model."
    
    prompt = f"""For the following smart contract, estimate gas costs for each function.
    Return the results as a formatted table.
    
    ```solidity
    {contract_code}
    ```
    """
    
    return model.send_request(prompt)

def generate_web3_tests(contract_file: str) -> Dict[str, str]:
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return {"error": f"Contract file {contract_file} not found"}
        
    model = SecretAIModel()
    if not model.llm:
        return {"error": "Could not initialize Secret AI model."}
    
    prompt = f"""Generate comprehensive test cases for the following smart contract.
    Use Hardhat and ethers.js for testing.
    Include tests for all public/external functions.
    
    ```solidity
    {contract_code}
    ```
    
    Format the response as a JSON object with test file paths as keys and test content as values.
    """
    
    response = model.send_request(prompt)
    try:
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx >= 0 and end_idx > 0:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        return {"error": "Could not parse JSON from model response"}
    except Exception as e:
        return {"error": str(e)}
