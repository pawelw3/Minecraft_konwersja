"""
RCON Client for Minecraft Server

Implementation of RCON protocol for remote control of Minecraft servers.
Based on: https://wiki.vg/RCON

Usage:
    client = RconClient("localhost", 25575, "password")
    client.connect()
    response = client.command("/say Hello!")
    client.disconnect()
"""

import socket
import struct
import time
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class PacketType(IntEnum):
    """RCON packet types"""
    RESPONSE = 0
    COMMAND = 2
    LOGIN = 3


@dataclass
class RconPacket:
    """RCON packet structure"""
    request_id: int
    packet_type: PacketType
    payload: str

    def encode(self) -> bytes:
        """Encode packet to bytes for sending"""
        payload_bytes = self.payload.encode('utf-8') + b'\x00'
        packet_data = struct.pack('<ii', self.request_id, self.packet_type) + payload_bytes + b'\x00'
        return struct.pack('<i', len(packet_data)) + packet_data

    @classmethod
    def decode(cls, data: bytes) -> 'RconPacket':
        """Decode bytes to packet"""
        if len(data) < 10:
            raise ValueError(f"Packet too short: {len(data)} bytes")

        request_id, packet_type = struct.unpack('<ii', data[:8])
        # Payload is null-terminated
        payload_end = data.find(b'\x00', 8)
        if payload_end == -1:
            payload = data[8:].decode('utf-8', errors='replace')
        else:
            payload = data[8:payload_end].decode('utf-8', errors='replace')

        return cls(
            request_id=request_id,
            packet_type=PacketType(packet_type),
            payload=payload
        )


class RconClient:
    """
    RCON client for Minecraft servers.

    Example:
        client = RconClient("localhost", 25575, "test123")
        if client.connect():
            result = client.command("/list")
            print(result)
            client.disconnect()
    """

    def __init__(self, host: str, port: int, password: str, timeout: float = 10.0):
        """
        Initialize RCON client.

        Args:
            host: Server hostname or IP
            port: RCON port (default Minecraft: 25575)
            password: RCON password
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.request_id = 0
        self.connected = False

    def _get_request_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    def _send_packet(self, packet: RconPacket) -> None:
        """Send packet to server"""
        if not self.socket:
            raise ConnectionError("Not connected")
        self.socket.sendall(packet.encode())

    def _recv_packet(self) -> RconPacket:
        """Receive packet from server"""
        if not self.socket:
            raise ConnectionError("Not connected")

        # Read packet length (4 bytes)
        length_data = self._recv_bytes(4)
        packet_length = struct.unpack('<i', length_data)[0]

        # Read packet data
        packet_data = self._recv_bytes(packet_length)
        return RconPacket.decode(packet_data)

    def _recv_bytes(self, count: int) -> bytes:
        """Receive exact number of bytes"""
        if not self.socket:
            raise ConnectionError("Not connected")

        data = b''
        while len(data) < count:
            chunk = self.socket.recv(count - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def connect(self) -> bool:
        """
        Connect and authenticate to server.

        Returns:
            True if connected and authenticated successfully
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

            # Send login packet
            login_packet = RconPacket(
                request_id=self._get_request_id(),
                packet_type=PacketType.LOGIN,
                payload=self.password
            )
            self._send_packet(login_packet)

            # Receive response
            response = self._recv_packet()

            # Request ID of -1 means authentication failed
            if response.request_id == -1:
                self.disconnect()
                return False

            self.connected = True
            return True

        except (socket.error, ConnectionError) as e:
            self.disconnect()
            raise ConnectionError(f"Failed to connect: {e}")

    def disconnect(self) -> None:
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False

    def command(self, cmd: str) -> str:
        """
        Execute command on server.

        Args:
            cmd: Minecraft command (with or without leading /)

        Returns:
            Command response string
        """
        if not self.connected:
            raise ConnectionError("Not connected")

        packet = RconPacket(
            request_id=self._get_request_id(),
            packet_type=PacketType.COMMAND,
            payload=cmd
        )
        self._send_packet(packet)

        response = self._recv_packet()
        return response.payload

    def say(self, message: str) -> str:
        """Send /say command"""
        return self.command(f"/say {message}")

    def setblock(self, x: int, y: int, z: int, block: str, meta: int = 0) -> str:
        """
        Place a block using /setblock command.

        Args:
            x, y, z: Block coordinates
            block: Block ID (e.g., "minecraft:redstone_torch")
            meta: Block metadata/data value
        """
        return self.command(f"/setblock {x} {y} {z} {block} {meta}")

    def tp(self, target: str, x: int, y: int, z: int) -> str:
        """Teleport target to coordinates"""
        return self.command(f"/tp {target} {x} {y} {z}")

    def wait_for_ready(self, max_retries: int = 30, delay: float = 2.0) -> bool:
        """
        Wait for server to be ready by attempting to connect.

        Args:
            max_retries: Maximum connection attempts
            delay: Delay between attempts in seconds

        Returns:
            True if connected successfully
        """
        for attempt in range(max_retries):
            try:
                if self.connect():
                    return True
            except ConnectionError:
                pass
            time.sleep(delay)
        return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def test_connection(host: str = "127.0.0.1", port: int = 25575, password: str = "test123"):
    """
    Test RCON connection to server.

    Args:
        host: Server host
        port: RCON port
        password: RCON password
    """
    print(f"Testing RCON connection to {host}:{port}...")

    try:
        with RconClient(host, port, password) as client:
            print("Connected!")

            # Test /list command
            result = client.command("/list")
            print(f"Players: {result}")

            # Test /say
            result = client.say("[TEST] RCON connection successful!")
            print(f"Say result: {result}")

            print("RCON test passed!")

    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        password = sys.argv[3]
    else:
        host = "127.0.0.1"
        port = 25575
        password = "test123"

    test_connection(host, port, password)
