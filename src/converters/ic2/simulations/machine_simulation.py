"""Symulacja konwersji maszyn IC2 StandardMachine → Mekanism/Thermal/indreb/ftbic 1.18.2.

Obsługuje:
- progress (short) → progress w 1.18.2 (zależnie od targetu)
- energy (double, EU) → energy (int/double, FE) z mnożnikiem ×4
- facing (short) → blockstate "facing"
- inventory (Items/InvSlots) → inventory (zależnie od targetu)
- active (boolean) → blockstate / NBT

Źródło:
- IC2 1.7.10: TileEntityStandardMachine (writeToNBT/readFromNBT)
- indreb 1.18.2: BlockEntityStandardMachine, IndRebBlockEntity (save/load)
- ftbic 1.18.2: MachineBlockEntity, ElectricBlockEntity (writeData/readData)
- Mekanism 1.18.2: TileEntityMekanism
- Thermal 1.18.2: MachineBlockEntity
"""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

# Mnożnik EU → FE
EU_TO_FE = 4.0

# Mapowanie facing IC2 1.7.10 → string 1.18.2
# IC2: 0=down, 1=up, 2=north, 3=south, 4=west, 5=east
IC2_FACING_TO_STRING = {
    0: "down",
    1: "up",
    2: "north",
    3: "south",
    4: "west",
    5: "east",
}

# Target-specific defaults
DEFAULT_TARGET_PROGRESS_TICKS = {
    "mekanism": 200,   # typowy czas pracy w Mekanism
    "thermal": 200,    # typowy czas w Thermal
    "minecraft": 200,  # dla vanilla (blast furnace)
}


def convert_energy_eu_to_fe(energy_eu: float) -> int:
    """Konwertuje energię EU na FE z zaokrągleniem w dół."""
    return max(0, int(math.floor(energy_eu * EU_TO_FE)))


def convert_facing(ic2_facing: int) -> str:
    """Konwertuje facing IC2 (0-5) na string 1.18.2."""
    return IC2_FACING_TO_STRING.get(ic2_facing, "north")


def extract_inventory(nbt_1710: dict[str, Any]) -> list[dict[str, Any]]:
    """Wyciąga inventory z NBT IC2 1.7.10.
    
    IC2 używa zarówno starego formatu 'Items' (NBTTagList) jak i nowego 'InvSlots'.
    Zwraca listę slotów w formacie 1.18.2-compatible.
    
    UWAGA: W formacie InvSlots indeksy są lokalne per-kategoria (input.0, output.0),
    więc mogą się duplikować. Użyj extract_inventory_indreb() dla poprawnego mapowania
    na globalne sloty indreb.
    """
    items = []
    
    # Nowy format InvSlots (preferowany)
    inv_slots = nbt_1710.get("InvSlots", {})
    if isinstance(inv_slots, dict):
        for slot_name, slot_data in inv_slots.items():
            if isinstance(slot_data, dict):
                for idx_str, stack in slot_data.items():
                    if isinstance(stack, dict) and stack.get("id"):
                        items.append({
                            "Slot": int(idx_str),
                            "id": stack.get("id"),
                            "Count": stack.get("Count", 1),
                            "tag": stack.get("tag", {}),
                        })
    
    # Stary format Items (fallback)
    if not items:
        legacy_items = nbt_1710.get("Items", [])
        if isinstance(legacy_items, list):
            for entry in legacy_items:
                if isinstance(entry, dict):
                    items.append({
                        "Slot": entry.get("Slot", 0),
                        "id": entry.get("id"),
                        "Count": entry.get("Count", 1),
                        "tag": entry.get("tag", {}),
                    })
    
    return items


def extract_inventory_indreb(nbt_1710: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Wyciąga inventory z NBT IC2 i mapuje na strukturę indreb.
    
    indreb używa osobnych handlerów:
    - inventory: input, output, bonus (ItemStackHandler)
    - battery: discharge, charge (ItemStackHandler)
    - upgrade: upgrade (ItemStackHandler)
    
    Zwraca dict z kluczami 'inventory', 'battery', 'upgrade'.
    """
    result: dict[str, list[dict[str, Any]]] = {
        "inventory": [],
        "battery": [],
        "upgrade": [],
    }
    
    inv_slots = nbt_1710.get("InvSlots", {})
    if isinstance(inv_slots, dict):
        slot_counter = 0
        for category in ("input", "output", "bonus", "cell"):
            slot_data = inv_slots.get(category, {})
            if isinstance(slot_data, dict):
                for idx_str, stack in sorted(slot_data.items(), key=lambda x: int(x[0])):
                    if isinstance(stack, dict) and stack.get("id"):
                        result["inventory"].append({
                            "Slot": slot_counter,
                            "id": stack.get("id"),
                            "Count": stack.get("Count", 1),
                            "tag": stack.get("tag", {}),
                        })
                        slot_counter += 1
        
        battery_counter = 0
        for category in ("discharge", "charge", "fuel"):
            slot_data = inv_slots.get(category, {})
            if isinstance(slot_data, dict):
                for idx_str, stack in sorted(slot_data.items(), key=lambda x: int(x[0])):
                    if isinstance(stack, dict) and stack.get("id"):
                        result["battery"].append({
                            "Slot": battery_counter,
                            "id": stack.get("id"),
                            "Count": stack.get("Count", 1),
                            "tag": stack.get("tag", {}),
                        })
                        battery_counter += 1
        
        upgrade_counter = 0
        for category in ("upgrade",):
            slot_data = inv_slots.get(category, {})
            if isinstance(slot_data, dict):
                for idx_str, stack in sorted(slot_data.items(), key=lambda x: int(x[0])):
                    if isinstance(stack, dict) and stack.get("id"):
                        result["upgrade"].append({
                            "Slot": upgrade_counter,
                            "id": stack.get("id"),
                            "Count": stack.get("Count", 1),
                            "tag": stack.get("tag", {}),
                        })
                        upgrade_counter += 1
    
    # Fallback do legacy Items
    if not any(result.values()):
        legacy_items = nbt_1710.get("Items", [])
        if isinstance(legacy_items, list):
            for entry in legacy_items:
                if isinstance(entry, dict):
                    result["inventory"].append({
                        "Slot": entry.get("Slot", 0),
                        "id": entry.get("id"),
                        "Count": entry.get("Count", 1),
                        "tag": entry.get("tag", {}),
                    })
    
    return result


def simulate_standard_machine_conversion(
    nbt_1710: dict[str, Any],
    target_block_id: str,
    source_block_id: str = "",
    source_metadata: int = 0,
) -> dict[str, Any]:
    """Symuluje konwersję maszyny IC2 StandardMachine na 1.18.2.
    
    Zwraca dict reprezentujący NBT 1.18.2 (CompoundTag) oraz blockstate props.
    """
    result = {
        "nbt_1182": {},
        "blockstate_props": {},
        "warnings": [],
        "errors": [],
    }
    
    # --- Facing ---
    ic2_facing = int(nbt_1710.get("facing", 2))
    result["blockstate_props"]["facing"] = convert_facing(ic2_facing)
    
    # --- Active state ---
    active = bool(nbt_1710.get("active", False))
    if target_block_id.startswith("minecraft:"):
        result["blockstate_props"]["lit"] = "true" if active else "false"
    elif target_block_id.startswith("thermal:"):
        result["blockstate_props"]["active"] = "true" if active else "false"
    elif target_block_id.startswith("indreb:"):
        # indreb: active jest w NBT (BlockEntityStandardMachine.save)
        result["nbt_1182"]["active"] = active
    elif target_block_id.startswith("ftbic:"):
        # ftbic: active jest w blockstate (ElectricBlock.ACTIVE), nie w NBT
        pass
    else:
        # Mekanism używa NBT / side config zamiast blockstate
        result["nbt_1182"]["active"] = active
    
    # --- Energy (EU → FE) ---
    energy_eu = float(nbt_1710.get("energy", 0.0))
    energy_fe = convert_energy_eu_to_fe(energy_eu)
    
    if target_block_id.startswith("mekanism:"):
        result["nbt_1182"]["energyContainer"] = {"stored": energy_fe}
    elif target_block_id.startswith("indreb:"):
        # indreb: flat int "energy" (IndRebBlockEntity.save)
        result["nbt_1182"]["energy"] = energy_fe
    elif target_block_id.startswith("ftbic:"):
        # ftbic: double "Energy" (ElectricBlockEntity.writeData)
        result["nbt_1182"]["Energy"] = float(energy_fe)
    else:
        result["nbt_1182"]["energy"] = energy_fe
    
    # --- Progress ---
    progress = int(nbt_1710.get("progress", 0))
    max_progress_ic2 = 400  # typowe dla IC2
    
    if target_block_id.startswith("thermal:"):
        max_progress_target = 200
        scaled_progress = int((progress / max_progress_ic2) * max_progress_target)
        result["nbt_1182"]["Process"] = scaled_progress
        result["nbt_1182"]["ProcessMax"] = max_progress_target
    elif target_block_id.startswith("mekanism:"):
        result["nbt_1182"]["operatingTicks"] = progress
    elif target_block_id.startswith("indreb:"):
        # indreb: progress jako CompoundTag {progress: float, progressMax: float}
        # BlockEntityProgress.serializeNBT()
        result["nbt_1182"]["progress"] = {
            "progress": float(progress),
            "progressMax": float(max_progress_ic2),
        }
    elif target_block_id.startswith("ftbic:"):
        # ftbic: double "Progress" i "MaxProgress" (MachineBlockEntity.writeData)
        result["nbt_1182"]["Progress"] = float(progress)
        result["nbt_1182"]["MaxProgress"] = float(max_progress_ic2)
    
    # --- Inventory ---
    items = extract_inventory(nbt_1710)
    if items:
        if target_block_id.startswith("indreb:"):
            # indreb: ItemStackHandler.serializeNBT() → {Size: int, Items: [...]}
            # Użyj extract_inventory_indreb dla poprawnego mapowania slotów
            indreb_inv = extract_inventory_indreb(nbt_1710)
            if indreb_inv["inventory"]:
                result["nbt_1182"]["inventory"] = {
                    "Size": len(indreb_inv["inventory"]),
                    "Items": indreb_inv["inventory"],
                }
            if indreb_inv["battery"]:
                result["nbt_1182"]["battery"] = {
                    "Size": len(indreb_inv["battery"]),
                    "Items": indreb_inv["battery"],
                }
            if indreb_inv["upgrade"]:
                result["nbt_1182"]["upgrade"] = {
                    "Size": len(indreb_inv["upgrade"]),
                    "Items": indreb_inv["upgrade"],
                }
        elif target_block_id.startswith("ftbic:"):
            # ftbic: ListTag "Inventory" z byte Slot (ElectricBlockEntity.writeData)
            for it in items:
                it["Slot"] = int(it["Slot"]) & 0xFF  # ensure byte range
            result["nbt_1182"]["Inventory"] = items
        else:
            # Thermal / Mekanism / vanilla: "Items" ListTag
            result["nbt_1182"]["Items"] = items
    
    # --- Redstone mode (jeśli obecne) ---
    redstone_mode = nbt_1710.get("redstoneMode")
    if redstone_mode is not None:
        if target_block_id.startswith("mekanism:"):
            result["nbt_1182"]["redstoneControl"] = int(redstone_mode)
        elif target_block_id.startswith("indreb:"):
            # indreb nie ma direct redstoneControl; invertRedstone jest wewnętrzne
            result["warnings"].append(
                "IC2-W-REDSTONE-MODE: indreb nie wspiera bezpośredniego mapowania redstoneMode."
            )
        elif target_block_id.startswith("ftbic:"):
            # ftbic nie zapisuje redstone mode w NBT
            result["warnings"].append(
                "IC2-W-REDSTONE-MODE: ftbic nie wspiera bezpośredniego mapowania redstoneMode."
            )
    
    # --- Warnings ---
    if progress > 0 and not items:
        result["warnings"].append(
            "IC2-W-PROGRESS-NO-ITEMS: Maszyna ma progress ale brak itemów w inventory"
        )
    
    return result


def simulate_teleporter_conversion(
    nbt_1710: dict[str, Any],
) -> dict[str, Any]:
    """Symulacja konwersji Teleportera IC2 → Mekanism Teleporter.
    
    IC2: targetSet (bool), targetX/Y/Z (int)
    Mekanism: frequency (CompoundTag) z 'publicCache' lub 'securityMode'
    """
    result = {
        "nbt_1182": {},
        "blockstate_props": {},
        "warnings": [],
        "errors": [],
    }
    
    # Facing
    ic2_facing = int(nbt_1710.get("facing", 2))
    result["blockstate_props"]["facing"] = convert_facing(ic2_facing)
    
    # Energia
    energy_eu = float(nbt_1710.get("energy", 0.0))
    result["nbt_1182"]["energyContainer"] = {"stored": convert_energy_eu_to_fe(energy_eu)}
    
    # Współrzędne celu
    target_set = bool(nbt_1710.get("targetSet", False))
    if target_set:
        tx = nbt_1710.get("targetX", 0)
        ty = nbt_1710.get("targetY", 0)
        tz = nbt_1710.get("targetZ", 0)
        # Mekanism przechowuje frequency; współrzędne są w innym systemie
        result["nbt_1182"]["legacy_target"] = [tx, ty, tz]
        result["warnings"].append(
            "IC2-W-TELEPORTER-TARGET: Współrzędne celu zapisane w NBT, "
            "wymagana ręczna konfiguracja w Mekanism"
        )
    
    return result


def simulate_reactor_conversion(
    nbt_1710: dict[str, Any],
    target_block_id: str = "biggerreactors:reactor_casing",
) -> dict[str, Any]:
    """Symulacja konwersji reaktora IC2.
    
    UWAGA: Brak 1:1 odpowiednika. Zachowujemy oryginalne NBT jako 'legacy_data'.
    """
    result = {
        "nbt_1182": {},
        "blockstate_props": {},
        "warnings": [],
        "errors": [],
    }
    
    heat = int(nbt_1710.get("heat", 0))
    energy_eu = float(nbt_1710.get("energy", 0.0))
    
    result["nbt_1182"]["legacy_ic2_heat"] = heat
    result["nbt_1182"]["legacy_ic2_energy"] = convert_energy_eu_to_fe(energy_eu)
    
    # Zachowaj oryginalne inventory komponentów reaktora
    items = extract_inventory(nbt_1710)
    if items:
        result["nbt_1182"]["legacy_ic2_items"] = items
    
    result["warnings"].append(
        "IC2-W-REACTOR-NO-1:1: Nuclear reactor components require manual rebuild. "
        f"Original heat={heat} EU-buffer={energy_eu}. "
        f"Saved {len(items)} component stacks as legacy data."
    )
    
    return result
