import os
import sys
import subprocess
import platform
import shutil
import json
import threading
import time
import uuid

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

class CopilotLSPClient:
    def __init__(self):
        self.proc = None
        self._start_lsp()
        self._id_counter = 100
        self._pending = {}
        self._reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        self._reader_thread.start()
        self._status = None
        self._last_response = None

    def _start_lsp(self):
        self.proc = run_copilot_lsp()
        time.sleep(0.2)

    def _next_id(self):
        self._id_counter += 1
        return self._id_counter

    def _send(self, msg):
        data = json.dumps(msg)
        header = f"Content-Length: {len(data)}\r\n\r\n"
        self.proc.stdin.write(header.encode() + data.encode())
        self.proc.stdin.flush()

    def _read_responses(self):
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break
            if line.startswith(b"Content-Length:"):
                length = int(line.decode().split(":")[1].strip())
                self.proc.stdout.readline()  # skip empty line
                body = self.proc.stdout.read(length)
                resp = json.loads(body)
                if 'id' in resp:
                    self._pending[resp['id']] = resp
                if resp.get('method') == 'window/logMessage':
                    print(f"[Copilot LSP] {resp['params']['message']}")
                if resp.get('method') == 'window/showMessageRequest':
                    print(f"[Copilot LSP] {resp['params']['message']}")
                if resp.get('method') == 'telemetry/event':
                    pass  # handle telemetry if needed
                if resp.get('method') == 'copilot/didChangeStatus' or resp.get('method') == 'copilot/status':
                    self._status = resp['params']
                self._last_response = resp

    def initialize(self):
        msg = {
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
        self._send(msg)
        time.sleep(0.5)
        notif = {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        self._send(notif)

    def sign_in(self):
        self.initialize()
        signin = {"jsonrpc": "2.0", "id": 2, "method": "signIn", "params": {}}
        self._send(signin)
        # Wait for response
        for _ in range(20):
            resp = self._pending.get(2)
            if resp:
                user_code = resp["result"]["userCode"]
                print(f"Copilot Login: Go to the URL provided and enter code: {user_code}")
                print("Follow the browser instructions to complete authentication.")
                return user_code
            time.sleep(0.5)
        print("Copilot login timed out.")
        return None

    def sign_out(self):
        signout = {"jsonrpc": "2.0", "id": self._next_id(), "method": "signOut", "params": {}}
        self._send(signout)
        print("Sign out request sent.")

    def status(self):
        # Status is sent as notification, but we can print last known
        print(f"Copilot status: {self._status}")
        return self._status

    def did_change_configuration(self, settings):
        msg = {
            "jsonrpc": "2.0",
            "method": "workspace/didChangeConfiguration",
            "params": {"settings": settings}
        }
        self._send(msg)

    def did_change_workspace_folders(self, added=None, removed=None):
        msg = {
            "jsonrpc": "2.0",
            "method": "workspace/didChangeWorkspaceFolders",
            "params": {
                "event": {
                    "added": added or [],
                    "removed": removed or []
                }
            }
        }
        self._send(msg)

    def did_open(self, file_path, language_id="python", version=1):
        with open(file_path, "r") as f:
            text = f.read()
        msg = {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": f"file://{os.path.abspath(file_path)}",
                    "languageId": language_id,
                    "version": version,
                    "text": text
                }
            }
        }
        self._send(msg)

    def did_change(self, file_path, text, version=2):
        msg = {
            "jsonrpc": "2.0",
            "method": "textDocument/didChange",
            "params": {
                "textDocument": {
                    "uri": f"file://{os.path.abspath(file_path)}",
                    "version": version
                },
                "contentChanges": [{"text": text}]
            }
        }
        self._send(msg)

    def did_close(self, file_path):
        msg = {
            "jsonrpc": "2.0",
            "method": "textDocument/didClose",
            "params": {
                "textDocument": {
                    "uri": f"file://{os.path.abspath(file_path)}"
                }
            }
        }
        self._send(msg)

    def did_focus(self, file_path=None):
        params = {"textDocument": {"uri": f"file://{os.path.abspath(file_path)}"}} if file_path else {}
        msg = {"jsonrpc": "2.0", "method": "textDocument/didFocus", "params": params}
        self._send(msg)

    def inline_completion(self, file_path, line, character, version=1, tab_size=4, insert_spaces=True):
        uri = f"file://{os.path.abspath(file_path)}"
        msg = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "textDocument/inlineCompletion",
            "params": {
                "textDocument": {"uri": uri, "version": version},
                "position": {"line": line, "character": character},
                "context": {"triggerKind": 2},
                "formattingOptions": {"tabSize": tab_size, "insertSpaces": insert_spaces}
            }
        }
        self._send(msg)
        # Wait for response
        for _ in range(20):
            resp = self._pending.get(msg["id"])
            if resp:
                return resp.get("result", {})
            time.sleep(0.2)
        return None

    def panel_completion(self, file_path, line, character, version=1):
        uri = f"file://{os.path.abspath(file_path)}"
        msg = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "textDocument/copilotPanelCompletion",
            "params": {
                "textDocument": {"uri": uri, "version": version},
                "position": {"line": line, "character": character},
                "partialResultToken": str(uuid.uuid4())
            }
        }
        self._send(msg)
        for _ in range(20):
            resp = self._pending.get(msg["id"])
            if resp:
                return resp.get("result", {})
            time.sleep(0.2)
        return None

    def execute_command(self, command, arguments=None):
        msg = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "workspace/executeCommand",
            "params": {"command": command, "arguments": arguments or []}
        }
        self._send(msg)

    def shutdown(self):
        if self.proc:
            self.proc.terminate()

# CLI wrappers for login/logout/status/lsp/inline completion

def copilot_login():
    client = CopilotLSPClient()
    client.sign_in()
    client.shutdown()

def copilot_logout():
    client = CopilotLSPClient()
    client.sign_out()
    client.shutdown()

def copilot_status():
    client = CopilotLSPClient()
    client.status()
    client.shutdown()

def copilot_lsp_inline_completion(file_path, line, character):
    client = CopilotLSPClient()
    client.initialize()
    client.did_open(file_path)
    result = client.inline_completion(file_path, line, character)
    print(json.dumps(result, indent=2))
    client.shutdown()

def copilot_lsp_panel_completion(file_path, line, character):
    client = CopilotLSPClient()
    client.initialize()
    client.did_open(file_path)
    result = client.panel_completion(file_path, line, character)
    print(json.dumps(result, indent=2))
    client.shutdown()

def copilot_autocomplete(file_path, line, character):
    """Request inline completion for a file at a given position."""
    proc = run_copilot_lsp()
    # (Initialization as above, then send inlineCompletion request)
    # For brevity, not fully implemented here, but follows the same LSP protocol as login.
    # See copilot.md for request/response structure.
    pass