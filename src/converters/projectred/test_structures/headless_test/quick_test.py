"""
Quick Test Runner for ProjectRed

Runs tests on an already running Minecraft server.
Does not start/stop server - assumes server is already up with RCON enabled.

Usage:
    # Test connection
    python quick_test.py --action ping

    # Deploy test blocks using setblock commands
    python quick_test.py --action deploy

    # Run integration tests
    python quick_test.py --action test

    # Full workflow (deploy + test)
    python quick_test.py --action full

    # Custom server
    python quick_test.py --host 127.0.0.1 --port 25575 --password test123 --action test
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from src.converters.projectred.test_structures.headless_test.rcon_client import RconClient
from src.converters.projectred.test_structures.headless_test.log_parser import LogParser, TestResult
from src.converters.projectred.test_structures.headless_test.patch_generator import (
    load_structures_from_dir, PatchGenerator
)


class QuickTestRunner:
    """
    Quick test runner for already running server.
    """

    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 25575,
            password: str = "test123",
            log_path: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.password = password
        self.log_path = log_path or "headless_server/1.7.10/logs/latest.log"
        self.rcon: Optional[RconClient] = None
        self.structures_dir = Path(__file__).parent.parent / "generated"

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp"""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")

    def connect(self) -> bool:
        """Connect to server via RCON"""
        self.log(f"Connecting to {self.host}:{self.port}...")
        try:
            self.rcon = RconClient(self.host, self.port, self.password)
            if self.rcon.connect():
                self.log("Connected!")
                return True
            else:
                self.log("Authentication failed", "ERROR")
                return False
        except Exception as e:
            self.log(f"Connection failed: {e}", "ERROR")
            return False

    def disconnect(self):
        """Disconnect from server"""
        if self.rcon:
            self.rcon.disconnect()
            self.rcon = None

    def ping(self) -> bool:
        """Test connection with /list command"""
        if not self.connect():
            return False

        try:
            result = self.rcon.command("/list")
            self.log(f"Server response: {result}")
            self.rcon.say("[QUICK_TEST] Connection OK!")
            return True
        except Exception as e:
            self.log(f"Ping failed: {e}", "ERROR")
            return False
        finally:
            self.disconnect()

    def deploy_simple_test(self, offset_x: int = 600, offset_y: int = 70, offset_z: int = -100) -> bool:
        """
        Deploy a simple redstone test circuit using /setblock.

        Circuit: Lever -> Redstone -> Command Block

        This bypasses the need for Kotlin worker for basic testing.
        """
        if not self.connect():
            return False

        try:
            self.log("Deploying simple test circuit...")

            # Base layer (stone)
            for x in range(5):
                cmd = f"/setblock {offset_x + x} {offset_y - 1} {offset_z} minecraft:stone"
                self.rcon.command(cmd)

            # Lever (initially off)
            cmd = f"/setblock {offset_x} {offset_y} {offset_z} minecraft:lever 5"
            result = self.rcon.command(cmd)
            self.log(f"Lever: {result}")

            # Redstone dust
            cmd = f"/setblock {offset_x + 1} {offset_y} {offset_z} minecraft:redstone_wire 0"
            result = self.rcon.command(cmd)
            self.log(f"Redstone: {result}")

            cmd = f"/setblock {offset_x + 2} {offset_y} {offset_z} minecraft:redstone_wire 0"
            self.rcon.command(cmd)

            # Command block with test message
            # First place the block
            cmd = f"/setblock {offset_x + 3} {offset_y} {offset_z} minecraft:command_block 0"
            result = self.rcon.command(cmd)
            self.log(f"Command block: {result}")

            # Set command using blockdata (1.7.10+)
            time.sleep(0.5)
            cmd = f'/blockdata {offset_x + 3} {offset_y} {offset_z} {{Command:"/say [QUICK_TEST_OK] Simple circuit working!"}}'
            result = self.rcon.command(cmd)
            self.log(f"Blockdata: {result}")

            self.log(f"Test circuit deployed at ({offset_x}, {offset_y}, {offset_z})")
            self.log(f"Activate lever at ({offset_x}, {offset_y}, {offset_z}) to test")

            return True

        except Exception as e:
            self.log(f"Deploy failed: {e}", "ERROR")
            return False
        finally:
            self.disconnect()

    def deploy_integration_tests(self, start_x: int = 600, y: int = 70, z: int = -100) -> Dict[str, Dict]:
        """
        Deploy integration test circuits using /setblock.

        Returns dict of test names to their activation coordinates.
        """
        if not self.connect():
            return {}

        tests = {}
        current_x = start_x

        try:
            # Test 1: Simple AND simulation (two levers -> redstone -> command block)
            test_name = "simple_redstone_test"
            self.log(f"Deploying: {test_name}")

            # Base
            for x in range(5):
                self.rcon.command(f"/setblock {current_x + x} {y - 1} {z} minecraft:stone")

            # Lever
            self.rcon.command(f"/setblock {current_x} {y} {z} minecraft:lever 5")

            # Redstone
            self.rcon.command(f"/setblock {current_x + 1} {y} {z} minecraft:redstone_wire 0")
            self.rcon.command(f"/setblock {current_x + 2} {y} {z} minecraft:redstone_wire 0")

            # Command block
            self.rcon.command(f"/setblock {current_x + 3} {y} {z} minecraft:command_block 0")
            time.sleep(0.3)
            self.rcon.command(f'/blockdata {current_x + 3} {y} {z} {{Command:"/say [TEST_SIMPLE_OK] Basic redstone working"}}')

            tests[test_name] = {
                "activation": {"x": current_x, "y": y, "z": z, "type": "lever"},
                "expected": "TEST_SIMPLE_OK"
            }
            current_x += 10

            # Test 2: With repeater (signal propagation)
            test_name = "repeater_test"
            self.log(f"Deploying: {test_name}")

            for x in range(7):
                self.rcon.command(f"/setblock {current_x + x} {y - 1} {z} minecraft:stone")

            self.rcon.command(f"/setblock {current_x} {y} {z} minecraft:lever 5")
            self.rcon.command(f"/setblock {current_x + 1} {y} {z} minecraft:redstone_wire 0")
            # Repeater facing east (toward x+)
            self.rcon.command(f"/setblock {current_x + 2} {y} {z} minecraft:unpowered_repeater 1")
            self.rcon.command(f"/setblock {current_x + 3} {y} {z} minecraft:redstone_wire 0")
            self.rcon.command(f"/setblock {current_x + 4} {y} {z} minecraft:redstone_wire 0")
            self.rcon.command(f"/setblock {current_x + 5} {y} {z} minecraft:command_block 0")
            time.sleep(0.3)
            self.rcon.command(f'/blockdata {current_x + 5} {y} {z} {{Command:"/say [TEST_REPEATER_OK] Repeater working"}}')

            tests[test_name] = {
                "activation": {"x": current_x, "y": y, "z": z, "type": "lever"},
                "expected": "TEST_REPEATER_OK"
            }
            current_x += 12

            # Test 3: Torch inverter (NOT gate equivalent)
            test_name = "torch_inverter_test"
            self.log(f"Deploying: {test_name}")

            for x in range(6):
                self.rcon.command(f"/setblock {current_x + x} {y - 1} {z} minecraft:stone")

            self.rcon.command(f"/setblock {current_x} {y} {z} minecraft:lever 5")
            self.rcon.command(f"/setblock {current_x + 1} {y} {z} minecraft:redstone_wire 0")
            # Torch on side of block (acts as NOT)
            self.rcon.command(f"/setblock {current_x + 2} {y} {z} minecraft:stone")
            self.rcon.command(f"/setblock {current_x + 2} {y + 1} {z} minecraft:redstone_torch 5")  # On top
            self.rcon.command(f"/setblock {current_x + 3} {y + 1} {z} minecraft:redstone_wire 0")
            self.rcon.command(f"/setblock {current_x + 3} {y} {z} minecraft:stone")
            self.rcon.command(f"/setblock {current_x + 4} {y + 1} {z} minecraft:command_block 0")
            time.sleep(0.3)
            # This fires when lever is OFF (torch provides signal)
            self.rcon.command(f'/blockdata {current_x + 4} {y + 1} {z} {{Command:"/say [TEST_INVERTER_OK] Inverter working"}}')

            tests[test_name] = {
                "activation": {"x": current_x, "y": y, "z": z, "type": "lever"},
                "expected": "TEST_INVERTER_OK",
                "note": "Output expected when lever OFF"
            }

            self.log(f"Deployed {len(tests)} test circuits")
            return tests

        except Exception as e:
            self.log(f"Deploy failed: {e}", "ERROR")
            return tests
        finally:
            self.disconnect()

    def run_tests(self, tests: Dict[str, Dict], delay: float = 2.0) -> Dict[str, bool]:
        """
        Run tests by activating levers and checking logs.

        Args:
            tests: Dict from deploy_integration_tests
            delay: Seconds to wait after activation

        Returns:
            Dict of test_name -> passed
        """
        if not self.connect():
            return {}

        results = {}

        try:
            for test_name, test_info in tests.items():
                self.log(f"Running: {test_name}")

                activation = test_info["activation"]
                expected = test_info["expected"]
                x, y, z = activation["x"], activation["y"], activation["z"]

                # Toggle lever ON
                # Lever meta: facing | 0x8 for powered
                # 5 = facing east, 5 | 8 = 13 powered
                cmd = f"/setblock {x} {y} {z} minecraft:lever 13"
                self.rcon.command(cmd)

                # Wait for signal
                time.sleep(delay)

                # Check logs
                parser = LogParser(self.log_path)
                found = parser.find_test_markers([expected])

                if expected in found:
                    self.log(f"  PASS: Found {expected}")
                    results[test_name] = True
                else:
                    self.log(f"  FAIL: {expected} not found")
                    results[test_name] = False

                # Toggle lever OFF for next test
                cmd = f"/setblock {x} {y} {z} minecraft:lever 5"
                self.rcon.command(cmd)
                time.sleep(0.5)

            return results

        except Exception as e:
            self.log(f"Test run failed: {e}", "ERROR")
            return results
        finally:
            self.disconnect()

    def full_test(self) -> bool:
        """Run full deploy + test cycle"""
        self.log("=" * 50)
        self.log("QUICK TEST - Full Cycle")
        self.log("=" * 50)

        # Deploy
        tests = self.deploy_integration_tests()
        if not tests:
            self.log("Deploy failed", "ERROR")
            return False

        # Give time for blocks to settle
        time.sleep(1)

        # Run tests
        results = self.run_tests(tests)

        # Summary
        passed = sum(1 for v in results.values() if v)
        total = len(results)

        self.log("")
        self.log("=" * 50)
        self.log(f"RESULTS: {passed}/{total} passed")
        self.log("=" * 50)

        for name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.log(f"  [{status}] {name}")

        return passed == total


def main():
    parser = argparse.ArgumentParser(description="ProjectRed Quick Test Runner")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=25575, help="RCON port")
    parser.add_argument("--password", default="test123", help="RCON password")
    parser.add_argument("--log-path", default=None, help="Server log path")
    parser.add_argument(
        "--action",
        choices=["ping", "deploy", "test", "full"],
        default="ping",
        help="Action to perform"
    )

    args = parser.parse_args()

    runner = QuickTestRunner(
        host=args.host,
        port=args.port,
        password=args.password,
        log_path=args.log_path
    )

    if args.action == "ping":
        success = runner.ping()
    elif args.action == "deploy":
        runner.deploy_simple_test()
        success = True
    elif args.action == "test":
        tests = runner.deploy_integration_tests()
        results = runner.run_tests(tests)
        success = all(results.values()) if results else False
    elif args.action == "full":
        success = runner.full_test()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
