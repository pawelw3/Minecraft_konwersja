"""
Minecraft Server Log Parser

Parses server logs to find test markers and results.
"""

import re
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TestResult(Enum):
    """Test result status"""
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"


@dataclass
class LogEntry:
    """Parsed log entry"""
    timestamp: str
    thread: str
    level: str
    message: str
    raw_line: str


@dataclass
class TestMarker:
    """Test marker found in logs"""
    marker: str
    timestamp: str
    test_name: str
    full_message: str


@dataclass
class ServerStatus:
    """Server status from logs"""
    started: bool = False
    rcon_ready: bool = False
    world_loaded: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    start_time: Optional[str] = None


class LogParser:
    """
    Parser for Minecraft server logs.

    Example:
        parser = LogParser("server/logs/latest.log")
        status = parser.get_server_status()
        markers = parser.find_test_markers(["TEST_AND_GATE_OK", "TEST_OR_GATE_OK"])
    """

    # Pattern for standard Minecraft log lines
    # [HH:MM:SS] [Thread/LEVEL]: Message
    LOG_PATTERN = re.compile(
        r'\[(\d{2}:\d{2}:\d{2})\] \[([^\]]+)/(\w+)\]: (.+)'
    )

    # Pattern for test markers: [TEST_NAME] or TEST_NAME_OK
    TEST_MARKER_PATTERN = re.compile(
        r'\[?(TEST[\w_]+)\]?'
    )

    def __init__(self, log_path: str):
        """
        Initialize log parser.

        Args:
            log_path: Path to server log file
        """
        self.log_path = Path(log_path)
        self._cached_content: Optional[str] = None
        self._last_read_time: float = 0
        self._last_position: int = 0

    def _read_log(self, from_beginning: bool = True) -> str:
        """Read log file content"""
        if not self.log_path.exists():
            return ""

        with open(self.log_path, 'r', encoding='utf-8', errors='replace') as f:
            if from_beginning:
                return f.read()
            else:
                f.seek(self._last_position)
                content = f.read()
                self._last_position = f.tell()
                return content

    def _parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse single log line"""
        line = line.strip()
        if not line:
            return None

        match = self.LOG_PATTERN.match(line)
        if match:
            return LogEntry(
                timestamp=match.group(1),
                thread=match.group(2),
                level=match.group(3),
                message=match.group(4),
                raw_line=line
            )
        # Return raw line if pattern doesn't match
        return LogEntry(
            timestamp="",
            thread="",
            level="",
            message=line,
            raw_line=line
        )

    def parse_all(self) -> List[LogEntry]:
        """Parse all log entries"""
        content = self._read_log()
        entries = []
        for line in content.splitlines():
            entry = self._parse_line(line)
            if entry:
                entries.append(entry)
        return entries

    def get_server_status(self) -> ServerStatus:
        """
        Get server status from logs.

        Returns:
            ServerStatus with startup information
        """
        status = ServerStatus()
        entries = self.parse_all()

        for entry in entries:
            msg = entry.message.lower()

            # Server started
            if "done" in msg and "for help" in msg:
                status.started = True
                status.start_time = entry.timestamp

            # RCON ready
            if "rcon running" in msg or "rcon listener" in msg.lower():
                status.rcon_ready = True

            # World loaded
            if "preparing spawn area" in msg or "time elapsed" in msg:
                status.world_loaded = True

            # Errors
            if entry.level == "ERROR" or entry.level == "SEVERE":
                status.errors.append(entry.message)

            # Warnings
            if entry.level == "WARN":
                status.warnings.append(entry.message)

            # Chunk load errors
            if "couldn't load chunk" in msg or "chunk data corrupt" in msg:
                status.errors.append(entry.message)

        return status

    def find_test_markers(self, expected_markers: List[str]) -> Dict[str, TestMarker]:
        """
        Find test markers in logs.

        Args:
            expected_markers: List of marker strings to find (e.g., ["TEST_AND_GATE_OK"])

        Returns:
            Dict mapping marker name to TestMarker object
        """
        found: Dict[str, TestMarker] = {}
        entries = self.parse_all()

        for entry in entries:
            for marker in expected_markers:
                if marker in entry.message:
                    # Extract test name from marker
                    test_name = marker.replace("TEST_", "").replace("_OK", "")

                    found[marker] = TestMarker(
                        marker=marker,
                        timestamp=entry.timestamp,
                        test_name=test_name,
                        full_message=entry.message
                    )

        return found

    def wait_for_markers(
            self,
            expected_markers: List[str],
            timeout: float = 60.0,
            poll_interval: float = 0.5
    ) -> Dict[str, TestMarker]:
        """
        Wait for test markers to appear in logs.

        Args:
            expected_markers: List of markers to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Time between log checks

        Returns:
            Dict of found markers
        """
        start_time = time.time()
        found: Dict[str, TestMarker] = {}
        remaining = set(expected_markers)

        while time.time() - start_time < timeout and remaining:
            current_found = self.find_test_markers(list(remaining))
            found.update(current_found)
            remaining -= set(current_found.keys())

            if remaining:
                time.sleep(poll_interval)

        return found

    def wait_for_server_ready(
            self,
            timeout: float = 120.0,
            poll_interval: float = 2.0
    ) -> ServerStatus:
        """
        Wait for server to be ready.

        Args:
            timeout: Maximum wait time in seconds
            poll_interval: Time between checks

        Returns:
            ServerStatus when ready or after timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_server_status()
            if status.started and status.rcon_ready:
                return status
            time.sleep(poll_interval)

        return self.get_server_status()

    def find_errors_after(self, timestamp: str) -> List[str]:
        """Find errors that occurred after given timestamp"""
        errors = []
        entries = self.parse_all()
        found_timestamp = False

        for entry in entries:
            if entry.timestamp == timestamp:
                found_timestamp = True
                continue

            if found_timestamp:
                if entry.level in ("ERROR", "SEVERE"):
                    errors.append(entry.message)

        return errors

    def get_command_block_outputs(self) -> List[str]:
        """Get all command block outputs (messages starting with [@])"""
        outputs = []
        entries = self.parse_all()

        for entry in entries:
            if entry.message.startswith("[@]") or entry.message.startswith("[Server]"):
                outputs.append(entry.message)

        return outputs

    def tail(self, lines: int = 50) -> List[str]:
        """Get last N lines of log"""
        content = self._read_log()
        all_lines = content.splitlines()
        return all_lines[-lines:] if len(all_lines) > lines else all_lines


def verify_tests(
        log_path: str,
        test_expectations: Dict[str, str],
        timeout: float = 60.0
) -> Dict[str, Tuple[TestResult, Optional[TestMarker]]]:
    """
    Verify multiple tests against log file.

    Args:
        log_path: Path to server log
        test_expectations: Dict of {test_name: expected_marker}
        timeout: Timeout for waiting

    Returns:
        Dict of {test_name: (result, marker_or_none)}

    Example:
        results = verify_tests("logs/latest.log", {
            "and_gate": "TEST_AND_GATE_OK",
            "or_gate": "TEST_OR_GATE_OK"
        })
    """
    parser = LogParser(log_path)
    markers = list(test_expectations.values())

    # Wait for markers
    found = parser.wait_for_markers(markers, timeout=timeout)

    # Build results
    results = {}
    for test_name, expected_marker in test_expectations.items():
        if expected_marker in found:
            results[test_name] = (TestResult.PASSED, found[expected_marker])
        else:
            results[test_name] = (TestResult.NOT_FOUND, None)

    return results


def print_test_results(results: Dict[str, Tuple[TestResult, Optional[TestMarker]]]):
    """Pretty print test results"""
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    for test_name, (result, marker) in sorted(results.items()):
        if result == TestResult.PASSED:
            status = "[PASS]"
            passed += 1
            timestamp = marker.timestamp if marker else ""
            print(f"  {status} {test_name} @ {timestamp}")
        else:
            status = "[FAIL]"
            failed += 1
            print(f"  {status} {test_name}")

    print(f"\n" + "-" * 60)
    print(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    print(f"Success rate: {passed / (passed + failed) * 100:.1f}%")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python log_parser.py <log_path> [marker1 marker2 ...]")
        sys.exit(1)

    log_path = sys.argv[1]
    parser = LogParser(log_path)

    print(f"Parsing: {log_path}\n")

    # Get server status
    status = parser.get_server_status()
    print(f"Server started: {status.started}")
    print(f"RCON ready: {status.rcon_ready}")
    print(f"Errors: {len(status.errors)}")

    if len(sys.argv) > 2:
        markers = sys.argv[2:]
        print(f"\nSearching for markers: {markers}")
        found = parser.find_test_markers(markers)
        for marker, info in found.items():
            print(f"  Found: {marker} at {info.timestamp}")

    # Show command block outputs
    outputs = parser.get_command_block_outputs()
    if outputs:
        print(f"\nCommand block outputs ({len(outputs)}):")
        for output in outputs[-10:]:  # Last 10
            print(f"  {output}")
