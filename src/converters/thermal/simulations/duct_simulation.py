"""Symulacja funkcjonalnosci ductow Thermal Dynamics.

W 1.7.10 ducty tworza sieci (grids) przesylajace energie/plyny/itemy.
W 1.18.2 Thermal Dynamics ma uproszczony system.
W przypadku fallbacku na Mekanism: Logistical Transporter przesyla itemy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class DuctNetwork:
    """Sieć ductow (symulacja)."""
    duct_type: str  # energy, fluid, item, structural, transport
    nodes: list = field(default_factory=list)
    connections: list = field(default_factory=list)

    # Statystyki przeplywu
    throughput_per_tick: int = 1000  # np. RF/t dla energii

    def add_node(self, position: tuple[int, int, int], tier: str = "basic"):
        self.nodes.append({"pos": position, "tier": tier, "attachments": []})

    def connect(self, pos_a: tuple, pos_b: tuple):
        self.connections.append((pos_a, pos_b))

    def simulate_tick(self, input_at: tuple, amount: int) -> dict:
        """Symuluje 1 tick transportu."""
        # Uproszczony model: rozdziela rownomiernie miedzy outputy
        outputs = [n for n in self.nodes if n["pos"] != input_at]
        if not outputs:
            return {"transferred": 0, "loss": amount}

        per_output = amount // len(outputs)
        transferred = per_output * len(outputs)
        loss = amount - transferred

        return {
            "transferred": transferred,
            "loss": loss,
            "per_output": per_output,
            "output_count": len(outputs),
        }


def simulate_energy_grid(
    sources: list[tuple],
    sinks: list[tuple],
    total_rf: int = 10000,
) -> dict:
    """Symuluje siec energy ductow.

    W 1.7.10: Leadstone (80 RF/t), Hardened (400), Redstone (4000),
              Signalum (10000), Resonant (20000), Cryo-Stabilized (unlimited)
    W 1.18.2: energy_duct (bez tierow, rate limit zalezy od konfiguracji)
    W Mekanism: Universal Cable (tier: basic/advanced/elite/ultimate)
    """
    network = DuctNetwork("energy")
    for pos in sources + sinks:
        network.add_node(pos, tier="hardened")

    # Polacz w lancuch
    all_nodes = sources + sinks
    for i in range(len(all_nodes) - 1):
        network.connect(all_nodes[i], all_nodes[i + 1])

    tick = 0
    total_transferred = 0
    remaining = total_rf
    while remaining > 0 and tick < 1000:
        chunk = min(400, remaining)  # Hardened limit
        result = network.simulate_tick(sources[0], chunk)
        total_transferred += result["transferred"]
        remaining -= result["transferred"]
        tick += 1

    return {
        "total_rf": total_rf,
        "transferred": total_transferred,
        "ticks": tick,
        "sources": len(sources),
        "sinks": len(sinks),
        "note": "Thermal 1.18.2: energy_duct bez tierow (limit w konfiguracji); "
                "Mekanism fallback: universal_cable z tierami",
    }


def simulate_item_transport(
    source: tuple,
    sinks: list[tuple],
    items: list[str],
) -> dict:
    """Symuluje transport itemow przez Itemduct.

    W 1.7.10: Itemduct z servo/filter/retriever.
    W 1.18.2: item_buffer (brak prawdziwych itemductow).
    W Mekanism fallback: Logistical Transporter + Logistical Sorter.
    """
    network = DuctNetwork("item")
    network.add_node(source, tier="itemduct")
    for sink in sinks:
        network.add_node(sink, tier="itemduct")
        network.connect(source, sink)

    transferred = 0
    for item in items:
        # Symulacja: kazdy item trafia do losowego sinka
        transferred += 1

    return {
        "items_sent": len(items),
        "items_delivered": transferred,
        "sinks": len(sinks),
        "has_filtering": True,  # 1.7.10 mialy filtry
        "target_1182": "thermal:item_buffer (bez filtrowania)",
        "target_mekanism_fallback": "mekanism:basic_logistical_transporter + sorter",
    }


if __name__ == "__main__":
    print("=== Symulacja energy grid ===")
    result = simulate_energy_grid(
        sources=[(0, 0, 0)],
        sinks=[(5, 0, 0), (10, 0, 0)],
        total_rf=10000,
    )
    for k, v in result.items():
        print(f"  {k}: {v}")

    print("\n=== Symulacja item transport ===")
    result = simulate_item_transport(
        source=(0, 0, 0),
        sinks=[(3, 0, 0), (6, 0, 0)],
        items=["minecraft:iron_ingot"] * 64,
    )
    for k, v in result.items():
        print(f"  {k}: {v}")
