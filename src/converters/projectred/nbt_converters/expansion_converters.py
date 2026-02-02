"""
NBT Converters for ProjectRed Expansion Module

Konwertery dla maszyn z modułu Expansion.

Source mapping:
1.7.10:
- TileBatteryBox: expansion/TileBatteryBox.scala (save/load: storage)
- TileChargingBench: expansion/TileChargingBench.scala (save/load: storage, srr)
- TileElectrotineGenerator: expansion/TileElectrotineGenerator.scala (save/load: storage, btime)
- TileFrameMotor: expansion/TileFrameMotor.scala (save/load: ch, pow)
- TileFrameActuator: expansion/TileFrameActuator.scala (save/load: ch, pow)
- TileBlockBreaker: expansion/TileBlockBreaker.scala (no extra NBT)
- TileFireStarter: expansion/TileFireStarter.scala (no extra NBT)
- TileProjectBench: expansion/TileProjectBench.scala (save/load: inventory)
- TileAutoCrafter: expansion/TileAutoCrafter.scala (save/load: cyt1, cyt2)

1.18.2:
- BatteryBoxBlockEntity: expansion/tile/BatteryBoxBlockEntity.java
  (saveToNBT: storage, inventory, vCap, iCap, chargeFlow)
- ChargingBenchBlockEntity: expansion/tile/ChargingBenchBlockEntity.java
  (saveToNBT: storage, chargeSlot, inventory, vCap, iCap, chargeFlow)
- ElectrotineGeneratorBlockEntity: core/tile/ElectrotineGeneratorBlockEntity.java
  (saveToNBT: stored, burnTime, inventory, vCap, iCap)
- BaseFrameMoverBlockEntity: expansion/tile/BaseFrameMoverBlockEntity.java
  (saveToNBT: powered, vCap, iCap, chargeFlow)
- BlockBreakerBlockEntity: expansion/tile/BlockBreakerBlockEntity.java
  (saveToNBT: queue, schedTick, side, powered, active)
- FireStarterBlockEntity: expansion/tile/FireStarterBlockEntity.java
  (saveToNBT: schedTick, side, powered, active)
- ProjectBenchBlockEntity: expansion/tile/ProjectBenchBlockEntity.java
  (saveToNBT: plan_inv, crafting_inv, storage_inv, plan_crafting_inv)
- AutoCrafterBlockEntity: expansion/tile/AutoCrafterBlockEntity.java
  (saveToNBT: storage_inv, plan_inv, plan_slot, remaining_work, total_work, working, charging, vCap, iCap, chargeFlow)
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class BatteryBoxConverter(BaseNBTConverter):
    """
    Konwerter dla TileBatteryBox (1.7.10) -> BatteryBoxBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - storage (Integer): energia przechowywana (0-8000)
    - Inventory: przez saveInv() (opcjonalne)

    1.18.2 NBT:
    - storage (int): energia przechowywana
    - inventory (CompoundTag): inwentarz
    - vCap (double): napięcie kondensatora (z PowerConductor)
    - iCap (double): prąd kondensatora (z PowerConductor)
    - chargeFlow (int): przepływ ładunku
    """

    SOURCE_1710 = "expansion/TileBatteryBox.scala:103-111"
    SOURCE_1182 = "expansion/tile/BatteryBoxBlockEntity.java:53-67"

    @property
    def converter_name(self) -> str:
        return "battery_box"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # Pobierz storage z 1.7.10
        storage = nbt_1710.get("storage", 0)

        # Konwertuj inventory jeśli istnieje
        inventory = self._convert_inventory(nbt_1710, "items")

        # W 1.18.2 PowerConductor używa vCap/iCap zamiast flows
        # Nie możemy dokładnie skonwertować stanu elektrycznego,
        # ale możemy ustawić rozsądne wartości początkowe
        # Bazując na storage, obliczamy przybliżone vCap
        # (w 1.18.2: vCap ~ sqrt(storage * 0.1 * capacitance))
        # Domyślna capacitance dla BatteryBox to ~8000
        v_cap = 0.0
        if storage > 0:
            # Przybliżenie: v_cap ~ storage / 100 (uproszczenie)
            v_cap = min(storage / 100.0, 80.0)

        converted_nbt = {
            "storage": storage,
            "inventory": inventory,
            "vCap": v_cap,
            "iCap": 0.0,  # Prąd startuje od 0
            "chargeFlow": 0  # Domyślnie brak przepływu
        }

        if storage > 8000:
            self._add_warning("STORAGE-OVERFLOW",
                            f"storage={storage} przekracza limit 8000, zostanie obcięty")
            converted_nbt["storage"] = 8000

        return self._create_result(converted_nbt)


class ChargingBenchConverter(BaseNBTConverter):
    """
    Konwerter dla TileChargingBench (1.7.10) -> ChargingBenchBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - storage (Integer): energia przechowywana
    - srr (Byte): slotRoundRobin - aktualny slot ładowania

    1.18.2 NBT:
    - storage (int): energia przechowywana
    - chargeSlot (byte): aktualny slot ładowania
    - inventory (CompoundTag): inwentarz
    - vCap, iCap (double): stan kondensatora
    - chargeFlow (int): przepływ ładunku
    """

    SOURCE_1710 = "expansion/TileChargingBench.scala:41-54"
    SOURCE_1182 = "expansion/tile/ChargingBenchBlockEntity.java:49-62"

    @property
    def converter_name(self) -> str:
        return "charging_bench"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        storage = nbt_1710.get("storage", 0)
        # srr w 1.7.10 -> chargeSlot w 1.18.2
        srr = nbt_1710.get("srr", 0)

        inventory = self._convert_inventory(nbt_1710, "items")

        v_cap = 0.0
        if storage > 0:
            v_cap = min(storage / 100.0, 80.0)

        converted_nbt = {
            "storage": storage,
            "chargeSlot": srr,  # Zmiana nazwy: srr -> chargeSlot
            "inventory": inventory,
            "vCap": v_cap,
            "iCap": 0.0,
            "chargeFlow": 0
        }

        return self._create_result(converted_nbt)


class ElectrotineGeneratorConverter(BaseNBTConverter):
    """
    Konwerter dla TileElectrotineGenerator (1.7.10) -> ElectrotineGeneratorBlockEntity (1.18.2)

    UWAGA: W 1.18.2 ElectrotineGenerator jest w module Core, nie Expansion!

    Source mapping:
    1.7.10 NBT:
    - storage (Integer): energia przechowywana
    - btime (Short): burnTimeRemaining

    1.18.2 NBT:
    - stored (int): energia przechowywana (zmiana nazwy!)
    - burnTime (int): czas spalania (zmiana z Short na int, zmiana nazwy!)
    - inventory (CompoundTag): inwentarz
    - vCap, iCap (double): stan kondensatora
    """

    SOURCE_1710 = "expansion/TileElectrotineGenerator.scala:39-54"
    SOURCE_1182 = "core/tile/ElectrotineGeneratorBlockEntity.java:47-62"

    @property
    def converter_name(self) -> str:
        return "electrotine_generator"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # 1.7.10: storage -> 1.18.2: stored (zmiana nazwy!)
        storage = nbt_1710.get("storage", 0)
        # 1.7.10: btime (Short) -> 1.18.2: burnTime (int)
        btime = nbt_1710.get("btime", 0)

        inventory = self._convert_inventory(nbt_1710, "items")

        v_cap = 0.0
        if storage > 0:
            v_cap = min(storage / 100.0, 80.0)

        converted_nbt = {
            "stored": storage,  # UWAGA: zmiana nazwy z "storage" na "stored"
            "burnTime": int(btime),  # UWAGA: zmiana z Short na int, zmiana nazwy
            "inventory": inventory,
            "vCap": v_cap,
            "iCap": 0.0
        }

        return self._create_result(converted_nbt)


class FrameMotorConverter(BaseNBTConverter):
    """
    Konwerter dla TileFrameMotor (1.7.10) -> FrameMotorBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT (TMotorTile trait):
    - ch (Boolean): isCharged
    - pow (Boolean): isPowered

    1.18.2 NBT (BaseFrameMoverBlockEntity):
    - powered (boolean): stan zasilania
    - vCap, iCap (double): stan kondensatora
    - chargeFlow (int): przepływ ładunku
    """

    SOURCE_1710 = "expansion/TileFrameMotor.scala:39-50 (trait TMotorTile)"
    SOURCE_1182 = "expansion/tile/BaseFrameMoverBlockEntity.java:37-45"

    @property
    def converter_name(self) -> str:
        return "frame_motor"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # 1.7.10: ch (charged), pow (powered)
        # 1.18.2: tylko powered
        is_charged = nbt_1710.get("ch", False)
        is_powered = nbt_1710.get("pow", False)

        # W 1.18.2 nie ma osobnego "isCharged" - używamy tylko powered
        # Jeśli był naładowany, ustawiamy początkowe vCap
        v_cap = 600.0 if is_charged else 0.0  # 600 to charge threshold

        converted_nbt = {
            "powered": is_powered,
            "vCap": v_cap,
            "iCap": 0.0,
            "chargeFlow": 0
        }

        if is_charged and not is_powered:
            self._add_warning("CHARGE-STATE",
                            "isCharged=True ale isPowered=False - stan może być nieprecyzyjny w 1.18.2")

        return self._create_result(converted_nbt)


class FrameActuatorConverter(FrameMotorConverter):
    """
    Konwerter dla TileFrameActuator (1.7.10) -> FrameActuatorBlockEntity (1.18.2)

    Dziedziczy strukturę NBT z FrameMotor (TMotorTile trait).
    """

    SOURCE_1710 = "expansion/TileFrameActuator.scala (dziedziczy z TMotorTile)"
    SOURCE_1182 = "expansion/tile/FrameActuatorBlockEntity.java (dziedziczy z BaseFrameMoverBlockEntity)"

    @property
    def converter_name(self) -> str:
        return "frame_actuator"


class BlockBreakerConverter(BaseNBTConverter):
    """
    Konwerter dla TileBlockBreaker (1.7.10) -> BlockBreakerBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - Brak specjalnych tagów (dziedziczy z TileMachine)
    - Orientacja przez metadata

    1.18.2 NBT (BasePneumaticDeviceBlockEntity + BaseDeviceBlockEntity):
    - queue (CompoundTag): kolejka pneumatyczna
    - schedTick (long): zaplanowany tick
    - side (byte): strona
    - powered (boolean): czy zasilany
    - active (boolean): czy aktywny
    """

    SOURCE_1710 = "expansion/TileBlockBreaker.scala (brak dodatkowych tagów)"
    SOURCE_1182 = "expansion/tile/BlockBreakerBlockEntity.java:32-43"

    @property
    def converter_name(self) -> str:
        return "block_breaker"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # W 1.7.10 BlockBreaker nie ma dodatkowych tagów NBT
        # W 1.18.2 mamy więcej danych - inicjalizujemy domyślnymi wartościami

        # Orientacja z metadata -> blockstate (nie NBT!)
        side = self._metadata_to_side(metadata)
        facing = self._side_to_facing(side)

        converted_nbt = {
            "queue": {},  # Pusta kolejka
            "schedTick": -1,  # Brak zaplanowanego ticku
            "side": side,
            "powered": False,
            "active": False
        }

        # Orientacja idzie do blockstate, nie do NBT
        blockstate_props = {"facing": facing}

        return self._create_result(converted_nbt, blockstate_props)


class FireStarterConverter(BaseNBTConverter):
    """
    Konwerter dla TileFireStarter (1.7.10) -> FireStarterBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - Brak specjalnych tagów (dziedziczy z TileMachine)

    1.18.2 NBT (BaseDeviceBlockEntity):
    - schedTick (long): zaplanowany tick
    - side (byte): strona
    - powered (boolean): czy zasilany
    - active (boolean): czy aktywny
    """

    SOURCE_1710 = "expansion/TileFireStarter.scala (brak dodatkowych tagów)"
    SOURCE_1182 = "expansion/tile/FireStarterBlockEntity.java"

    @property
    def converter_name(self) -> str:
        return "fire_starter"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        side = self._metadata_to_side(metadata)
        facing = self._side_to_facing(side)

        converted_nbt = {
            "schedTick": -1,
            "side": side,
            "powered": False,
            "active": False
        }

        blockstate_props = {"facing": facing}

        return self._create_result(converted_nbt, blockstate_props)


class ProjectBenchConverter(BaseNBTConverter):
    """
    Konwerter dla TileProjectBench (1.7.10) -> ProjectBenchBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - Inventory zapisywany przez saveInv() (standardowy format)

    1.18.2 NBT:
    - plan_inv (CompoundTag): inwentarz planów
    - crafting_inv (CompoundTag): siatka craftingu
    - storage_inv (CompoundTag): inwentarz magazynowy
    - plan_crafting_inv (CompoundTag): siatka craftingu z planu
    """

    SOURCE_1710 = "expansion/TileProjectBench.scala:58-65"
    SOURCE_1182 = "expansion/tile/ProjectBenchBlockEntity.java:64-77"

    @property
    def converter_name(self) -> str:
        return "project_bench"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # W 1.7.10 jest jeden wspólny inwentarz
        # W 1.18.2 jest podzielony na 4 osobne inwentarze
        # Musimy rozdzielić itemy na odpowiednie sloty

        items_1710 = nbt_1710.get("items", [])

        # ProjectBench w 1.7.10 ma layout:
        # Sloty 0-8: crafting grid (3x3)
        # Sloty 9-26: storage (18 slotów)
        # W 1.18.2 struktura jest inna

        crafting_items = []
        storage_items = []

        for item in items_1710:
            if not item:
                continue
            slot = item.get("Slot", 0)
            if slot < 9:
                # Crafting grid
                crafting_items.append(item)
            else:
                # Storage
                new_item = dict(item)
                new_item["Slot"] = slot - 9  # Przepisz sloty od 0
                storage_items.append(new_item)

        converted_nbt = {
            "plan_inv": {"Items": []},  # Plany - puste na start
            "crafting_inv": {"Items": crafting_items},
            "storage_inv": {"Items": storage_items},
            "plan_crafting_inv": {"Items": []}  # Puste na start
        }

        return self._create_result(converted_nbt)


class AutoCrafterConverter(BaseNBTConverter):
    """
    Konwerter dla TileAutoCrafter (1.7.10) -> AutoCrafterBlockEntity (1.18.2)

    Source mapping:
    1.7.10 NBT:
    - cyt1 (Integer): cycleTimer1 - timer bez zasilania
    - cyt2 (Integer): cycleTimer2 - timer z zasilaniem
    - Inventory przez saveInv()

    1.18.2 NBT:
    - storage_inv (CompoundTag): inwentarz magazynowy
    - plan_inv (CompoundTag): inwentarz planów
    - plan_slot (byte): aktywny slot planu
    - remaining_work (int): pozostała praca
    - total_work (int): całkowita praca
    - working (boolean): czy pracuje
    - charging (boolean): czy ładuje
    - vCap, iCap (double): stan kondensatora
    - chargeFlow (int): przepływ ładunku
    """

    SOURCE_1710 = "expansion/TileAutoCrafter.scala:54-66"
    SOURCE_1182 = "expansion/tile/AutoCrafterBlockEntity.java:55-68"

    @property
    def converter_name(self) -> str:
        return "auto_crafter"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        # Pobierz timery z 1.7.10
        cyt1 = nbt_1710.get("cyt1", 0)
        cyt2 = nbt_1710.get("cyt2", 0)

        # W 1.18.2 nie ma cyt1/cyt2 - używamy remaining_work/total_work
        # Jeśli timer był aktywny, konwertujemy na working state
        is_working = cyt1 > 0 or cyt2 > 0

        items_1710 = nbt_1710.get("items", [])

        # AutoCrafter layout w 1.7.10:
        # Sloty 0-8: plan grid (3x3)
        # Sloty 9+: storage
        plan_items = []
        storage_items = []

        for item in items_1710:
            if not item:
                continue
            slot = item.get("Slot", 0)
            if slot < 9:
                plan_items.append(item)
            else:
                new_item = dict(item)
                new_item["Slot"] = slot - 9
                storage_items.append(new_item)

        converted_nbt = {
            "storage_inv": {"Items": storage_items},
            "plan_inv": {"Items": plan_items},
            "plan_slot": 0,  # Domyślnie pierwszy slot
            "remaining_work": cyt2 if cyt2 > 0 else cyt1,  # Przybliżenie
            "total_work": 20,  # Domyślna wartość work
            "working": is_working,
            "charging": False,
            "vCap": 0.0,
            "iCap": 0.0,
            "chargeFlow": 0
        }

        if is_working:
            self._add_warning("TIMER-CONVERSION",
                            f"cyt1={cyt1}, cyt2={cyt2} skonwertowane na remaining_work - może być nieprecyzyjne")

        return self._create_result(converted_nbt)


class DeployerConverter(BaseNBTConverter):
    """
    Konwerter dla TileBlockPlacer (1.7.10) -> DeployerBlockEntity (1.18.2)

    UWAGA: BlockPlacer został zastąpiony przez Deployer w 1.18.2

    Source mapping:
    1.7.10 NBT (TileBlockPlacer):
    - Brak specjalnych tagów (dziedziczy z TileMachine)

    1.18.2 NBT (DeployerBlockEntity):
    - queue (CompoundTag): kolejka
    - schedTick (long): zaplanowany tick
    - side (byte): strona
    - powered (boolean): czy zasilany
    - active (boolean): czy aktywny
    """

    SOURCE_1710 = "expansion/TileBlockPlacer.scala (brak dodatkowych tagów)"
    SOURCE_1182 = "expansion/tile/DeployerBlockEntity.java"

    @property
    def converter_name(self) -> str:
        return "deployer"

    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        self.reset()

        self._add_warning("BLOCK-REPLACED",
                         "TileBlockPlacer zastąpiony przez Deployer - funkcjonalność może się różnić")

        side = self._metadata_to_side(metadata)
        facing = self._side_to_facing(side)

        converted_nbt = {
            "queue": {},
            "schedTick": -1,
            "side": side,
            "powered": False,
            "active": False
        }

        blockstate_props = {"facing": facing}

        return self._create_result(converted_nbt, blockstate_props)
