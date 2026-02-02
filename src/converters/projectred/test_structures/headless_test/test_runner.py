"""
ProjectRed Headless Server Test Runner

Automated testing workflow:
1. Generate patch from structures
2. Deploy patch to test world (via Kotlin worker)
3. Start headless server
4. Wait for server ready
5. Activate tests via RCON
6. Parse logs for test results
7. Generate report

Usage:
    python test_runner.py --version 1.7.10 --server-dir headless_server/1.7.10
    python test_runner.py --version 1.18.2 --server-dir headless_server/1.18.2
"""

import os
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient
from src.converters.projectred.test_structures.headless_test.log_parser import (
    LogParser, TestResult, verify_tests, print_test_results
)
from src.converters.projectred.test_structures.headless_test.patch_generator import (
    PatchGenerator, load_structures_from_dir, generate_projectred_test_patch
)


class TestPhase(Enum):
    """Test execution phase"""
    SETUP = "setup"
    DEPLOY = "deploy"
    START_SERVER = "start_server"
    WAIT_READY = "wait_ready"
    RUN_TESTS = "run_tests"
    COLLECT_RESULTS = "collect_results"
    CLEANUP = "cleanup"
    DONE = "done"


@dataclass
class TestConfig:
    """Test configuration"""
    # Paths
    server_dir: str = "headless_server/1.7.10"
    world_name: str = "world"
    structures_dir: str = "src/converters/projectred/test_structures/generated"
    output_dir: str = "output/projectred_headless_test"

    # Server settings
    minecraft_version: str = "1.7.10"
    java_path: str = "java"
    server_jar: str = "minecraft_server.jar"
    java_args: List[str] = field(default_factory=lambda: ["-Xms1G", "-Xmx2G"])

    # RCON settings
    rcon_host: str = "127.0.0.1"
    rcon_port: int = 25575
    rcon_password: str = "test123"

    # Timeouts
    server_start_timeout: float = 180.0  # 3 minutes
    test_timeout: float = 60.0  # Per test
    signal_propagation_delay: float = 2.0  # Delay after lever activation

    # Test placement
    start_offset: Tuple[int, int, int] = (600, 70, -100)
    structure_spacing: int = 15

    # Patch deployment (Kotlin worker)
    kotlin_worker_path: str = "jvm/worker/mc-editkit-worker.jar"


@dataclass
class TestRunResult:
    """Result of a single test run"""
    test_name: str
    result: TestResult
    timestamp: Optional[str] = None
    activation_command: Optional[str] = None
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TestReport:
    """Complete test report"""
    version: str
    timestamp: str
    config: Dict[str, Any]
    phase_results: Dict[str, bool] = field(default_factory=dict)
    test_results: List[TestRunResult] = field(default_factory=list)
    server_errors: List[str] = field(default_factory=list)
    total_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "config": self.config,
            "phase_results": self.phase_results,
            "test_results": [
                {
                    "name": r.test_name,
                    "result": r.result.value,
                    "timestamp": r.timestamp,
                    "expected": r.expected_output,
                    "actual": r.actual_output,
                    "error": r.error
                }
                for r in self.test_results
            ],
            "server_errors": self.server_errors,
            "total_time_seconds": self.total_time_seconds,
            "summary": self.get_summary()
        }

    def get_summary(self) -> Dict[str, Any]:
        passed = sum(1 for r in self.test_results if r.result == TestResult.PASSED)
        failed = sum(1 for r in self.test_results if r.result != TestResult.PASSED)
        return {
            "total": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": f"{passed / max(1, len(self.test_results)) * 100:.1f}%"
        }


class ProjectRedTestRunner:
    """
    Automated test runner for ProjectRed on headless Minecraft server.
    """

    def __init__(self, config: TestConfig):
        self.config = config
        self.report = TestReport(
            version=config.minecraft_version,
            timestamp=datetime.now().isoformat(),
            config={
                "server_dir": config.server_dir,
                "minecraft_version": config.minecraft_version,
                "rcon_port": config.rcon_port
            }
        )
        self.server_process: Optional[subprocess.Popen] = None
        self.rcon: Optional[RconClient] = None
        self.patch_data: Optional[Dict[str, Any]] = None
        self.current_phase = TestPhase.SETUP

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] {message}")

    def _phase(self, phase: TestPhase, success: bool):
        """Record phase result"""
        self.current_phase = phase
        self.report.phase_results[phase.value] = success
        status = "OK" if success else "FAILED"
        self.log(f"Phase {phase.value}: {status}")

    # =========================================================================
    # Phase 1: Setup - Generate patch
    # =========================================================================

    def setup(self) -> bool:
        """Generate test patch from structures"""
        self.log("Setting up test environment...")

        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Generate patch
            patch_path = os.path.join(self.config.output_dir, "test_patch.json")
            self.patch_data = generate_projectred_test_patch(
                self.config.structures_dir,
                patch_path,
                start_offset=self.config.start_offset,
                spacing=self.config.structure_spacing
            )

            self.log(f"Generated patch with {len(self.patch_data['edits'])} edits")
            self._phase(TestPhase.SETUP, True)
            return True

        except Exception as e:
            self.log(f"Setup failed: {e}", "ERROR")
            self._phase(TestPhase.SETUP, False)
            return False

    # =========================================================================
    # Phase 2: Deploy - Apply patch to world
    # =========================================================================

    def deploy(self) -> bool:
        """Deploy test structures to world"""
        self.log("Deploying structures to world...")

        try:
            world_path = os.path.join(self.config.server_dir, self.config.world_name)

            # For now, use /setblock via RCON after server starts
            # In production, this would use Kotlin worker
            self.log("Patch will be deployed via RCON after server starts")
            self._phase(TestPhase.DEPLOY, True)
            return True

        except Exception as e:
            self.log(f"Deploy failed: {e}", "ERROR")
            self._phase(TestPhase.DEPLOY, False)
            return False

    # =========================================================================
    # Phase 3: Start Server
    # =========================================================================

    def start_server(self) -> bool:
        """Start headless Minecraft server"""
        self.log(f"Starting server in {self.config.server_dir}...")

        try:
            server_jar = os.path.join(self.config.server_dir, self.config.server_jar)
            if not os.path.exists(server_jar):
                # Try finding any jar
                jars = list(Path(self.config.server_dir).glob("*.jar"))
                if jars:
                    server_jar = str(jars[0])
                else:
                    raise FileNotFoundError(f"No server JAR found in {self.config.server_dir}")

            cmd = [
                self.config.java_path,
                *self.config.java_args,
                "-jar", os.path.basename(server_jar),
                "nogui"
            ]

            self.log(f"Command: {' '.join(cmd)}")

            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.config.server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE
            )

            self.log(f"Server started (PID: {self.server_process.pid})")
            self._phase(TestPhase.START_SERVER, True)
            return True

        except Exception as e:
            self.log(f"Server start failed: {e}", "ERROR")
            self._phase(TestPhase.START_SERVER, False)
            return False

    # =========================================================================
    # Phase 4: Wait for Ready
    # =========================================================================

    def wait_ready(self) -> bool:
        """Wait for server to be ready"""
        self.log("Waiting for server to be ready...")

        try:
            log_path = os.path.join(self.config.server_dir, "logs", "latest.log")
            parser = LogParser(log_path)

            status = parser.wait_for_server_ready(
                timeout=self.config.server_start_timeout,
                poll_interval=2.0
            )

            if status.started and status.rcon_ready:
                self.log(f"Server ready at {status.start_time}")

                # Connect RCON
                self.rcon = RconClient(
                    self.config.rcon_host,
                    self.config.rcon_port,
                    self.config.rcon_password
                )
                if self.rcon.connect():
                    self.log("RCON connected")
                    self._phase(TestPhase.WAIT_READY, True)
                    return True
                else:
                    self.log("RCON connection failed", "ERROR")

            self.log(f"Server not ready: started={status.started}, rcon={status.rcon_ready}", "ERROR")
            self.report.server_errors.extend(status.errors)
            self._phase(TestPhase.WAIT_READY, False)
            return False

        except Exception as e:
            self.log(f"Wait ready failed: {e}", "ERROR")
            self._phase(TestPhase.WAIT_READY, False)
            return False

    # =========================================================================
    # Phase 5: Run Tests
    # =========================================================================

    def run_tests(self) -> bool:
        """Run all integration tests"""
        self.log("Running integration tests...")

        try:
            if not self.patch_data or not self.rcon:
                raise RuntimeError("Not ready to run tests")

            # Get integration tests
            structures = self.patch_data["metadata"].get("structures", [])
            integration_tests = [s for s in structures if s["type"] == "integration"]

            self.log(f"Found {len(integration_tests)} integration tests")

            for struct in integration_tests:
                test_name = struct["name"]
                self.log(f"Running: {test_name}")

                result = self._run_single_test(struct)
                self.report.test_results.append(result)

                status = "PASS" if result.result == TestResult.PASSED else "FAIL"
                self.log(f"  Result: {status}")

            self._phase(TestPhase.RUN_TESTS, True)
            return True

        except Exception as e:
            self.log(f"Run tests failed: {e}", "ERROR")
            self._phase(TestPhase.RUN_TESTS, False)
            return False

    def _run_single_test(self, struct: Dict[str, Any]) -> TestRunResult:
        """Run a single integration test"""
        test_name = struct["name"]
        metadata = struct.get("metadata", {})
        test_info = metadata.get("test_info", {})
        activation = metadata.get("activation_point", {})

        result = TestRunResult(
            test_name=test_name,
            result=TestResult.NOT_FOUND,
            expected_output=test_info.get("expected_output", "")
        )

        try:
            if not activation:
                result.error = "No activation point defined"
                result.result = TestResult.FAILED
                return result

            # Activate lever/button using RCON setblock
            x, y, z = activation["x"], activation["y"], activation["z"]
            block_type = activation.get("block_type", "minecraft:lever")

            if "lever" in block_type:
                # Toggle lever on: setblock with powered state
                # In 1.7.10: lever meta | 0x8 = powered
                cmd = f"/setblock {x} {y} {z} minecraft:lever 13"  # 5 | 8 = 13
            else:
                # Button: just place it (it will trigger)
                cmd = f"/setblock {x} {y} {z} minecraft:stone_button 5"

            result.activation_command = cmd
            self.rcon.command(cmd)

            # Wait for signal propagation
            time.sleep(self.config.signal_propagation_delay)

            # Check logs for expected output
            log_path = os.path.join(self.config.server_dir, "logs", "latest.log")
            parser = LogParser(log_path)

            expected = result.expected_output
            if expected:
                found = parser.find_test_markers([expected])
                if expected in found:
                    result.result = TestResult.PASSED
                    result.timestamp = found[expected].timestamp
                    result.actual_output = found[expected].full_message
                else:
                    result.result = TestResult.NOT_FOUND

        except Exception as e:
            result.error = str(e)
            result.result = TestResult.FAILED

        return result

    # =========================================================================
    # Phase 6: Collect Results
    # =========================================================================

    def collect_results(self) -> bool:
        """Collect and analyze test results"""
        self.log("Collecting results...")

        try:
            log_path = os.path.join(self.config.server_dir, "logs", "latest.log")
            parser = LogParser(log_path)

            # Get server status
            status = parser.get_server_status()
            self.report.server_errors.extend(status.errors)

            # Get all command block outputs
            outputs = parser.get_command_block_outputs()
            self.log(f"Found {len(outputs)} command block outputs")

            self._phase(TestPhase.COLLECT_RESULTS, True)
            return True

        except Exception as e:
            self.log(f"Collect results failed: {e}", "ERROR")
            self._phase(TestPhase.COLLECT_RESULTS, False)
            return False

    # =========================================================================
    # Phase 7: Cleanup
    # =========================================================================

    def cleanup(self) -> bool:
        """Stop server and cleanup"""
        self.log("Cleaning up...")

        try:
            # Disconnect RCON
            if self.rcon:
                try:
                    self.rcon.command("/stop")
                except:
                    pass
                self.rcon.disconnect()
                self.rcon = None

            # Wait for server to stop
            if self.server_process:
                self.log("Waiting for server to stop...")
                try:
                    self.server_process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    self.log("Server did not stop, terminating...")
                    self.server_process.terminate()
                self.server_process = None

            self._phase(TestPhase.CLEANUP, True)
            return True

        except Exception as e:
            self.log(f"Cleanup failed: {e}", "ERROR")
            self._phase(TestPhase.CLEANUP, False)
            return False

    # =========================================================================
    # Main Runner
    # =========================================================================

    def run(self) -> TestReport:
        """Run complete test workflow"""
        start_time = time.time()
        self.log("=" * 60)
        self.log(f"ProjectRed Headless Test - Minecraft {self.config.minecraft_version}")
        self.log("=" * 60)

        try:
            phases = [
                self.setup,
                self.deploy,
                self.start_server,
                self.wait_ready,
                self.run_tests,
                self.collect_results,
            ]

            for phase in phases:
                if not phase():
                    self.log(f"Stopping due to phase failure: {self.current_phase.value}", "ERROR")
                    break

        finally:
            self.cleanup()

        self.report.total_time_seconds = time.time() - start_time
        self._phase(TestPhase.DONE, True)

        # Print summary
        self._print_summary()

        # Save report
        self._save_report()

        return self.report

    def _print_summary(self):
        """Print test summary"""
        summary = self.report.get_summary()

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Version: {self.report.version}")
        print(f"Total tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']}")
        print(f"Time: {self.report.total_time_seconds:.1f}s")

        if self.report.server_errors:
            print(f"\nServer errors ({len(self.report.server_errors)}):")
            for err in self.report.server_errors[:5]:
                print(f"  - {err[:80]}")

        print("\nTest results:")
        for result in self.report.test_results:
            status = "PASS" if result.result == TestResult.PASSED else "FAIL"
            print(f"  [{status}] {result.test_name}")

    def _save_report(self):
        """Save report to JSON"""
        report_path = os.path.join(
            self.config.output_dir,
            f"test_report_{self.config.minecraft_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report.to_dict(), f, indent=2, ensure_ascii=False)
        self.log(f"Report saved: {report_path}")


def main():
    """Run ProjectRed headless tests"""
    import argparse

    parser = argparse.ArgumentParser(description="ProjectRed Headless Test Runner")
    parser.add_argument("--version", default="1.7.10", help="Minecraft version")
    parser.add_argument("--server-dir", default="headless_server/1.7.10", help="Server directory")
    parser.add_argument("--rcon-port", type=int, default=25575, help="RCON port")
    parser.add_argument("--rcon-password", default="test123", help="RCON password")

    args = parser.parse_args()

    config = TestConfig(
        server_dir=args.server_dir,
        minecraft_version=args.version,
        rcon_port=args.rcon_port,
        rcon_password=args.rcon_password
    )

    runner = ProjectRedTestRunner(config)
    report = runner.run()

    # Exit with error code if tests failed
    summary = report.get_summary()
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
