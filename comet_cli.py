#!/usr/bin/env python3
"""
☄️ COMET-AGENT INTERACTIVE TERMINAL CLI CLIENT (RESILIENT EDITION)
Designed for maximized humanized code power, strong resilience, and diverse utilization.

Features:
- Request retry decorator with backoff for connection stability.
- Automatic session activity logging to output/session_<id>_history.log.
- Option to save extracted page text/HTML directly to local files in output/.
- Seamless server checks & automated background startup.
- Full ANSI color-coded console telemetry.
"""

import os
import sys
import time
import json
import socket
import subprocess
import requests
from typing import Optional, Dict, Any, Callable

# --- ANSI CONSOLE COLOR SYSTEM ---
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"

def print_banner():
    print(f"\n{C_BOLD}{C_MAGENTA}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║ ☄️  COMET-AGENT INTERACTIVE CONTROL CLI [RESILIENT EDITION]       ║")
    print(f"║    [ Robust Retries | Export Pipelines | Local Session Logs ]   ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{C_RESET}\n")

def log_info(msg: str):
    print(f"{C_BOLD}{C_CYAN}[INFO]{C_RESET} {msg}")

def log_success(msg: str):
    print(f"{C_BOLD}{C_GREEN}[SUCCESS]{C_RESET} {msg}")

def log_warning(msg: str):
    print(f"{C_BOLD}{C_YELLOW}[WARNING]{C_RESET} {msg}")

def log_error(msg: str):
    print(f"{C_BOLD}{C_RED}[ERROR]{C_RESET} {msg}")

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# --- RESILIENCE DECORATOR: CONNECTION RETRY WITH BACKOFF ---
def resilient_request(max_retries: int = 3, backoff_in_seconds: float = 2.0):
    """Decorator to retry HTTP requests upon encountering connection issues or timeouts."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    last_error = e
                    if isinstance(e, requests.exceptions.ConnectionError):
                        log_warning("Server connection lost. Attempting to ensure server is online...")
                        if len(args) > 0 and hasattr(args[0], 'ensure_server'):
                            args[0].ensure_server()
                    if attempt < max_retries - 1:
                        sleep_time = backoff_in_seconds * (2 ** attempt)
                        log_warning(f"Retrying in {sleep_time}s (Attempt {attempt + 1}/{max_retries})...")
                        time.sleep(sleep_time)
            log_error(f"Failed to complete operation after {max_retries} attempts: {last_error}")
            return None
        return wrapper
    return decorator

class CometClient:
    def __init__(self, port: int = 8787):
        self.base_url = f"http://localhost:{port}"
        self.session_id: Optional[str] = None
        self.port = port
        self.log_file_path: Optional[str] = None

    def log_activity(self, message: str):
        """Append operational event to the active session log file."""
        if not self.log_file_path:
            return
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def ensure_server(self):
        """Checks if server is running; if not, attempts to launch it in the background."""
        if is_port_in_use(self.port):
            log_info(f"Connected to active comet-agent server on port {self.port}.")
            return

        log_warning(f"comet-agent server offline on port {self.port}. Spinning up server...")
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.expanduser("~/logs")
        os.makedirs(log_dir, exist_ok=True)
        boot_log = os.path.join(log_dir, "comet_agent_boot.log")
        
        with open(boot_log, "a") as f:
            f.write(f"\n--- BOOTING FROM CLI CLIENT AT {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            
        env = os.environ.copy()
        dist_path = os.path.join(project_dir, "dist", "index.js")
        if os.path.exists(dist_path):
            boot_cmd = ["node", dist_path]
            env["NODE_ENV"] = "production"
            log_info("Starting server from pre-compiled dist/index.js (low-memory)...")
        else:
            boot_cmd = ["npm", "run", "dev"]
            env["NODE_ENV"] = "development"
            log_info("Starting server in dev mode via tsx watch...")
            
        subprocess.Popen(
            boot_cmd,
            cwd=project_dir,
            stdout=open(boot_log, "a"),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            env=env
        )
        
        for _ in range(10):
            time.sleep(1.0)
            if is_port_in_use(self.port):
                log_success(f"comet-agent server successfully initialized on port {self.port}!")
                return
                
        log_error("Could not verify server startup. Check logs in ~/logs/comet_agent_boot.log.")
        sys.exit(1)

    @resilient_request(max_retries=3, backoff_in_seconds=1.5)
    def create_session(self, custom_id: Optional[str] = None) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/session"
        payload = {"sessionId": custom_id} if custom_id else {}
        return requests.post(url, json=payload, timeout=10)

    def initialize_session(self, custom_id: Optional[str] = None) -> bool:
        """Helper to create session and establish logging boundaries."""
        r = self.create_session(custom_id)
        if r and r.status_code == 200:
            data = r.json()
            self.session_id = data["session"]["id"]
            
            # Setup session audit log path
            project_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(project_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            self.log_file_path = os.path.join(output_dir, f"session_{self.session_id}_history.log")
            
            self.log_activity(f"Session initialized. Custom ID requested: {custom_id}")
            log_success(f"Browser Session Created: {C_BOLD}{self.session_id}{C_RESET}")
            log_info(f"Audit log active at: {self.log_file_path}")
            return True
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            text = r.text if r else "Host unreachable"
            log_error(f"Failed to create session: {code} - {text}")
            return False

    @resilient_request(max_retries=3, backoff_in_seconds=2.0)
    def navigate_request(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/navigate"
        return requests.post(url, json=payload, timeout=25)

    def navigate(self, target_url: str) -> bool:
        if not self.session_id:
            log_warning("No active session.")
            return False
            
        payload = {
            "sessionId": self.session_id,
            "url": target_url,
            "waitUntil": "domcontentloaded"
        }
        
        log_info(f"Navigating to {C_BOLD}{target_url}{C_RESET}...")
        self.log_activity(f"Navigation request to URL: {target_url}")
        
        t0 = time.time()
        r = self.navigate_request(payload)
        latency = round(time.time() - t0, 2)
        
        if r and r.status_code == 200:
            log_success(f"Navigated successfully! (Latency: {latency}s)")
            self.log_activity(f"Navigation success (Latency: {latency}s). URL resolved: {r.json().get('url')}")
            return True
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            log_error(f"Navigation failed (Code: {code}).")
            self.log_activity(f"Navigation failed (Code: {code}).")
            return False

    @resilient_request(max_retries=3, backoff_in_seconds=1.5)
    def act_request(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/act"
        return requests.post(url, json=payload, timeout=15)

    def act(self, selector: Optional[str], value: Optional[str], instruction: Optional[str] = None) -> bool:
        if not self.session_id:
            log_warning("No active session.")
            return False
            
        payload: Dict[str, Any] = {"sessionId": self.session_id}
        if selector:
            payload["selector"] = selector
        if value:
            payload["value"] = value
        if instruction:
            payload["instruction"] = instruction
            
        action_desc = f"Selector={selector}" if selector else f"Instruction={instruction}"
        log_info(f"Executing action: {C_BOLD}{action_desc}{C_RESET}...")
        self.log_activity(f"Action triggered: {action_desc} | Value: {value}")
        
        r = self.act_request(payload)
        if r and r.status_code == 200:
            log_success("Action executed successfully.")
            self.log_activity("Action response: SUCCESS")
            return True
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            text = r.text if r else "Host unreachable"
            log_error(f"Action failed: {code} - {text}")
            self.log_activity(f"Action response: FAILED ({code})")
            return False

    @resilient_request(max_retries=3, backoff_in_seconds=1.5)
    def extract_request(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/extract"
        return requests.post(url, json=payload, timeout=20)

    def extract(self, selector: Optional[str], instruction: Optional[str] = None) -> Optional[Any]:
        if not self.session_id:
            log_warning("No active session.")
            return None
            
        payload: Dict[str, Any] = {"sessionId": self.session_id}
        if selector:
            payload["selector"] = selector
        if instruction:
            payload["instruction"] = instruction
            
        log_info("Extracting data from page...")
        self.log_activity(f"Extraction triggered. Selector: {selector} | Instruction: {instruction}")
        
        r = self.extract_request(payload)
        if r and r.status_code == 200:
            data = r.json().get("data")
            log_success("Extraction completed successfully.")
            self.log_activity(f"Extraction success. Data length: {len(str(data))}")
            return data
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            log_error(f"Extraction failed: {code}")
            self.log_activity(f"Extraction failed (Code: {code})")
            return None

    @resilient_request(max_retries=3, backoff_in_seconds=1.5)
    def screenshot_request(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/screenshot"
        return requests.post(url, json=payload, timeout=15)

    def take_screenshot(self, filename: str) -> bool:
        if not self.session_id:
            log_warning("No active session.")
            return False
            
        payload = {"sessionId": self.session_id, "fullPage": True}
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_dir, "output")
        dest_path = os.path.join(output_dir, filename)
        
        log_info(f"Capturing screenshot...")
        self.log_activity(f"Screenshot triggered. Destination file: {filename}")
        
        r = self.screenshot_request(payload)
        if r and r.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            log_success(f"Screenshot saved to: {C_BOLD}{dest_path}{C_RESET}")
            self.log_activity(f"Screenshot success: {dest_path}")
            return True
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            log_error(f"Screenshot failed: {code}")
            self.log_activity(f"Screenshot failed (Code: {code})")
            return False

    @resilient_request(max_retries=3, backoff_in_seconds=1.0)
    def delete_session(self) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/session/{self.session_id}"
        return requests.delete(url, timeout=10)

    def close_session(self) -> bool:
        if not self.session_id:
            return True
            
        log_info(f"Closing session {self.session_id}...")
        self.log_activity("Session termination requested.")
        
        r = self.delete_session()
        if r and r.status_code == 200:
            log_success("Session closed successfully.")
            self.log_activity("Session closed successfully. Connection terminated.")
            self.session_id = None
            return True
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            log_error(f"Failed to close session cleanly: {code}")
            self.log_activity(f"Session close error: {code}")
            return False

    @resilient_request(max_retries=3, backoff_in_seconds=1.5)
    def get_sessions_request(self) -> Optional[requests.Response]:
        url = f"{self.base_url}/browser/sessions"
        return requests.get(url, timeout=10)

    def list_sessions(self) -> Optional[list]:
        """Fetch list of all active sessions from the server."""
        r = self.get_sessions_request()
        if r and r.status_code == 200:
            return r.json().get("sessions", [])
        else:
            code = r.status_code if r else "CONNECTION ERROR"
            log_error(f"Failed to fetch sessions: {code}")
            return None

    def attach_session(self, session_id: str) -> bool:
        """Attach to an existing active session."""
        self.session_id = session_id
        project_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(project_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        self.log_file_path = os.path.join(output_dir, f"session_{self.session_id}_history.log")
        self.log_activity(f"Session attached: {session_id}")
        log_success(f"Attached to Browser Session: {C_BOLD}{self.session_id}{C_RESET}")
        log_info(f"Audit log active at: {self.log_file_path}")
        return True

def save_extracted_data(data: Any, default_name: str = "extracted_data.txt"):
    """Helper to save extracted data string or json directly to output/ folder."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_dir, "output")
    
    filename = input(f"Enter filename to save data (default: {default_name}): ").strip()
    if not filename:
        filename = default_name
        
    dest_path = os.path.join(output_dir, filename)
    try:
        with open(dest_path, "w") as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        log_success(f"Extracted content successfully exported to: {C_BOLD}{dest_path}{C_RESET}")
    except Exception as e:
        log_error(f"Failed to write exported file: {e}")

def run_session_menu(client: CometClient):
    while client.session_id:
        print(f"\n{C_BOLD}☄️  [Session: {client.session_id}] Action Menu:{C_RESET}")
        print("  [1] Navigate to URL")
        print("  [2] Act on Page (click/fill selector)")
        print("  [3] Extract Page Content (with export pipeline)")
        print("  [4] Capture Screenshot")
        print("  [5] Detach from Session (returns to main menu)")
        print("  [6] Close Session & Detach")
        
        opt = input(f"\nSelect action [1-6]: ").strip()
        print()
        
        if opt == "1":
            target = input("Enter target URL (e.g. https://google.com): ").strip()
            if target:
                client.navigate(target)
                
        elif opt == "2":
            sel = input("Enter CSS selector (leave blank for instruction): ").strip()
            val = None
            inst = None
            if sel:
                val = input("Enter text value to fill (leave blank to just click): ").strip()
                if not val:
                    val = None
            else:
                inst = input("Enter natural language instruction for agent: ").strip()
                if not inst:
                    log_warning("Must provide either selector or instruction.")
                    continue
            client.act(selector=sel, value=val, instruction=inst)
            
        elif opt == "3":
            sel = input("Enter CSS selector to extract from (leave blank for full page): ").strip()
            inst = None
            if not sel:
                inst = input("Enter extraction instruction (leave blank for raw HTML): ").strip()
                if not inst:
                    inst = None
            data = client.extract(selector=sel, instruction=inst)
            if data:
                print(f"\n{C_DIM}--- EXTRACTED CONTENT PREVIEW ---{C_RESET}")
                if isinstance(data, (dict, list)):
                    preview = json.dumps(data, indent=2)
                    default_ext = "extracted_data.json"
                else:
                    preview = str(data)
                    default_ext = "extracted_page.html" if not sel and not inst else "extracted_data.txt"
                
                print(preview[:800])
                if len(preview) > 800:
                    print(f"\n{C_DIM}... [truncated {len(preview) - 800} chars] ...{C_RESET}")
                print(f"{C_DIM}---------------------------------{C_RESET}\n")
                
                save_opt = input("Do you want to save this extracted content to a file? (y/n): ").strip().lower()
                if save_opt == 'y':
                    save_extracted_data(data, default_ext)
                
        elif opt == "4":
            filename = input("Enter file name (default: page_capture.png): ").strip()
            if not filename:
                filename = "page_capture.png"
            if not filename.endswith(".png"):
                filename += ".png"
            client.take_screenshot(filename)
            
        elif opt == "5":
            log_info(f"Detaching from session {client.session_id}. Session remains active on server.")
            client.session_id = None
            break
            
        elif opt == "6":
            client.close_session()
            break
        else:
            log_warning("Invalid option. Enter [1-6].")

def show_interactive_loop(client: CometClient):
    print_banner()
    client.ensure_server()
    
    while True:
        print(f"\n{C_BOLD}Main Menu:{C_RESET}")
        print("  1. Create new random session")
        print("  2. Create custom named session")
        print("  3. List active sessions on server")
        print("  4. Attach to an existing session")
        print("  5. Exit")
        
        choice = input(f"\nSelect option: ").strip()
        if choice == "5":
            print("Goodbye.")
            break
        elif choice == "1":
            if client.initialize_session():
                run_session_menu(client)
        elif choice == "2":
            name = input("Enter custom session name: ").strip()
            if not name:
                log_warning("Name cannot be empty.")
                continue
            if client.initialize_session(name):
                run_session_menu(client)
        elif choice == "3":
            sessions = client.list_sessions()
            if sessions is not None:
                if not sessions:
                    log_info("No active sessions on the server.")
                else:
                    print(f"\n{C_BOLD}Active Sessions:{C_RESET}")
                    for idx, s in enumerate(sessions):
                        print(f"  [{idx + 1}] ID: {C_BOLD}{s['id']}{C_RESET} | URL: {s['url']} | Created: {s['createdAt']}")
            else:
                log_error("Could not fetch sessions.")
        elif choice == "4":
            sessions = client.list_sessions()
            if sessions is None:
                log_error("Could not fetch sessions.")
                continue
            if not sessions:
                log_info("No active sessions to attach to.")
                continue
            
            print(f"\n{C_BOLD}Select a session to attach to:{C_RESET}")
            for idx, s in enumerate(sessions):
                print(f"  [{idx + 1}] ID: {C_BOLD}{s['id']}{C_RESET} | URL: {s['url']}")
            
            idx_input = input(f"\nEnter number [1-{len(sessions)}]: ").strip()
            try:
                idx = int(idx_input) - 1
                if 0 <= idx < len(sessions):
                    selected_id = sessions[idx]["id"]
                    if client.attach_session(selected_id):
                        run_session_menu(client)
                else:
                    log_warning("Invalid selection.")
            except ValueError:
                log_warning("Invalid input. Must be a number.")
        else:
            log_warning("Invalid option. Enter [1-5].")

if __name__ == "__main__":
    client = CometClient()
    try:
        show_interactive_loop(client)
    except KeyboardInterrupt:
        print("\n\nCtrl+C detected. Terminating session...")
        client.close_session()
        print("Goodbye.")
