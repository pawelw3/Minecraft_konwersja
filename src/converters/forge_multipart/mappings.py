"""
Mapowania ForgeMultipart 1.7.10 -> CB Multipart 1.18.2

Source mapping:
- 1.7.10: dekompilacja JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar
- 1.18.2: źródła ProjectRed 1.18.2 (importy codechicken.multipart) + dokumentacja CB Multipart
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Mapowanie ID bloków
# ---------------------------------------------------------------------------
BLOCK_ID_1710_TO_1182: dict[str, str] = {
    "ForgeMultipart:block": "cb_multipart:block",
    # Mikrobloki nie są osobnymi blokami w 1.7.10 — są partami wewnątrz BlockMultipart.
    # W 1.18.2 również nie mają osobnych block ID.
}

# ---------------------------------------------------------------------------
# Mapowanie ID TileEntity / BlockEntity
# ---------------------------------------------------------------------------
TE_ID_1710_TO_1182: dict[str, str] = {
    # Exact string potwierdzony na mapie (Zadanie 4):
    # ForgeMultipart używa dynamicznej rejestracji przez ASM;
    # w NBT chunka TileMultipart pojawia się jako "savedMultipart".
    "savedMultipart": "cb_multipart:tile_multipart",
    # Hipotetyczne alternatywy (do weryfikacji jeśli się pojawią):
    "TileMultipart": "cb_multipart:tile_multipart",
    "ForgeMultipart:TileMultipart": "cb_multipart:tile_multipart",
}

# ---------------------------------------------------------------------------
# Mapowanie ID partów (multipart registry) 1.7.10 -> 1.18.2
# ---------------------------------------------------------------------------
PART_ID_1710_TO_1182: dict[str, str] = {
    # ForgeMicroblock (mikrobloki)
    "mcr_face":   "microblockcbe:face",
    "mcr_hollow": "microblockcbe:hollow",
    "mcr_corner": "microblockcbe:corner",
    "mcr_cnr":    "microblockcbe:corner",   # alias z mapy (skrót od corner)
    "mcr_edge":   "microblockcbe:edge",
    "mcr_post":   "microblockcbe:post",

    # McMultipart (vanilla parts)
    "mc_torch":        "cb_multipart:torch",
    "mc_redtorch":     "cb_multipart:redstone_torch",
    "mc_button":       "cb_multipart:button",
    "mc_lever":        "cb_multipart:lever",

    # ProjectRed parts (często spotykane na mapach z ForgeMultipart)
    # Te będą obsługiwane przez konwerter ProjectRed, ale dla kompletności:
    "pr_redwire":      "projectred-transmission:redwire",
    "pr_insulated":    "projectred-transmission:insulated_wire",
    "pr_bundled":      "projectred-transmission:bundled_cable",
    "pr_framed":       "projectred-transmission:framed_wire",
    "pr_gate":         "projectred-integration:gate",
}

# ---------------------------------------------------------------------------
# Mapowanie itemów (dla kompletności — itemy mogą być w inventory TE innych modów)
# ---------------------------------------------------------------------------
ITEM_ID_1710_TO_1182: dict[str, str] = {
    "ForgeMicroblock:microblock":    "microblockcbe:microblock",
    "microblock:microblock":         "microblockcbe:microblock",
    "ForgeMicroblock:sawStone":      "microblockcbe:saw_stone",
    "ForgeMicroblock:sawIron":       "microblockcbe:saw_iron",
    "ForgeMicroblock:sawDiamond":    "microblockcbe:saw_diamond",
    "ForgeMicroblock:stoneRod":      "microblockcbe:stone_rod",
}


def map_block_id(block_id_1710: str) -> str | None:
    """Zwraca block ID 1.18.2 lub None jeśli nieznane."""
    return BLOCK_ID_1710_TO_1182.get(block_id_1710)


def map_te_id(te_id_1710: str) -> str | None:
    """Zwraca TE/BE ID 1.18.2 lub None jeśli nieznane."""
    return TE_ID_1710_TO_1182.get(te_id_1710)


def map_part_id(part_id_1710: str) -> str:
    """Zwraca part ID 1.18.2; jeśli brak mapowania, zwraca oryginał z ostrzeżeniem."""
    return PART_ID_1710_TO_1182.get(part_id_1710, part_id_1710)


def map_item_id(item_id_1710: str) -> str:
    """Zwraca item ID 1.18.2; jeśli brak mapowania, zwraca oryginał."""
    return ITEM_ID_1710_TO_1182.get(item_id_1710, item_id_1710)
