"""Wspolne helpery do konwersji UUID miedzy formatami 1.7.10 a 1.18.2."""

from __future__ import annotations

import uuid
from typing import List


def uuid_string_to_int_array(uuid_str: str) -> List[int]:
    """Konwertuje UUID string (1.7.10) na int[4] array (1.18.2).

    Format int-array uzywany od Minecraft 1.16+.
    Przyklad: "550e8400-e29b-41d4-a716-446655440000"
    -> [1427014656, 3801825748, 2803254374, 1430519808]
    """
    try:
        u = uuid.UUID(uuid_str)
    except ValueError:
        # Jesli string nie jest poprawnym UUID, generujemy nowy
        u = uuid.uuid4()

    msb = u.int >> 64
    lsb = u.int & 0xFFFFFFFFFFFFFFFF
    return [
        (msb >> 32) & 0xFFFFFFFF,
        msb & 0xFFFFFFFF,
        (lsb >> 32) & 0xFFFFFFFF,
        lsb & 0xFFFFFFFF,
    ]


def int_array_to_uuid_string(int_array: List[int]) -> str:
    """Konwertuje int[4] array (1.18.2) na UUID string."""
    if len(int_array) != 4:
        raise ValueError(f"int_array must have 4 elements, got {len(int_array)}")
    msb = (int_array[0] << 32) | int_array[1]
    lsb = (int_array[2] << 32) | int_array[3]
    u = uuid.UUID(int=(msb << 64) | lsb)
    return str(u)
