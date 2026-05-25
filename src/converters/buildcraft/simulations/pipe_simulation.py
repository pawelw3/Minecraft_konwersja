"""
Symulacja konwersji rur BuildCraft (GenericPipe) -> decyzja architektoniczna.

BuildCraft 1.7.10 GenericPipe NBT:
- pipeId: int (identyfikator typu rury, np. 4163)
- inputOpen / outputOpen: int (bitmask otwartych stron)
- wireSet[0-3]: int (BC gates wire)
- redstoneInputSide[0-5]: int (redstone input per side)
- travelingEntities: list (itemy w trakcie transportu)

Problem:
- pipeId jest numerycznym ID wewnętrznym BuildCraft; mapowanie na nazwy typów
  (Cobblestone, Stone, Iron, Gold, Diamond, Emerald, Obsidian, Void, itd.)
  wymagałoby dostępu do kodu źródłowego BC lub dekompilacji.
- Pipez 1.18.2 nie ma logiki gates, wire, traveling entities.
- Nie da się bezstratnie przenieść konfiguracji rur.

Decyzje:
- Opcja A (REMOVE): Usunąć wszystkie rury. Najprostsze, ale tracimy infrastrukturę.
- Opcja B (REPLACE_UNIVERSAL): Zamienić na Pipez Universal Pipe (lub Item/Fluid/Energy
  w zależności od kontekstu). Wymaga odgadnięcia typu z NBT (np. po obecności
  tankFuel/tankCoolant w sąsiednich silnikach).
- Opcja C (SMART_REPLACE): Analiza sąsiedztwa (co jest podłączone do rury)
  i wybór odpowiedniego typu Pipez.

Rekomendacja: Opcja A dla większości (rury to tymczasowa infrastruktura),
Opcja B tylko dla kluczowych połączeń (np. pomiędzy pompą a tankiem).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Set


@dataclass
class PipeState1710:
    """Stan rury BuildCraft 1.7.10."""
    te_id: str
    x: int
    y: int
    z: int
    pipe_id: int = 0
    input_open: int = 63   # bitmask (6 bitów = 6 stron)
    output_open: int = 63  # bitmask
    wire_set: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    redstone_input: list[int] = field(default_factory=lambda: [0]*6)
    traveling_entities: list[Any] = field(default_factory=list)

    @classmethod
    def from_nbt(cls, nbt: dict[str, Any]) -> "PipeState1710":
        # redstoneInputSide[0..5] może być zapisane jako osobne klucze
        redstone = [0]*6
        for i in range(6):
            redstone[i] = nbt.get(f"redstoneInputSide[{i}]", 0)
        # wireSet[0..3]
        wires = [nbt.get(f"wireSet[{i}]", 0) for i in range(4)]
        return cls(
            te_id=nbt.get("id", ""),
            x=nbt.get("x", 0),
            y=nbt.get("y", 0),
            z=nbt.get("z", 0),
            pipe_id=nbt.get("pipeId", 0),
            input_open=nbt.get("inputOpen", 63),
            output_open=nbt.get("outputOpen", 63),
            wire_set=wires,
            redstone_input=redstone,
            traveling_entities=nbt.get("travelingEntities", []),
        )

    def open_sides(self) -> Set[str]:
        """Zwraca zbiór otwartych stron na podstawie outputOpen bitmask."""
        sides = ["down", "up", "north", "south", "west", "east"]
        result = set()
        for i, side in enumerate(sides):
            if self.output_open & (1 << i):
                result.add(side)
        return result

    def has_active_logic(self) -> bool:
        """Czy rura ma aktywną logikę (wires, gates, redstone)?"""
        if any(self.wire_set):
            return True
        if any(self.redstone_input):
            return True
        return False

    def has_items_in_transit(self) -> bool:
        """Czy w rurze są itemy w trakcie transportu?"""
        return len(self.traveling_entities) > 0


@dataclass
class PipeReplacement1182:
    """Propozycja zastępstwa rury w 1.18.2."""
    block_id: Optional[str]  # None = usunięcie
    reason: str
    strategy: str  # REMOVE, UNIVERSAL_PIPE, ITEM_PIPE, FLUID_PIPE, ENERGY_PIPE


# Mapowanie pipeId na prawdopodobne typy (przybliżone, bez dekompilacji BC)
# Zakresy ID z obserwacji mapy:
# - transport pipes (item): zazwyczaj niższe ID
# - fluid pipes: środkowe
# - kinesis pipes (power): wyższe
# W praktyce bez dekompilacji nie znamy dokładnego mapowania.
PIPE_ID_STRATEGY_GUESS = {
    # Jeśli pipe_id < 4000: prawdopodobnie transport (item)
    # Jeśli 4000-4200: prawdopodobnie kinesis (power) - nasze dane: 4163
    # Jeśli > 4200: prawdopodobnie fluid
}


def simulate_pipe_conversion(
    state_1710: PipeState1710,
    neighbors_have_fluid: bool = False,
    neighbors_have_power: bool = False,
    is_critical_connection: bool = False,
) -> dict[str, Any]:
    """Symuluje konwersję rury BC na decyzję 1.18.2.

    Args:
        neighbors_have_fluid: czy sąsiadujący blok to pump/tank/refinery
        neighbors_have_power: czy sąsiadujący blok to engine
        is_critical_connection: czy to kluczowe połączenie (np. pomiędzy maszynami)
    """
    # Decyzja użytkownika: NIE usuwać rur w ogóle -> wszystkie zamieniamy na Pipez
    # (nawet jeśli miały logikę gates/wires, tracimy ją ale zachowujemy infrastrukturę)
    if neighbors_have_fluid:
        strategy = "FLUID_PIPE"
        replacement_block = "pipez:fluid_pipe"
        reason = "Rura BC -> Pipez Fluid Pipe."
    elif neighbors_have_power:
        strategy = "ENERGY_PIPE"
        replacement_block = "pipez:energy_pipe"
        reason = "Rura BC -> Pipez Energy Pipe."
    else:
        strategy = "UNIVERSAL_PIPE"
        replacement_block = "pipez:universal_pipe"
        reason = "Rura BC -> Pipez Universal Pipe (item/fluid/energy)."

    # Uwaga: logika gates/wires oraz travelingEntities są tracone
    if state_1710.has_active_logic():
        reason += " UWAGA: logika gates/wires zostaje utracona."
    elif state_1710.has_items_in_transit():
        reason += " UWAGA: itemy w transporcie zostają utracene."

    return {
        "action": strategy,
        "reason": reason,
        "original": {
            "te_id": state_1710.te_id,
            "x": state_1710.x,
            "y": state_1710.y,
            "z": state_1710.z,
            "pipe_id": state_1710.pipe_id,
            "open_sides": list(state_1710.open_sides()),
        },
        "replacement_block": replacement_block,
    }


def print_pipe_report(result: dict[str, Any]) -> None:
    """Drukuje czytelny raport z konwersji rury."""
    action = result["action"]
    orig = result["original"]
    print(f"[Pipe] {orig['te_id']} @ ({orig['x']},{orig['y']},{orig['z']}) -> {action}")
    print(f"  pipeId={orig['pipe_id']}, otwarte strony={orig['open_sides']}")
    print(f"  Powód: {result['reason']}")
    if result.get("replacement_block"):
        print(f"  Zamiennik: {result['replacement_block']}")
    print()


# =============================================================================
# TESTY / PRZYKŁADY UŻYCIA
# =============================================================================

if __name__ == "__main__":
    # Przykład 1: Zwykła rura bez logiki -> REMOVE
    pipe1_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 100, "y": 64, "z": 200,
        "pipeId": 4163,
        "inputOpen": 63,
        "outputOpen": 63,
        "wireSet[0]": 0, "wireSet[1]": 0, "wireSet[2]": 0, "wireSet[3]": 0,
        "redstoneInputSide[0]": 0, "redstoneInputSide[1]": 0,
        "redstoneInputSide[2]": 0, "redstoneInputSide[3]": 0,
        "redstoneInputSide[4]": 0, "redstoneInputSide[5]": 0,
        "travelingEntities": [],
    }
    pipe1 = PipeState1710.from_nbt(pipe1_nbt)
    result = simulate_pipe_conversion(pipe1)
    print_pipe_report(result)
    assert result["action"] == "REMOVE"

    # Przykład 2: Rura z logiką (wire) -> REMOVE
    pipe2_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 101, "y": 64, "z": 200,
        "pipeId": 4100,
        "inputOpen": 63,
        "outputOpen": 63,
        "wireSet[0]": 1, "wireSet[1]": 0, "wireSet[2]": 0, "wireSet[3]": 0,
        "redstoneInputSide[0]": 0, "redstoneInputSide[1]": 0,
        "redstoneInputSide[2]": 0, "redstoneInputSide[3]": 0,
        "redstoneInputSide[4]": 0, "redstoneInputSide[5]": 0,
        "travelingEntities": [],
    }
    pipe2 = PipeState1710.from_nbt(pipe2_nbt)
    result = simulate_pipe_conversion(pipe2)
    print_pipe_report(result)
    assert result["action"] == "REMOVE"
    assert "logikę BC" in result["reason"]

    # Przykład 3: Rura z itemami w transporcie -> REMOVE
    pipe3_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 102, "y": 64, "z": 200,
        "pipeId": 4163,
        "inputOpen": 63,
        "outputOpen": 63,
        "wireSet[0]": 0,
        "travelingEntities": [{"some": "entity"}],
    }
    pipe3 = PipeState1710.from_nbt(pipe3_nbt)
    result = simulate_pipe_conversion(pipe3)
    print_pipe_report(result)
    assert result["action"] == "REMOVE"
    assert "itemy" in result["reason"]

    # Przykład 4: Kluczowe połączenie płynowe -> FLUID_PIPE
    pipe4_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 103, "y": 64, "z": 200,
        "pipeId": 4201,
        "inputOpen": 12,  # tylko N/S
        "outputOpen": 12,
        "wireSet[0]": 0,
        "travelingEntities": [],
    }
    pipe4 = PipeState1710.from_nbt(pipe4_nbt)
    result = simulate_pipe_conversion(pipe4, neighbors_have_fluid=True, is_critical_connection=True)
    print_pipe_report(result)
    assert result["action"] == "FLUID_PIPE"
    assert result["replacement_block"] == "pipez:fluid_pipe"

    # Przykład 5: Kluczowe połączenie energetyczne -> ENERGY_PIPE
    pipe5_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 104, "y": 64, "z": 200,
        "pipeId": 4163,
        "inputOpen": 3,  # down/up
        "outputOpen": 3,
        "wireSet[0]": 0,
        "travelingEntities": [],
    }
    pipe5 = PipeState1710.from_nbt(pipe5_nbt)
    result = simulate_pipe_conversion(pipe5, neighbors_have_power=True, is_critical_connection=True)
    print_pipe_report(result)
    assert result["action"] == "ENERGY_PIPE"
    assert result["replacement_block"] == "pipez:energy_pipe"

    # Przykład 6: Kluczowe połączenie uniwersalne -> UNIVERSAL_PIPE
    pipe6_nbt = {
        "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
        "x": 105, "y": 64, "z": 200,
        "pipeId": 4163,
        "inputOpen": 63,
        "outputOpen": 63,
        "wireSet[0]": 0,
        "travelingEntities": [],
    }
    pipe6 = PipeState1710.from_nbt(pipe6_nbt)
    result = simulate_pipe_conversion(pipe6, is_critical_connection=True)
    print_pipe_report(result)
    assert result["action"] == "UNIVERSAL_PIPE"
    assert result["replacement_block"] == "pipez:universal_pipe"

    print("=" * 60)
    print("Wszystkie symulacje rur zakończone sukcesem.")
    print("=" * 60)
