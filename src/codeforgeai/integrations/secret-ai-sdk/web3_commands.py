import os
import json
import logging
from typing import Dict, List, Any, Optional
import subprocess

from codeforgeai.integrations.secret-ai-sdk.secret_ai_integration import SecretAIModel, get_web3_contract_analysis, generate_web3_boilerplate

_logger = logging.getLogger(__name__)

def scaffold_web3_project(project_name: str, project_type: str, output_dir: Optional[str] = None) -> str:
    """Scaffold a new web3 project using Secret AI.
    
    Args:
        project_name: Name of the project
        project_type: Type of project (dapp, smart-contract, token, etc.)
        output_dir: Directory to create the project in (default: current directory)
        
    Returns:
        Path to the created project
    """
    if not output_dir:
        output_dir = os.getcwd()
        
    project_dir = os.path.join(output_dir, project_name)
    
    # Create project directory
    os.makedirs(project_dir, exist_ok=True)
    
    # Generate boilerplate code
    files = generate_web3_boilerplate(project_type)
    
    if "error" in files:
        _logger.error(f"Error generating boilerplate: {files['error']}")
        return f"Error: {files['error']}"
    
    # Write files to disk
    for file_path, content in files.items():
        # Ensure directories exist
        full_path = os.path.join(project_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file
        with open(full_path, "w") as f:
            f.write(content)
            
    return f"Web3 project created at {project_dir}"

def analyze_smart_contract(contract_file: str) -> str:
    """Analyze a local smart contract file.
    
    Args:
        contract_file: Path to the smart contract file
        
    Returns:
        Analysis of the contract
    """
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return f"Error: Contract file {contract_file} not found"
        
    model = SecretAIModel()
    
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
    """Estimate gas costs for a smart contract.
    
    Args:
        contract_file: Path to the smart contract file
        
    Returns:
        Estimated gas costs for each function
    """
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return f"Error: Contract file {contract_file} not found"
        
    model = SecretAIModel()
    
    prompt = f"""For the following smart contract, estimate gas costs for each function.
    Return the results as a formatted table.
    
    ```solidity
    {contract_code}
    ```
    """
    
    return model.send_request(prompt)

def generate_web3_tests(contract_file: str) -> Dict[str, str]:
    """Generate tests for a smart contract using Secret AI.
    
    Args:
        contract_file: Path to the smart contract file
        
    Returns:
        Dictionary of test file paths and their content
    """
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return {"error": f"Contract file {contract_file} not found"}
        
    model = SecretAIModel()
    
    prompt = f"""Generate comprehensive test cases for the following smart contract.
    Use Hardhat and ethers.js for testing.
    Include tests for all public/external functions.
    Cover edge cases and security considerations.
    
    ```solidity
    {contract_code}
    ```
    
    Format the response as a JSON object with test file paths as keys and test content as values.
    """
    
    response = model.send_request(prompt)
    try:
        # Try to parse JSON from the response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx >= 0 and end_idx > 0:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        return {"error": "Could not parse JSON from model response", "response": response}
    except Exception as e:
        return {"error": str(e), "response": response}

def verify_contract_compatibility(contract_file: str, target: str = "latest") -> str:
    """Verify smart contract compatibility with specified target.
    
    Args:
        contract_file: Path to the smart contract file
        target: Target compatibility (solidity version, EVM, etc.)
        
    Returns:
        Compatibility analysis
    """
    try:
        with open(contract_file, "r") as f:
            contract_code = f.read()
    except FileNotFoundError:
        return f"Error: Contract file {contract_file} not found"
        
    model = SecretAIModel()
    
    prompt = f"""Check if this smart contract is compatible with {target} standards/version.
    Identify any compatibility issues and suggest fixes.
    
    ```solidity
    {contract_code}
    ```
    """
    
    return model.send_request(prompt)
