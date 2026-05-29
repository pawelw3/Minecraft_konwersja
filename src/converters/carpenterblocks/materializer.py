"""
CBMaterializer: CBConversionResult → /setblock komendy dla cuttableblocks 1.18.2.

Jawna tabela translacji CB TileEntity → CuttableBlockEntity:

  Każdy z 18 bloków CB 1.7.10 używa TEBase jako swojego TileEntity.
  Wszystkie przekształcane są na CuttableBlockEntity (jeden typ w modzie 1.18.2).
  Typ semantyczny ("beType") zapisywany jest w NBT BlockEntity, umożliwiając
  rendererowi rozróżnienie sposobu renderowania.

  CB block_id_1710                        → 1.18.2 BE type  beType
  ─────────────────────────────────────────────────────────────────
  blockCarpentersSlope                    → CuttableBlockEntity  coverable
  blockCarpentersStairs                   → CuttableBlockEntity  coverable
  blockCarpentersBlock                    → CuttableBlockEntity  coverable
  blockCarpentersCollapsibleBlock         → CuttableBlockEntity  collapsible
  blockCarpentersBarrier                  → CuttableBlockEntity  coverable
  blockCarpentersGate                     → CuttableBlockEntity  coverable
  blockCarpentersHatch                    → CuttableBlockEntity  hatch
  blockCarpentersDoor                     → CuttableBlockEntity  door
  blockCarpentersLadder                   → CuttableBlockEntity  coverable
  blockCarpentersLever                    → CuttableBlockEntity  lever
  blockCarpentersButton                   → CuttableBlockEntity  button
  blockCarpentersPressurePlate            → CuttableBlockEntity  coverable
  blockCarpentersTorch                    → CuttableBlockEntity  coverable
  blockCarpentersDaylightSensor           → CuttableBlockEntity  coverable
  blockCarpentersSafe                     → CuttableBlockEntity  coverable
  blockCarpentersFlowerPot                → CuttableBlockEntity  flower_pot
  blockCarpentersBed                      → CuttableBlockEntity  multiblock
  blockCarpentersGarageDoor               → CuttableBlockEntity  multiblock

  Geometria (blockstate_props z CBBlockConverter) trafia do pola "geom" w NBT
  zamiast do właściwości blockstate — mod skeleton nie ma zdefiniowanych
  właściwości blockstate dla tych bloków.

NBT CuttableBlockEntity (SNBT generowane przez dict_to_snbt):
  coverMaterial    STRING  - bazowy materiał pokrycia
  sideCovers       COMPOUND{"0":id,...} - pokrycia per-bok (jeśli różne od base)
  sideDyes         COMPOUND{"0":id,...} - barwniki per-bok
  cbDesign         STRING  - wzór dłuta (chisel)
  illuminator      BYTE    - 1 jeśli ma iluminator
  beType           STRING  - typ semantyczny (coverable|collapsible|hatch|door|...)
  geom             COMPOUND - właściwości geometryczne (facing, half, shape, ...)
  quadDepths       INT[]   - głębokości kwadrantów (tylko collapsible)
  rigid            BYTE    - flaga sztywności (hatch/door)
  polarityNegative BYTE    - odwrócona polaryzacja (lever/button)
  smoldering       BYTE    - stan tlenia (torch)
  plantMaterial    STRING  - roślina (flower_pot)
  soilMaterial     STRING  - podłoże (flower_pot)
  cbMetadataRaw    INT     - surowe cbMetadata (multiblock, -1 = brak)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .nbt_converter import CBBlockConverter, CBConversionResult

# ─────────────────────────────────────────────────────────────────────────────
# Jawna tabela: CB block_id_1710 → semantyczny typ BlockEntity
# ─────────────────────────────────────────────────────────────────────────────

_CB_BLOCK_TO_BE_TYPE: dict[str, str] = {
    "CarpentersBlocks:blockCarpentersSlope":            "coverable",
    "CarpentersBlocks:blockCarpentersStairs":           "coverable",
    "CarpentersBlocks:blockCarpentersBlock":            "coverable",
    "CarpentersBlocks:blockCarpentersCollapsibleBlock": "collapsible",
    "CarpentersBlocks:blockCarpentersBarrier":          "coverable",
    "CarpentersBlocks:blockCarpentersGate":             "coverable",
    "CarpentersBlocks:blockCarpentersHatch":            "hatch",
    "CarpentersBlocks:blockCarpentersDoor":             "door",
    "CarpentersBlocks:blockCarpentersLadder":           "coverable",
    "CarpentersBlocks:blockCarpentersLever":            "lever",
    "CarpentersBlocks:blockCarpentersButton":           "button",
    "CarpentersBlocks:blockCarpentersPressurePlate":    "coverable",
    "CarpentersBlocks:blockCarpentersTorch":            "coverable",
    "CarpentersBlocks:blockCarpentersDaylightSensor":   "coverable",
    "CarpentersBlocks:blockCarpentersSafe":             "coverable",
    "CarpentersBlocks:blockCarpentersFlowerPot":        "flower_pot",
    "CarpentersBlocks:blockCarpentersBed":              "multiblock",
    "CarpentersBlocks:blockCarpentersGarageDoor":       "multiblock",
}


# ─────────────────────────────────────────────────────────────────────────────
# Generowanie SNBT
# ─────────────────────────────────────────────────────────────────────────────

def _snbt_value(v: Any) -> str:
    """Konwertuje wartość Python na SNBT."""
    if isinstance(v, bool):
        return "1b" if v else "0b"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"{v:.6g}f"
    if isinstance(v, str):
        escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(v, list):
        if v and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
            return "[I;" + ",".join(str(x) for x in v) + "]"
        return "[" + ",".join(_snbt_value(x) for x in v) + "]"
    if isinstance(v, dict):
        items = ",".join(f'"{k}":{_snbt_value(val)}' for k, val in v.items())
        return "{" + items + "}"
    return f'"{v!s}"'


def dict_to_snbt(d: dict) -> str:
    """Konwertuje słownik Python na string SNBT (bez nawiasów zewnętrznych nie)."""
    items = ",".join(f'"{k}":{_snbt_value(v)}' for k, v in d.items())
    return "{" + items + "}"


# ─────────────────────────────────────────────────────────────────────────────
# Wynik materializacji
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MaterializeEvent:
    """Jeden blok CB po konwersji → gotowy do umieszczenia w świecie 1.18.2."""
    pos: tuple[int, int, int]
    block_id: str              # np. "cuttableblocks:slope"
    nbt_snbt: str | None       # SNBT dołączony do komendy setblock
    be_type: str               # semantyczny typ BE ("coverable", "collapsible", …)
    blockstate_props: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not any(e.startswith("CB-E-") for e in self.errors)

    def to_setblock_command(self) -> str:
        x, y, z = self.pos
        cmd = f"setblock {x} {y} {z} {self.block_id}"
        if self.blockstate_props:
            props_str = ",".join(f"{k}={v}" for k, v in self.blockstate_props.items())
            cmd += f"[{props_str}]"
        if self.nbt_snbt:
            cmd += self.nbt_snbt
        cmd += " replace"
        return cmd


# ─────────────────────────────────────────────────────────────────────────────
# Główna klasa
# ─────────────────────────────────────────────────────────────────────────────

class CBMaterializer:
    """
    Konwertuje bloki CB 1.7.10 (pos + block_id + TE NBT) na eventy setblock
    dla cuttableblocks 1.18.2.

    Translacja BlockEntity:
      Wszystkie 18 typów CB TEBase → CuttableBlockEntity (jeden typ w 1.18.2).
      Geometria (blockstate_props) trafia do pola „geom" w NBT zamiast
      do właściwości blockstate, bo szkielet moda nie ma ich zdefiniowanych.
      Pole „beType" w NBT wskazuje semantyczny typ (coverable, collapsible, …).
    """

    def __init__(self, converter: CBBlockConverter | None = None):
        self.converter: CBBlockConverter = converter or CBBlockConverter()

    # ------------------------------------------------------------------
    def materialize_block(
        self,
        pos: tuple[int, int, int],
        block_id_1710: str,
        te_nbt: dict,
    ) -> MaterializeEvent:
        """Konwertuje jeden blok CB na MaterializeEvent."""
        result: CBConversionResult = self.converter.convert(block_id_1710, te_nbt)

        if not result.success:
            return MaterializeEvent(
                pos=pos,
                block_id="minecraft:air",
                nbt_snbt=None,
                be_type="error",
                errors=result.errors,
                warnings=result.warnings,
            )

        be_type = _CB_BLOCK_TO_BE_TYPE.get(block_id_1710, "coverable")

        # nbt_1182 zawiera już facing/shape/flags/sourceCarpentersTeId z konwertera
        merged: dict[str, Any] = dict(result.nbt_1182)

        return MaterializeEvent(
            pos=pos,
            block_id=result.block_id_1182,
            blockstate_props=dict(result.blockstate_props),
            nbt_snbt=dict_to_snbt(merged),
            be_type=be_type,
            errors=result.errors,
            warnings=result.warnings,
        )

    # ------------------------------------------------------------------
    def materialize_bulk(
        self,
        blocks: list[dict],
    ) -> list[MaterializeEvent]:
        """
        Konwertuje listę bloków.

        Każdy element listy: {"pos": (x, y, z), "block_id": str, "nbt": dict}
        """
        return [
            self.materialize_block(b["pos"], b["block_id"], b["nbt"])
            for b in blocks
        ]

    # ------------------------------------------------------------------
    def to_setblock_commands(
        self,
        events: list[MaterializeEvent],
        include_failed: bool = False,
    ) -> list[str]:
        """Generuje listę komend /setblock dla podanych eventów."""
        return [
            e.to_setblock_command()
            for e in events
            if include_failed or e.success
        ]

    # ------------------------------------------------------------------
    def stats(self, events: list[MaterializeEvent]) -> dict[str, int]:
        """Statystyki materializacji: sukces/ostrzeżenia/błędy per be_type."""
        result: dict[str, int] = {
            "total": len(events),
            "success": sum(1 for e in events if e.success),
            "with_warnings": sum(1 for e in events if e.warnings),
            "failed": sum(1 for e in events if not e.success),
        }
        by_type: dict[str, int] = {}
        for e in events:
            by_type[e.be_type] = by_type.get(e.be_type, 0) + 1
        result["by_be_type"] = by_type  # type: ignore[assignment]
        return result
