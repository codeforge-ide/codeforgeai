import subprocess
import os
import json
import logging

logger = logging.getLogger(__name__)

def compile_contract(file_path, output_format='abi', optimize=None, evm_version=None):
    """
    Compile a Vyper contract.
    
    Args:
        file_path (str): Path to the Vyper contract file (.vy)
        output_format (str): Output format (default: 'abi')
        optimize (str, optional): Optimization mode: 'none', 'gas', or 'codesize'
        evm_version (str, optional): Target EVM version
        
    Returns:
        dict: Dictionary containing compilation results or error information
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.endswith(".vy"):
        return {"error": f"Not a Vyper file: {file_path}"}
    
    try:
        cmd = ["vyper"]
        
        # Add output format
        if output_format:
            cmd.extend(["-f", output_format])
        
        # Add optimization mode if specified
        if optimize:
            cmd.extend(["--optimize", optimize])
        
        # Add EVM version if specified
        if evm_version:
            cmd.extend(["--evm-version", evm_version])
            
        cmd.append(file_path)
        
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Try to parse as JSON if possible
        try:
            return {
                "success": True,
                "output": json.loads(result.stdout),
                "format": output_format
            }
        except json.JSONDecodeError:
            # Return as plain text if not JSON
            return {
                "success": True,
                "output": result.stdout,
                "format": output_format
            }
            
    except subprocess.CalledProcessError as e:
        return {
            "error": f"Compilation failed: {e.stderr}"
        }
    except FileNotFoundError:
        return {
            "error": "Vyper compiler not found. Make sure it's installed and in your PATH."
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}"
        }

def check_vyper_installed():
    """Check if Vyper compiler is installed and get version"""
    try:
        result = subprocess.run(['vyper', '--version'], 
                               capture_output=True, text=True, check=True)
        return {
            "installed": True,
            "version": result.stdout.strip()
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "installed": False,
            "version": None
        }

def analyze_contract(file_path):
    """
    Analyze a Vyper smart contract for common patterns and features
    
    Args:
        file_path (str): Path to the Vyper contract file (.vy)
        
    Returns:
        dict: Information about the contract features
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        analysis = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "features": {
                "has_pragma": "#pragma" in content or "# @version" in content,
                "has_structs": "struct " in content,
                "has_events": "event " in content,
                "has_external_functions": "@external" in content,
                "has_internal_functions": "@internal" in content,
                "has_view_functions": "@view" in content,
                "has_pure_functions": "@pure" in content,
                "has_payable_functions": "@payable" in content,
                "has_interfaces": "interface " in content or "from " in content and " import " in content
            }
        }
        
        # Try to detect contract type
        if "def bid" in content and "@payable" in content:
            analysis["contract_type"] = "Auction"
        elif "def transfer" in content and "balance" in content:
            analysis["contract_type"] = "Token"
        elif "vote" in content and "proposal" in content:
            analysis["contract_type"] = "Voting"
        elif "crowdfund" in content.lower() or "fund" in content.lower() and "goal" in content:
            analysis["contract_type"] = "Crowdfund"
        else:
            analysis["contract_type"] = "Generic"
            
        return analysis
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}
