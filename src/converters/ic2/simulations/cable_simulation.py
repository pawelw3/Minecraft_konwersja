"""Symulacja konwersji kabli IC2 → Mekanism/indreb 1.18.2.

Obsługuje:
- cableType → tier kabla (basic/advanced/elite/ultimate)
- color → brak bezpośredniego odpowiednika
- foamed/foamColor → brak odpowiednika
- retexture → brak odpowiednika
- connectivity → brak NBT (kable obliczają połączenia dynamicznie)

Źródła:
- IC2 1.7.10: TileEntityCable (writeToNBT)
- indreb 1.18.2: BlockEntityCable (brak override save/load — brak NBT!)
- Mekanism 1.18.2: brak NBT dla kabli
"""

from __future__ import annotations

from typing import Any

# Mapowanie cableType IC2 → tier Mekanism
CABLE_TIER_MAP = {
    0: "basic",    # Insulated Copper
    1: "basic",    # Copper
    2: "advanced", # Gold
    3: "advanced", # Insulated Gold
    4: "advanced", # Double Insulated Gold
    5: "elite",    # Iron (HV)
    6: "elite",    # Insulated Iron
    7: "elite",    # Double Insulated Iron
    8: "elite",    # Triple Insulated Iron
    9: "ultimate", # Glass Fibre
    10: "basic",   # Tin
    11: "ultimate",# Detector Cable
    12: "ultimate",# Splitter Cable
    13: "basic",   # Insulated Tin
}

# Wartości energii na tick (uproszczone, dla informacji)
CABLE_TIER_CAPACITY = {
    "basic": 3200,
    "advanced": 12800,
    "elite": 51200,
    "ultimate": 204800,
}


def simulate_cable_conversion(
    nbt_1710: dict[str, Any],
    target_block_id: str,
) -> dict[str, Any]:
    """Konwertuje kabel IC2 na Universal Cable Mekanism.
    
    W Mekanism kable są zazwyczaj prostymi blokami bez NBT (connectivity 
    obliczana dynamicznie). Funkcja zwraca głównie blockstate_props i ostrzeżenia.
    """
    result = {
        "nbt_1182": {},
        "blockstate_props": {},
        "warnings": [],
        "errors": [],
    }
    
    cable_type = int(nbt_1710.get("cableType", 0))
    color = int(nbt_1710.get("color", 0))
    foamed = int(nbt_1710.get("foamed", 0))
    foam_color = int(nbt_1710.get("foamColor", 0))
    
    # --- Target-specific handling ---
    if target_block_id.startswith("indreb:"):
        # indreb cables: BlockEntityCable NIE override'uje save/load
        # Kable nie zapisują ŻADNEGO stanu w NBT — połączenia są dynamiczne
        pass
    elif target_block_id.startswith("mekanism:"):
        # Mekanism cables: brak NBT, tier w block_id
        pass
    else:
        # Fallback — zostaw puste NBT
        pass
    
    # --- Ostrzeżenia o utraconych właściwościach ---
    if color != 0:
        result["warnings"].append(
            f"IC2-W-CABLE-COLOR: Kolor kabla (color={color}) nie jest wspierany "
            f"w docelowym modzie. Kabel zostanie przekonwertowany bez koloru."
        )
    
    if foamed > 0:
        result["warnings"].append(
            f"IC2-W-CABLE-FOAMED: Kabel był zabudowany pianą (foamed={foamed}, "
            f"foamColor={foam_color}). Brak odpowiednika. "
            f"Zalecane ręczne obudowanie blokami konstrukcyjnymi."
        )
    
    # --- Retexture ---
    retexture_ref = nbt_1710.get("retextureRefMeta")
    if retexture_ref is not None:
        result["warnings"].append(
            "IC2-W-CABLE-RETEXTURE: Kabel miał customową teksturę (retexture). "
            "Tekstura zostanie utracona."
        )
    
    return result
