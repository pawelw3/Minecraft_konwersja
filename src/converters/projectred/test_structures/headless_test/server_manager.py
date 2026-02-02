"""
Minecraft Server Manager

Manages headless Minecraft server lifecycle:
- Kills existing server on port if occupied
- Starts new server
- Waits for ready state
- Provides RCON connection

Usage:
    manager = ServerManager("1.18.2")
    manager.start()  # Kills existing, starts new
    # ... run tests ...
    manager.stop()
"""

import os
import sys
import time
import subprocess
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient
from src.converters.projectred.test_structures.headless_test.log_parser import LogParser


@dataclass
class ServerConfig:
    """Server configuration"""
    version: str
    server_dir: Path
    server_port: int = 25565
    rcon_port: int = 25575
    rcon_password: str = "test123"
    java_path: str = "java"
    java_args: list = field(default_factory=lambda: ["-Xms2G", "-Xmx4G"])
    start_timeout: float = 300.0  # 5 minutes


# Pre-configured servers
SERVERS: Dict[str, ServerConfig] = {
    "1.7.10": ServerConfig(
        version="1.7.10",
        server_dir=PROJECT_ROOT / "headless_server" / "1.7.10",
        server_port=25565,
        rcon_port=25575,
        rcon_password="test123",
        java_path=r"C:\Program Files (x86)\Common Files\Oracle\Java\java8path\java.exe"
    ),
    "1.18.2": ServerConfig(
        version="1.18.2",
        server_dir=PROJECT_ROOT / "headless_server" / "1.18.2",
        server_port=25565,
        rcon_port=25575,
        rcon_password="ae2test123",
        java_path="java"  # 1.18.2 works with modern Java
    ),
}


class ServerManager:
    """
    Manages Minecraft server lifecycle.

    Ensures only one server runs at a time on the configured port.
    """

    def __init__(self, version: str = "1.18.2"):
        """
        Initialize server manager.

        Args:
            version: Minecraft version ("1.7.10" or "1.18.2")
        """
        if version not in SERVERS:
            raise ValueError(f"Unknown version: {version}. Available: {list(SERVERS.keys())}")

        self.config = SERVERS[version]
        self.process: Optional[subprocess.Popen] = None
        self.rcon: Optional[RconClient] = None

    def log(self, msg: str, level: str = "INFO"):
        """Log message with timestamp"""
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")

    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def kill_process_on_port(self, port: int) -> bool:
        """
        Kill any process using the specified port.

        Returns:
            True if a process was killed, False otherwise
        """
        if not self.is_port_in_use(port):
            return False

        self.log(f"Port {port} is in use, killing existing process...")

        if sys.platform == "win32":
            # Windows: use netstat + taskkill
            try:
                # Find PID using the port
                result = subprocess.run(
                    f'netstat -ano | findstr ":{port}"',
                    shell=True, capture_output=True, text=True
                )

                for line in result.stdout.strip().split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        pid = parts[-1]
                        self.log(f"Killing PID {pid} on port {port}")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        time.sleep(2)
                        return True

            except Exception as e:
                self.log(f"Failed to kill process: {e}", "ERROR")
        else:
            # Linux/Mac: use fuser or lsof
            try:
                subprocess.run(f'fuser -k {port}/tcp', shell=True)
                time.sleep(2)
                return True
            except:
                pass

        return False

    def ensure_port_available(self):
        """Ensure server port is available, killing existing process if needed"""
        self.kill_process_on_port(self.config.server_port)

        # Also try to gracefully stop via RCON if RCON port is open
        if self.is_port_in_use(self.config.rcon_port):
            try:
                self.log("Attempting graceful shutdown via RCON...")
                client = RconClient(
                    "127.0.0.1",
                    self.config.rcon_port,
                    self.config.rcon_password
                )
                if client.connect():
                    client.command("/stop")
                    client.disconnect()
                    time.sleep(5)
            except:
                pass

            # Force kill if still running
            self.kill_process_on_port(self.config.rcon_port)

        # Wait a bit for port to be released
        for _ in range(10):
            if not self.is_port_in_use(self.config.server_port):
                return
            time.sleep(1)

        if self.is_port_in_use(self.config.server_port):
            raise RuntimeError(f"Failed to free port {self.config.server_port}")

    def find_server_jar(self) -> Path:
        """Find the server JAR file"""
        server_dir = self.config.server_dir

        # Look for run script first (1.18.2 style)
        run_bat = server_dir / "run.bat"
        if run_bat.exists():
            return run_bat

        # Look for forge universal jar
        for jar in server_dir.glob("forge-*-universal.jar"):
            return jar

        # Look for any forge jar
        for jar in server_dir.glob("forge-*.jar"):
            if "installer" not in jar.name.lower():
                return jar

        # Look for minecraft server jar
        for jar in server_dir.glob("minecraft_server*.jar"):
            return jar

        raise FileNotFoundError(f"No server JAR found in {server_dir}")

    def start(self) -> bool:
        """
        Start the server.

        Kills any existing server on the port first.

        Returns:
            True if server started successfully
        """
        self.log(f"Starting Minecraft {self.config.version} server...")

        # Ensure port is available
        self.ensure_port_available()

        # Find server JAR or run script
        server_path = self.find_server_jar()
        self.log(f"Using: {server_path.name}")

        # Build command
        if server_path.name == "run.bat":
            # Use run.bat for 1.18.2
            cmd = [str(server_path)]
            shell = True
        else:
            # Direct JAR execution
            cmd = [
                self.config.java_path,
                *self.config.java_args,
                "-jar", server_path.name,
                "nogui"
            ]
            shell = False

        self.log(f"Command: {cmd[0]}...")

        # Start server
        try:
            if shell:
                self.process = subprocess.Popen(
                    cmd[0],
                    cwd=str(self.config.server_dir),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.config.server_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE
                )

            self.log(f"Server process started (PID: {self.process.pid})")
            return True

        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False

    def wait_for_ready(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for server to be ready.

        Args:
            timeout: Maximum wait time in seconds (default: config.start_timeout)

        Returns:
            True if server is ready
        """
        timeout = timeout or self.config.start_timeout
        log_path = self.config.server_dir / "logs" / "latest.log"

        self.log(f"Waiting for server ready (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if process died
            if self.process and self.process.poll() is not None:
                self.log("Server process terminated unexpectedly", "ERROR")
                return False

            # Check logs
            if log_path.exists():
                try:
                    parser = LogParser(str(log_path))
                    status = parser.get_server_status()

                    if status.started and status.rcon_ready:
                        self.log(f"Server ready! (started at {status.start_time})")

                        # Connect RCON
                        self.rcon = RconClient(
                            "127.0.0.1",
                            self.config.rcon_port,
                            self.config.rcon_password
                        )
                        if self.rcon.connect():
                            self.log("RCON connected")
                            return True
                        else:
                            self.log("RCON connection failed", "WARN")

                except Exception as e:
                    pass  # Log might not be ready yet

            time.sleep(2)

        self.log("Timeout waiting for server", "ERROR")
        return False

    def stop(self):
        """Stop the server gracefully"""
        self.log("Stopping server...")

        # Disconnect RCON
        if self.rcon:
            try:
                self.rcon.command("/stop")
            except:
                pass
            try:
                self.rcon.disconnect()
            except:
                pass
            self.rcon = None

        # Wait for process to stop
        if self.process:
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.log("Force terminating server...")
                self.process.terminate()
            self.process = None

        # Final cleanup
        self.kill_process_on_port(self.config.server_port)

        self.log("Server stopped")

    def command(self, cmd: str) -> str:
        """Execute RCON command"""
        if not self.rcon:
            raise RuntimeError("Not connected to server")
        return self.rcon.command(cmd)

    def __enter__(self):
        """Context manager entry"""
        self.start()
        if not self.wait_for_ready():
            self.stop()
            raise RuntimeError("Server failed to start")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def main():
    """Test server manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Minecraft Server Manager")
    parser.add_argument("--version", default="1.18.2", choices=["1.7.10", "1.18.2"])
    parser.add_argument("--action", choices=["start", "stop", "restart", "status"], default="status")

    args = parser.parse_args()

    manager = ServerManager(args.version)

    if args.action == "status":
        port_status = "in use" if manager.is_port_in_use(manager.config.server_port) else "free"
        print(f"Server port {manager.config.server_port}: {port_status}")

        rcon_status = "in use" if manager.is_port_in_use(manager.config.rcon_port) else "free"
        print(f"RCON port {manager.config.rcon_port}: {rcon_status}")

    elif args.action == "start":
        manager.start()
        if manager.wait_for_ready():
            print("Server is ready!")
            print(f"RCON: 127.0.0.1:{manager.config.rcon_port}")
        else:
            print("Server failed to start")
            manager.stop()

    elif args.action == "stop":
        manager.ensure_port_available()
        print("Server stopped")

    elif args.action == "restart":
        manager.ensure_port_available()
        manager.start()
        if manager.wait_for_ready():
            print("Server restarted successfully")


if __name__ == "__main__":
    main()
