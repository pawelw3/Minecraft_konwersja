#!/usr/bin/env python3
"""
ProjectRed Headless Test - Complete Workflow

This script orchestrates the complete headless testing workflow:
1. Prepare test world (copy clean world, apply patch)
2. Start headless server
3. Wait for server ready
4. Run integration tests via RCON
5. Analyze results
6. Generate report

Usage:
    # Full test on 1.7.10
    python run_headless_test.py --version 1.7.10

    # Test on 1.18.2 (converted world)
    python run_headless_test.py --version 1.18.2

    # Only deploy structures (no server start)
    python run_headless_test.py --version 1.7.10 --deploy-only

    # Only run tests (server already running)
    python run_headless_test.py --version 1.7.10 --test-only

Configuration is read from config files or command line arguments.
"""

import os
import sys
import json
import shutil
import time
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Setup path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient
from src.converters.projectred.test_structures.headless_test.log_parser import LogParser, TestResult
from src.converters.projectred.test_structures.headless_test.patch_generator import (
    load_structures_from_dir, generate_projectred_test_patch
)


@dataclass
class ServerConfig:
    """Server configuration for specific Minecraft version"""
    version: str
    server_dir: str
    world_name: str = "world"
    clean_world_dir: Optional[str] = None  # Source for clean world copy
    server_jar: str = "minecraft_server.jar"
    java_args: List[str] = field(default_factory=lambda: ["-Xms1G", "-Xmx2G"])
    rcon_port: int = 25575
    rcon_password: str = "test123"
    server_port: int = 25565


# Default configurations
CONFIGS = {
    "1.7.10": ServerConfig(
        version="1.7.10",
        server_dir="headless_server/1.7.10",
        clean_world_dir="headless_server/tests/headless_server/1.7.10_clean/world",
        server_jar="forge-1.7.10-10.13.4.1614-1.7.10-universal.jar",  # Adjust as needed
        rcon_port=25575,
        rcon_password="test123"
    ),
    "1.18.2": ServerConfig(
        version="1.18.2",
        server_dir="headless_server/1.18.2",
        clean_world_dir="headless_server/tests/headless_server/1.18.2_clean/world",
        server_jar="forge-1.18.2-40.2.0.jar",  # Adjust as needed
        rcon_port=25576,  # Different port to avoid conflicts
        rcon_password="test123"
    )
}


class HeadlessTestOrchestrator:
    """
    Orchestrates complete headless testing workflow.
    """

    def __init__(self, config: ServerConfig, verbose: bool = True):
        self.config = config
        self.verbose = verbose
        self.server_process: Optional[subprocess.Popen] = None
        self.rcon: Optional[RconClient] = None
        self.results: Dict[str, Any] = {
            "version": config.version,
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "errors": [],
            "summary": {}
        }

    def log(self, msg: str, level: str = "INFO"):
        """Log message"""
        if self.verbose or level == "ERROR":
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] [{level}] {msg}")

    def log_section(self, title: str):
        """Log section header"""
        print()
        print("=" * 60)
        print(f" {title}")
        print("=" * 60)

    # =========================================================================
    # Step 1: Prepare World
    # =========================================================================

    def prepare_world(self, patch_path: str) -> bool:
        """
        Prepare test world by copying clean world and applying patch.

        Note: For full patch application, use Kotlin worker.
        For quick tests, use RCON /setblock after server starts.
        """
        self.log_section("STEP 1: Prepare World")

        world_dir = Path(PROJECT_ROOT) / self.config.server_dir / self.config.world_name

        # Option 1: Copy clean world if available
        if self.config.clean_world_dir:
            clean_dir = Path(PROJECT_ROOT) / self.config.clean_world_dir
            if clean_dir.exists():
                self.log(f"Copying clean world from {clean_dir}")
                if world_dir.exists():
                    shutil.rmtree(world_dir)
                shutil.copytree(clean_dir, world_dir)
                self.log("Clean world copied")
            else:
                self.log(f"Clean world not found at {clean_dir}", "WARN")

        # Option 2: Apply patch using Kotlin worker
        # This requires the worker JAR to be built
        kotlin_worker = Path(PROJECT_ROOT) / "jvm" / "worker" / "mc-editkit-worker.jar"
        if kotlin_worker.exists() and Path(patch_path).exists():
            self.log("Applying patch with Kotlin worker...")
            cmd = [
                "java", "-jar", str(kotlin_worker),
                "--world", str(world_dir),
                "--patch", patch_path
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.log("Patch applied successfully")
                else:
                    self.log(f"Patch application failed: {result.stderr}", "WARN")
            except Exception as e:
                self.log(f"Kotlin worker not available: {e}", "WARN")
                self.log("Will deploy via RCON instead")
        else:
            self.log("Kotlin worker not available - will deploy via RCON")

        return True

    # =========================================================================
    # Step 2: Start Server
    # =========================================================================

    def start_server(self) -> bool:
        """Start headless Minecraft server"""
        self.log_section("STEP 2: Start Server")

        server_dir = Path(PROJECT_ROOT) / self.config.server_dir

        # Find server JAR
        server_jar = server_dir / self.config.server_jar
        if not server_jar.exists():
            # Try finding any JAR
            jars = list(server_dir.glob("*.jar"))
            forge_jars = [j for j in jars if "forge" in j.name.lower()]
            if forge_jars:
                server_jar = forge_jars[0]
            elif jars:
                server_jar = jars[0]
            else:
                self.log(f"No server JAR found in {server_dir}", "ERROR")
                return False

        self.log(f"Using server JAR: {server_jar.name}")

        # Ensure server.properties has RCON enabled
        props_path = server_dir / "server.properties"
        self._ensure_rcon_enabled(props_path)

        # Start server
        cmd = [
            "java",
            *self.config.java_args,
            "-jar", server_jar.name,
            "nogui"
        ]

        self.log(f"Starting: {' '.join(cmd[:5])}...")

        try:
            self.server_process = subprocess.Popen(
                cmd,
                cwd=str(server_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            self.log(f"Server started (PID: {self.server_process.pid})")
            return True

        except Exception as e:
            self.log(f"Failed to start server: {e}", "ERROR")
            return False

    def _ensure_rcon_enabled(self, props_path: Path):
        """Ensure server.properties has RCON enabled"""
        if not props_path.exists():
            self.log("Creating server.properties with RCON enabled")
            content = f"""
enable-rcon=true
rcon.password={self.config.rcon_password}
rcon.port={self.config.rcon_port}
server-port={self.config.server_port}
enable-command-block=true
online-mode=false
spawn-protection=0
"""
            props_path.write_text(content)
        else:
            # Verify RCON settings
            content = props_path.read_text()
            if "enable-rcon=true" not in content:
                self.log("Enabling RCON in server.properties")
                lines = content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("enable-rcon="):
                        new_lines.append("enable-rcon=true")
                    elif line.startswith("rcon.password="):
                        new_lines.append(f"rcon.password={self.config.rcon_password}")
                    elif line.startswith("rcon.port="):
                        new_lines.append(f"rcon.port={self.config.rcon_port}")
                    else:
                        new_lines.append(line)

                # Add missing settings
                if "enable-rcon" not in content:
                    new_lines.append("enable-rcon=true")
                if "rcon.password" not in content:
                    new_lines.append(f"rcon.password={self.config.rcon_password}")
                if "rcon.port" not in content:
                    new_lines.append(f"rcon.port={self.config.rcon_port}")
                if "enable-command-block" not in content:
                    new_lines.append("enable-command-block=true")

                props_path.write_text("\n".join(new_lines))

    # =========================================================================
    # Step 3: Wait for Ready
    # =========================================================================

    def wait_for_ready(self, timeout: float = 180.0) -> bool:
        """Wait for server to be ready"""
        self.log_section("STEP 3: Wait for Server Ready")

        log_path = Path(PROJECT_ROOT) / self.config.server_dir / "logs" / "latest.log"

        self.log(f"Waiting for server ready (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if process died
            if self.server_process and self.server_process.poll() is not None:
                self.log("Server process terminated unexpectedly", "ERROR")
                return False

            # Check logs
            if log_path.exists():
                parser = LogParser(str(log_path))
                status = parser.get_server_status()

                if status.started:
                    self.log(f"Server started at {status.start_time}")

                if status.rcon_ready:
                    self.log("RCON ready")

                    # Try connecting
                    try:
                        self.rcon = RconClient(
                            "127.0.0.1",
                            self.config.rcon_port,
                            self.config.rcon_password
                        )
                        if self.rcon.connect():
                            self.log("RCON connected!")
                            return True
                    except:
                        pass

                if status.errors:
                    for err in status.errors[-3:]:
                        self.log(f"Server error: {err[:100]}", "WARN")

            time.sleep(2)

        self.log("Timeout waiting for server", "ERROR")
        return False

    # =========================================================================
    # Step 4: Run Tests
    # =========================================================================

    def run_tests(self, patch_data: Dict[str, Any]) -> bool:
        """Run integration tests via RCON"""
        self.log_section("STEP 4: Run Integration Tests")

        if not self.rcon:
            self.log("RCON not connected", "ERROR")
            return False

        # Deploy simple test circuits first
        self._deploy_simple_tests()

        # Get integration tests from patch metadata
        structures = patch_data.get("metadata", {}).get("structures", [])
        integration_tests = [s for s in structures if s.get("type") == "integration"]

        self.log(f"Running {len(integration_tests)} integration tests...")

        log_path = Path(PROJECT_ROOT) / self.config.server_dir / "logs" / "latest.log"
        parser = LogParser(str(log_path))

        for struct in integration_tests:
            test_name = struct["name"]
            metadata = struct.get("metadata", {})
            test_info = metadata.get("test_info", {})
            activation = metadata.get("activation_point", {})

            self.log(f"  Running: {test_name}")

            result = {
                "name": test_name,
                "passed": False,
                "expected": test_info.get("expected_output", ""),
                "actual": None,
                "error": None
            }

            try:
                if activation:
                    x, y, z = activation["x"], activation["y"], activation["z"]
                    # Activate lever (powered state)
                    cmd = f"/setblock {x} {y} {z} minecraft:lever 13"
                    self.rcon.command(cmd)

                    # Wait for signal
                    time.sleep(2)

                    # Check for expected output
                    expected = result["expected"]
                    if expected:
                        found = parser.find_test_markers([expected])
                        if expected in found:
                            result["passed"] = True
                            result["actual"] = found[expected].full_message
                            self.log(f"    PASS: {expected}")
                        else:
                            self.log(f"    FAIL: {expected} not found")

                    # Reset lever
                    cmd = f"/setblock {x} {y} {z} minecraft:lever 5"
                    self.rcon.command(cmd)
                else:
                    result["error"] = "No activation point"

            except Exception as e:
                result["error"] = str(e)
                self.log(f"    ERROR: {e}", "ERROR")

            self.results["tests"].append(result)

        return True

    def _deploy_simple_tests(self):
        """Deploy simple vanilla redstone tests to verify basic functionality"""
        self.log("Deploying simple test circuits...")

        base_x, y, z = 500, 70, -100

        # Simple lever -> redstone -> command block
        for x in range(5):
            self.rcon.command(f"/setblock {base_x + x} {y - 1} {z} minecraft:stone")

        self.rcon.command(f"/setblock {base_x} {y} {z} minecraft:lever 5")
        self.rcon.command(f"/setblock {base_x + 1} {y} {z} minecraft:redstone_wire 0")
        self.rcon.command(f"/setblock {base_x + 2} {y} {z} minecraft:redstone_wire 0")
        self.rcon.command(f"/setblock {base_x + 3} {y} {z} minecraft:command_block 0")
        time.sleep(0.3)
        self.rcon.command(
            f'/blockdata {base_x + 3} {y} {z} '
            f'{{Command:"/say [TEST_BASIC_REDSTONE_OK] Basic redstone working"}}'
        )

        # Activate test
        time.sleep(0.5)
        self.rcon.command(f"/setblock {base_x} {y} {z} minecraft:lever 13")
        time.sleep(1)

        # Check result
        log_path = Path(PROJECT_ROOT) / self.config.server_dir / "logs" / "latest.log"
        parser = LogParser(str(log_path))
        found = parser.find_test_markers(["TEST_BASIC_REDSTONE_OK"])

        if "TEST_BASIC_REDSTONE_OK" in found:
            self.log("  Basic redstone test: PASS")
            self.results["tests"].append({
                "name": "basic_redstone",
                "passed": True,
                "expected": "TEST_BASIC_REDSTONE_OK"
            })
        else:
            self.log("  Basic redstone test: FAIL", "WARN")
            self.results["tests"].append({
                "name": "basic_redstone",
                "passed": False,
                "expected": "TEST_BASIC_REDSTONE_OK"
            })

    # =========================================================================
    # Step 5: Analyze & Report
    # =========================================================================

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        self.log_section("STEP 5: Generate Report")

        passed = sum(1 for t in self.results["tests"] if t.get("passed"))
        total = len(self.results["tests"])

        self.results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{passed / max(1, total) * 100:.1f}%"
        }

        # Save report
        output_dir = Path(PROJECT_ROOT) / "output" / "projectred_headless_test"
        output_dir.mkdir(parents=True, exist_ok=True)

        report_name = f"report_{self.config.version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = output_dir / report_name

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        self.log(f"Report saved: {report_path}")

        # Print summary
        print()
        print("=" * 60)
        print(f" TEST SUMMARY - Minecraft {self.config.version}")
        print("=" * 60)
        print(f" Total:   {total}")
        print(f" Passed:  {passed}")
        print(f" Failed:  {total - passed}")
        print(f" Success: {self.results['summary']['success_rate']}")
        print("=" * 60)
        print()
        print("Test Results:")
        for test in self.results["tests"]:
            status = "PASS" if test.get("passed") else "FAIL"
            print(f"  [{status}] {test['name']}")

        return self.results

    # =========================================================================
    # Step 6: Cleanup
    # =========================================================================

    def cleanup(self):
        """Stop server and cleanup"""
        self.log_section("CLEANUP")

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

        # Wait for server to stop
        if self.server_process:
            self.log("Waiting for server to stop...")
            try:
                self.server_process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.log("Terminating server...")
                self.server_process.terminate()
            self.server_process = None

        self.log("Cleanup complete")

    # =========================================================================
    # Main Run
    # =========================================================================

    def run(self, deploy_only: bool = False, test_only: bool = False) -> bool:
        """
        Run complete test workflow.

        Args:
            deploy_only: Only prepare world and deploy, don't start server
            test_only: Server already running, only run tests
        """
        try:
            # Generate patch
            patch_path = str(SCRIPT_DIR / "projectred_test_patch.json")
            if not Path(patch_path).exists():
                structures_dir = str(SCRIPT_DIR.parent / "generated")
                generate_projectred_test_patch(structures_dir, patch_path)

            with open(patch_path, 'r') as f:
                patch_data = json.load(f)

            if test_only:
                # Just run tests on already running server
                self.log("Test-only mode: connecting to running server...")
                self.rcon = RconClient("127.0.0.1", self.config.rcon_port, self.config.rcon_password)
                if not self.rcon.connect():
                    self.log("Failed to connect to server", "ERROR")
                    return False
                self.run_tests(patch_data)
                self.generate_report()
                return True

            # Full workflow
            if not self.prepare_world(patch_path):
                return False

            if deploy_only:
                self.log("Deploy-only mode: stopping here")
                return True

            if not self.start_server():
                return False

            if not self.wait_for_ready():
                return False

            self.run_tests(patch_data)
            self.generate_report()

            return self.results["summary"]["failed"] == 0

        finally:
            if not test_only:
                self.cleanup()


def main():
    parser = argparse.ArgumentParser(description="ProjectRed Headless Test Orchestrator")
    parser.add_argument("--version", default="1.7.10", choices=["1.7.10", "1.18.2"],
                        help="Minecraft version")
    parser.add_argument("--deploy-only", action="store_true",
                        help="Only prepare world, don't start server")
    parser.add_argument("--test-only", action="store_true",
                        help="Only run tests (server already running)")
    parser.add_argument("--verbose", "-v", action="store_true", default=True,
                        help="Verbose output")

    args = parser.parse_args()

    config = CONFIGS.get(args.version)
    if not config:
        print(f"Unknown version: {args.version}")
        sys.exit(1)

    orchestrator = HeadlessTestOrchestrator(config, verbose=args.verbose)
    success = orchestrator.run(
        deploy_only=args.deploy_only,
        test_only=args.test_only
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
