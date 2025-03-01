def pretty_print_json(data):
    import json
    print(json.dumps(data, indent=4))

# ...other utility functions...

# Secret AI SDK integration utilities
def check_secret_ai_credentials():
    """Check if Secret AI credentials are properly set up.
    
    Returns:
        bool: True if credentials are found, False otherwise
    """
    import os
    return bool(os.environ.get("CLAIVE_AI_API_KEY"))

def format_smart_contract_analysis(analysis_text):
    """Format smart contract analysis output for better readability.
    
    Args:
        analysis_text: Raw analysis text from Secret AI
        
    Returns:
        Formatted analysis text with sections and highlighting
    """
    import re
    
    # Add section headers
    formatted = analysis_text
    sections = ["Security Issues", "Gas Optimization", "Code Quality", "Recommendations"]
    
    for section in sections:
        pattern = fr'(?i){section}:?\s*'
        if re.search(pattern, formatted):
            formatted = re.sub(pattern, f"\n\n## {section}\n", formatted)
    
    # Add code highlighting
    code_blocks = re.findall(r'```(\w*)\n(.*?)```', formatted, re.DOTALL)
    for lang, code in code_blocks:
        highlighted = f"```{lang}\n{code}```"
        formatted = formatted.replace(f"```{lang}\n{code}```", highlighted)
    
    return formatted

def check_web3_dev_environment():
    """Check for required web3 development tools and report status.
    
    Returns:
        Dict with status of each tool
    """
    tools = {
        "node": "node --version",
        "npm": "npm --version",
        "truffle": "truffle version",
        "hardhat": "npx hardhat --version",
        "ganache": "ganache-cli --version",
        "solc": "solc --version"
    }
    
    results = {}
    import subprocess
    import shutil
    
    for tool, cmd in tools.items():
        if tool == "solc" and not shutil.which("solc"):
            # Special case for solc which might be installed via npm
            try:
                subprocess.check_output("npx solcjs --version", shell=True, text=True)
                results[tool] = "Available via npx"
                continue
            except:
                pass
                
        try:
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
            results[tool] = "Available"
        except (subprocess.CalledProcessError, FileNotFoundError):
            results[tool] = "Not found"
            
    return results

def install_web3_dependencies(install_type="minimal"):
    """Install required web3 dependencies.
    
    Args:
        install_type: Type of installation ("minimal", "full")
        
    Returns:
        Result of installation
    """
    import subprocess
    
    packages = {
        "minimal": ["ethers", "web3", "hardhat"],
        "full": ["ethers", "web3", "hardhat", "truffle", "ganache", "solc", "@openzeppelin/contracts"]
    }
    
    if install_type not in packages:
        return f"Unknown installation type: {install_type}"
    
    try:
        # Check if npm is available
        subprocess.check_output("npm --version", shell=True)
        
        # Install selected packages
        result = subprocess.check_output(
            f"npm install --save-dev {' '.join(packages[install_type])}",
            shell=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        return f"Successfully installed web3 dependencies:\n{result}"
    except subprocess.CalledProcessError as e:
        return f"Error installing dependencies: {e.output}"
    except FileNotFoundError:
        return "npm not found. Please install Node.js and npm first."
