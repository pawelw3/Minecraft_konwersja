"""Symulacja sieci (cable + modem) ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Bazuje na kodzie źródłowym:
- 1.7.10: `shared/peripheral/modem/TileCable.java`
- 1.18.2: `shared/peripheral/modem/wired/CableBlockEntity.java`,
           `shared/peripheral/modem/wired/WiredModemLocalPeripheral.java`

Kluczowe różnice:
- 1.7.10: `peripheralAccess` (bool), `peripheralID` (int)
- 1.18.2: `PeripheralId` (int), `PeripheralType` (string)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Cable1710:
    """Symulacja kabla/przewodowego modemu 1.7.10."""

    peripheral_access_allowed: bool = False
    attached_peripheral_id: int = -1

    def write_to_nbt(self) -> dict:
        nbt: dict = {}
        nbt["peripheralAccess"] = self.peripheral_access_allowed
        nbt["peripheralID"] = self.attached_peripheral_id
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Cable1710":
        return cls(
            peripheral_access_allowed=nbt.get("peripheralAccess", False),
            attached_peripheral_id=nbt.get("peripheralID", -1),
        )


@dataclass
class Cable1182:
    """Symulacja kabla/przewodowego modemu 1.18.2."""

    peripheral_id: int = -1
    peripheral_type: str | None = None

    def write_to_nbt(self) -> dict:
        nbt: dict = {}
        if self.peripheral_id >= 0:
            nbt["PeripheralId"] = self.peripheral_id
        if self.peripheral_type:
            nbt["PeripheralType"] = self.peripheral_type
        return nbt

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Cable1182":
        return cls(
            peripheral_id=nbt.get("PeripheralId", -1),
            peripheral_type=nbt.get("PeripheralType"),
        )


def convert_cable_nbt(nbt_1710: dict) -> dict:
    """Skonwertuj NBT kabla z 1.7.10 na 1.18.2.

    W 1.7.10 `peripheralAccess` określa czy modem ma udostępniać podłączone
    peryferium jako peryferium sieciowe. W 1.18.2 ten mechanizm jest inny
    (peripheral attachment jest dynamiczne), ale zachowujemy `peripheralID`
    jako `PeripheralId`.

    `peripheralType` nie było w 1.7.10 — CC:Tweaked ustawi to dynamicznie
    na podstawie podłączonego bloku.
    """
    result: dict = {}
    if "peripheralID" in nbt_1710:
        pid = nbt_1710["peripheralID"]
        if pid >= 0:
            result["PeripheralId"] = pid
    # peripheralAccess nie ma bezpośredniego odpowiednika w NBT 1.18.2
    # (stan jest runtime'owy / w blockstate)
    return result


def derive_cable_blockstate(metadata: int) -> dict[str, str]:
    """Wydedukuj blockstate kabla 1.18.2 z metadata 1.7.10.

    1.7.10 cable meta:
      0-5   = wired modem only (no cable)
      6-11  = wired modem + cable
      13    = cable only

    1.18.2 blockstate:
      cable = true/false
      modem = variant (none, down_off, down_on, ...)
    """
    if metadata < 6:
        return {"cable": "false", "modem": "none"}  # modem bez kabla — w 1.18.2 cable=false
    if metadata < 12:
        # modem + cable — w 1.18.2 cable=true, modem ma facing
        return {"cable": "true", "modem": "none"}
    if metadata == 13:
        return {"cable": "true", "modem": "none"}
    return {"cable": "false", "modem": "none"}


def _run_example():
    print("=" * 60)
    print("ComputerCraft — symulacja sieci (cable/modem)")
    print("=" * 60)

    # Kabel z podłączonym peryferium
    cab_1710 = Cable1710(peripheral_access_allowed=True, attached_peripheral_id=3)
    nbt_1710 = cab_1710.write_to_nbt()
    print("\n[1.7.10] Cable NBT:", nbt_1710)

    nbt_1182 = convert_cable_nbt(nbt_1710)
    print("[1.18.2] Converted NBT:", nbt_1182)

    cab_1182 = Cable1182.read_from_nbt(nbt_1182)
    print("[1.18.2] Loaded cable:", cab_1182)

    # Blockstate dla różnych metadata
    print("\n--- Blockstate mapping ---")
    for meta in [0, 5, 6, 11, 13]:
        bs = derive_cable_blockstate(meta)
        print(f"  meta={meta:2d} → {bs}")

    print("\n✓ Symulacja sieci zakończona")


if __name__ == "__main__":
    _run_example()
