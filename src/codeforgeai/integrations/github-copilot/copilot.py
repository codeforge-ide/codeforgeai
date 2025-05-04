import os
import sys
import subprocess
import platform
import shutil
import json

def detect_package_manager():
    """Detect global package manager, preferring pnpm > yarn > npm."""
    for pm in ["pnpm", "yarn", "npm"]:
        if shutil.which(pm):
            return pm
    raise RuntimeError("No supported package manager (pnpm, yarn, npm) found.")

def get_global_node_modules(pm):
    """Get global node_modules root for the given package manager."""
    try:
        if pm == "pnpm":
            out = subprocess.check_output([pm, "root", "-g"], text=True).strip()
        elif pm == "yarn":
            out = subprocess.check_output([pm, "global", "dir"], text=True).strip()
            out = os.path.join(out, "node_modules")
        else:  # npm
            out = subprocess.check_output([pm, "root", "-g"], text=True).strip()
        return out
    except Exception as e:
        raise RuntimeError(f"Failed to get global node_modules for {pm}: {e}")

def get_architecture():
    """Map platform/arch to Copilot's expected folder name."""
    sys_map = {
        "Darwin": "darwin",
        "Linux": "linux",
        "Windows": "win32"
    }
    arch_map = {
        "x86_64": "x64",
        "arm64": "arm64",
        "AMD64": "x64"
    }
    sys_name = sys_map.get(platform.system())
    arch = arch_map.get(platform.machine(), platform.machine())
    if not sys_name or not arch:
        raise RuntimeError("Unsupported OS or architecture for Copilot LSP.")
    return f"{sys_name}-{arch}"

def get_copilot_lsp_path():
    pm = detect_package_manager()
    node_modules = get_global_node_modules(pm)
    arch = get_architecture()
    lsp_path = os.path.join(
        node_modules, "@github", "copilot-language-server", "native", arch, "copilot-language-server"
    )
    if not os.path.isfile(lsp_path):
        raise FileNotFoundError(f"Copilot language server binary not found at {lsp_path}")
    return lsp_path

def install_copilot_language_server():
    pm = detect_package_manager()
    pkg = "@github/copilot-language-server"
    try:
        if pm == "pnpm":
            subprocess.check_call([pm, "add", "-g", pkg])
        elif pm == "yarn":
            subprocess.check_call([pm, "global", "add", pkg])
        else:
            subprocess.check_call([pm, "install", "-g", pkg])
        print("Copilot language server installed globally.")
    except Exception as e:
        print(f"Failed to install Copilot language server: {e}")

def run_copilot_lsp(extra_args=None):
    """Run the Copilot language server with --stdio."""
    lsp_path = get_copilot_lsp_path()
    args = [lsp_path, "--stdio"]
    if extra_args:
        args.extend(extra_args)
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def copilot_login():
    """Handle Copilot login flow via LSP."""
    import threading

    proc = run_copilot_lsp()
    # Send initialize request (see copilot.md)
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": os.getpid(),
            "workspaceFolders": [{"uri": f"file://{os.getcwd()}"}],
            "capabilities": {"workspace": {"workspaceFolders": True}},
            "initializationOptions": {
                "editorInfo": {"name": "CodeforgeAI", "version": "1.0.0"},
                "editorPluginInfo": {"name": "CodeforgeAI Copilot", "version": "1.0.0"}
            }
        }
    }
    msg = json.dumps(initialize)
    header = f"Content-Length: {len(msg)}\r\n\r\n"
    proc.stdin.write(header.encode() + msg.encode())
    proc.stdin.flush()

    # Wait for initialize response, then send initialized notification
    def read_responses():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if line.startswith(b"Content-Length:"):
                length = int(line.decode().split(":")[1].strip())
                proc.stdout.readline()  # skip empty line
                body = proc.stdout.read(length)
                resp = json.loads(body)
                if resp.get("id") == 1:
                    # Send initialized notification
                    notif = {
                        "jsonrpc": "2.0",
                        "method": "initialized",
                        "params": {}
                    }
                    notif_msg = json.dumps(notif)
                    notif_header = f"Content-Length: {len(notif_msg)}\r\n\r\n"
                    proc.stdin.write(notif_header.encode() + notif_msg.encode())
                    proc.stdin.flush()
                    # Now send signIn request
                    signin = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "signIn",
                        "params": {}
                    }
                    signin_msg = json.dumps(signin)
                    signin_header = f"Content-Length: {len(signin_msg)}\r\n\r\n"
                    proc.stdin.write(signin_header.encode() + signin_msg.encode())
                    proc.stdin.flush()
                elif resp.get("id") == 2:
                    # signIn response
                    user_code = resp["result"]["userCode"]
                    print(f"Copilot Login: Go to the URL provided and enter code: {user_code}")
                    print("Follow the browser instructions to complete authentication.")
                    proc.terminate()
                    break
    t = threading.Thread(target=read_responses)
    t.start()
    t.join()

def copilot_autocomplete(file_path, line, character):
    """Request inline completion for a file at a given position."""
    proc = run_copilot_lsp()
    # (Initialization as above, then send inlineCompletion request)
    # For brevity, not fully implemented here, but follows the same LSP protocol as login.
    # See copilot.md for request/response structure.
    pass