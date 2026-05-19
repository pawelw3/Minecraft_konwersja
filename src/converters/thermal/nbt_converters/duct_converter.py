"""Konwerter NBT dla ductow Thermal Dynamics.

W 1.7.10 ducty sa Tile Entities z sieciami (grids).
W 1.18.2:
- energy_duct / fluid_duct / fluid_duct_windowed — proste BE
- item_buffer — zamiast itemductow
- Mekanism fallback: logistical_transporter dla itemow

Duct NBT w 1.7.10:
- Con (byte) - maska polaczen (6 bitow dla 6 stron)
- Type (byte) - typ/tier ducta
- Item / Fluid / Energy - dane transportowane
- Attachment data - servo, filter, cover
"""

from __future__ import annotations

from .base_converter import build_base_nbt_1182


def convert_energy_duct_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje energy duct (FluxDuct) na 1.18.2.

    W 1.18.2 energy_duct jest prostym blockiem bez zlozonego NBT.
    Zachowujemy tylko podstawowe informacje.
    """
    result = build_base_nbt_1182(nbt_1710, target_id)

    # Maska polaczen (opcjonalnie do odtworzenia modelu)
    con = nbt_1710.get("Con", 0)
    result["connections"] = int(con)

    # Usun zbedne pola (ducty w 1.18.2 nie maja energy/Items)
    result.pop("energy", None)
    result.pop("Items", None)
    result.pop("augments", None)
    result.pop("side_config", None)
    result.pop("redstone_control", None)

    return result


def convert_fluid_duct_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje fluid duct na 1.18.2.

    W 1.18.2 fluid_duct moze przechowywac mala ilosc plynu.
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    con = nbt_1710.get("Con", 0)
    result["connections"] = int(con)

    # Fluid w duct (jesli byl)
    fluid = nbt_1710.get("Fluid", {})
    if isinstance(fluid, dict):
        result["fluid"] = {
            "FluidName": fluid.get("FluidName", ""),
            "Amount": fluid.get("Amount", 0),
        }

    result.pop("energy", None)
    result.pop("Items", None)
    result.pop("augments", None)
    result.pop("side_config", None)
    result.pop("redstone_control", None)

    return result


def convert_item_duct_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje item duct na 1.18.2 lub Mekanism fallback.

    W 1.18.2 Thermal: item_buffer (magazynuje itemy, nie transportuje).
    W Mekanism fallback: basic_logistical_transporter.
    """
    result = build_base_nbt_1182(nbt_1710, target_id)
    con = nbt_1710.get("Con", 0)
    result["connections"] = int(con)

    # Item w duct (jaki byl transportowany)
    item = nbt_1710.get("Item", {})
    if isinstance(item, dict):
        result["transiting_item"] = {
            "id": item.get("id", ""),
            "Count": item.get("Count", 1),
        }

    # Attachment info (servo/filter/retriever)
    attachment = nbt_1710.get("Attachment", {})
    if isinstance(attachment, dict):
        result["legacy_attachment"] = {
            "type": attachment.get("type", ""),
            "tier": attachment.get("tier", 0),
        }

    result.pop("energy", None)
    result.pop("augments", None)
    result.pop("side_config", None)
    result.pop("redstone_control", None)

    return result


def convert_tesseract_nbt(nbt_1710: dict, target_id: str) -> dict:
    """Konwertuje Tesseract (1.7.10) -> Quantum Entangloporter (Mekanism 1.18.2).

    Tesseract NBT:
    - Frequency (string/int) - kanal
    - ModeItem, ModeFluid, ModeEnergy (byte) - tryby przesylu
    - Access (byte) - public/private/restricted

    Quantum Entangloporter NBT (Mekanism):
    - frequency (CompoundTag) z color1-4, name, securityMode, trusted
    - ejector (CompoundTag) - auto-eject settings
    """
    result = build_base_nbt_1182(nbt_1710, target_id)

    # Frequency
    freq = nbt_1710.get("Frequency", 0)
    if isinstance(freq, int):
        # Simple numeric frequency -> name-based
        result["frequency"] = {
            "name": f"thermal_tesseract_{freq}",
            "color1": freq % 16,
            "color2": (freq // 16) % 16,
            "color3": 0,
            "color4": 0,
            "securityMode": "PUBLIC",  # default
        }
    elif isinstance(freq, str):
        result["frequency"] = {
            "name": freq,
            "color1": 0, "color2": 0, "color3": 0, "color4": 0,
            "securityMode": "PUBLIC",
        }

    # Tryby przesylu
    mode_item = nbt_1710.get("ModeItem", 1)
    mode_fluid = nbt_1710.get("ModeFluid", 1)
    mode_energy = nbt_1710.get("ModeEnergy", 1)
    result["mode_item"] = bool(mode_item)
    result["mode_fluid"] = bool(mode_fluid)
    result["mode_energy"] = bool(mode_energy)
    result["mode_chemical"] = False  # Mekanism dodaje chemical

    # Access
    access = nbt_1710.get("Access", 0)
    access_map = {0: "PUBLIC", 1: "PRIVATE", 2: "TRUSTED"}
    result["security_mode"] = access_map.get(access, "PUBLIC")

    # Usun Items (Tesseract nie przechowuje)
    result.pop("Items", None)
    result.pop("augments", None)
    result.pop("energy", None)
    result.pop("side_config", None)
    result.pop("redstone_control", None)

    return result
