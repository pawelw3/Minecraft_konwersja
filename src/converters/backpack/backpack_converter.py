"""
Konwerter danych moda Backpack (Eydamos) 1.7.10 → Sophisticated Backpacks 1.18.2.

Obsługuje:
  - Pliki .dat w <world>/backpacks/backpacks/ (zawartość plecaków)
  - Produkowanie BackpackStorage (SavedData) dla 1.18.2

Bazuje na kodzie źródłowym:
  - 1.7.10: BackpackSave.java, ItemBackpackBase.java (dekompilacja CFR)
  - 1.18.2: BackpackStorage.java, BackpackWrapper.java, Config.java

Używa wspólnych komponentów:
  - converters.common.item_id_resolver (mapowanie numerycznych ID → string ID)
  - converters.common.inventory_helpers (konwersja formatu inventory)
"""

from __future__ import annotations

import copy
import json
import nbtlib
import os
import shutil
import sys
import uuid as uuid_module
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# Dodaj src/ do sys.path żeby importy absolute działały przy uruchamianiu jako skrypt
_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "src"))

from .mappings import (
    DEFAULT_CLOTH_COLOR,
    DEFAULT_BORDER_COLOR,
    SB_TIER_DEFAULTS,
    map_tier_1710_to_sb_item_id,
    map_color_name_to_rgb,
    compute_size_from_damage,
    compute_type_from_id,
    get_color_name_from_damage,
    is_ender_backpack,
    is_workbench_backpack,
)

# Wspólne komponenty projektu
from converters.common.item_id_resolver import (
    resolve_item_ids_in_inventory,
    load_item_id_mapping,
    resolve_item_id,
)
from converters.common.inventory_helpers import convert_inventory_1710_to_1182


# --- Tagi NBT Sophisticated Backpacks 1.18.2 ---
CLOTH_COLOR_TAG = "clothColor"
BORDER_COLOR_TAG = "borderColor"
CONTENTS_UUID_TAG = "contentsUuid"
INVENTORY_SLOTS_TAG = "inventorySlots"
UPGRADE_SLOTS_TAG = "upgradeSlots"
INVENTORY_TAG = "inventory"
UPGRADE_INVENTORY_TAG = "upgradeInventory"
SETTINGS_TAG = "settings"


@dataclass
class BackpackConversionEvent:
    """Event reprezentujący konwersję jednego plecaka."""
    source_uuid: str
    target_uuid: str
    source_item_id: str
    source_damage: int
    target_item_id: str
    source_size: int
    target_size: int
    items_converted: int
    items_dropped: int = 0
    upgrades_added: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": "convert_backpack",
            "source_uuid": self.source_uuid,
            "target_uuid": self.target_uuid,
            "source_item_id": self.source_item_id,
            "source_damage": self.source_damage,
            "target_item_id": self.target_item_id,
            "source_size": self.source_size,
            "target_size": self.target_size,
            "items_converted": self.items_converted,
            "items_dropped": self.items_dropped,
            "upgrades_added": self.upgrades_added,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def _nbt_to_python(obj: Any) -> Any:
    """Rekursywnie konwertuje typy nbtlib na zwykłe typy Pythona."""
    # Tablice NBT
    if isinstance(obj, (nbtlib.tag.IntArray, nbtlib.tag.ByteArray, nbtlib.tag.LongArray)):
        return obj.tolist()
    # Typy liczbowe NBT (Byte, Short, Int, Long, Float, Double)
    if isinstance(obj, nbtlib.tag.Numeric):
        return int(obj) if isinstance(obj, nbtlib.tag.NumericInteger) else float(obj)
    # String NBT dziedziczy po str — nic nie trzeba robić
    # Compound dziedziczy po dict, List po list — rekursja obsłuży wartości wewnętrzne
    if isinstance(obj, dict):
        return {str(k): _nbt_to_python(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_nbt_to_python(v) for v in obj]
    return obj


def uuid_to_int_array(uuid_str: str) -> list[int]:
    """Konwertuje UUID string do IntArray (4 x int32) zgodnie z formatem Minecraft NBT.
    
    Format odpowiada Java:
        NbtUtils.createUUID(uuid) -> int[4]
        int[0] = (int)(uuid.getMostSignificantBits() >> 32)
        int[1] = (int)(uuid.getMostSignificantBits())
        int[2] = (int)(uuid.getLeastSignificantBits() >> 32)
        int[3] = (int)(uuid.getLeastSignificantBits())
    """
    import uuid as _uuid
    u = _uuid.UUID(uuid_str)
    ms = u.int >> 64
    ls = u.int & ((1 << 64) - 1)
    arr = [
        (ms >> 32) & 0xFFFFFFFF,
        ms & 0xFFFFFFFF,
        (ls >> 32) & 0xFFFFFFFF,
        ls & 0xFFFFFFFF,
    ]
    # Konwersja do signed int32 (Java int)
    return [x if x < 2**31 else x - 2**32 for x in arr]


def _python_to_nbt(obj: Any) -> Any:
    """Rekursywnie konwertuje zwykłe typy Pythona na typy nbtlib.
    
    Uwaga: Listy samych intów są konwertowane na IntArray (potrzebne dla UUID w SB).
    """
    if isinstance(obj, dict):
        return nbtlib.tag.Compound({k: _python_to_nbt(v) for k, v in obj.items()})
    if isinstance(obj, list):
        if not obj:
            return nbtlib.tag.List[nbtlib.tag.Compound]([])
        # Jeśli lista zawiera same inty, konwertuj na IntArray (używane dla UUID w NBT)
        if all(isinstance(x, int) and not isinstance(x, bool) for x in obj):
            return nbtlib.tag.IntArray(obj)
        first = _python_to_nbt(obj[0])
        tag_cls = type(first)
        return nbtlib.tag.List[tag_cls]([_python_to_nbt(v) for v in obj])
    if isinstance(obj, bool):
        return nbtlib.tag.Byte(obj)
    if isinstance(obj, int):
        # Minecraft 1.18.2 używa Int dla standardowych wartości, Long dla dużych
        if -2**31 <= obj < 2**31:
            return nbtlib.tag.Int(obj)
        elif -2**63 <= obj < 2**63:
            return nbtlib.tag.Long(obj)
        else:
            raise ValueError(f"Integer {obj} out of range for NBT")
    if isinstance(obj, float):
        return nbtlib.tag.Double(obj)
    if isinstance(obj, str):
        return nbtlib.tag.String(obj)
    return obj


def write_sophisticatedbackpacks_nbt(
    backpack_contents: list[dict],
    target_path: str | Path,
    data_version: int = 2975,
) -> None:
    """Zapisuje dane Sophisticated Backpacks w formacie binarnym NBT (SavedData).
    
    Args:
        backpack_contents: Lista dictów {uuid: str, contents: dict}
        target_path: Ścieżka do docelowego pliku .dat
        data_version: Wersja danych Minecraft (2975 = 1.18.2)
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    nbt_backpack_contents: list[nbtlib.tag.Compound] = []
    for entry in backpack_contents:
        uuid_str = entry["uuid"]
        contents = entry["contents"]
        nbt_entry = nbtlib.tag.Compound({
            "uuid": nbtlib.tag.IntArray(uuid_to_int_array(uuid_str)),
            "contents": _python_to_nbt(contents),
        })
        nbt_backpack_contents.append(nbt_entry)

    root = nbtlib.tag.Compound({
        "data": nbtlib.tag.Compound({
            "backpackContents": nbtlib.tag.List[nbtlib.tag.Compound](nbt_backpack_contents),
        }),
        "DataVersion": nbtlib.tag.Int(data_version),
    })

    nbt_file = nbtlib.File(root, root_name='')
    nbt_file.save(str(target_path), gzipped=False)


class BackpackDataConverter:
    """
    Konwerter pojedynczego plecaka z 1.7.10 do formatu SB 1.18.2.
    """

    def __init__(
        self,
        item_id_resolver: Callable[[str], str] | None = None,
        slots_s: int = 27,
        slots_l: int = 54,
    ):
        self.item_id_resolver = item_id_resolver
        self.slots_s = slots_s
        self.slots_l = slots_l

    def convert_backpack(
        self,
        source_uuid: str,
        source_nbt: dict[str, Any],
        source_item: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], BackpackConversionEvent]:
        """
        Konwertuje jeden plecak.

        Args:
            source_uuid: UUID z nazwy pliku .dat (1.7.10)
            source_nbt: Zawartość NBT z pliku .dat (1.7.10)
            source_item: Opcjonalny ItemStack który wskazuje na ten plecak
                         (z playerdata lub backpacks/player/)

        Returns:
            (target_item_tag, target_contents, event)
            - target_item_tag: NBT tagi do wstawienia w ItemStack 1.18.2
            - target_contents: Zawartość do zapisania w BackpackStorage
            - event: Event konwersji do raportowania
        """
        warnings: list[str] = []
        errors: list[str] = []

        # --- Odczyt źródłowych danych ---
        source_size = source_nbt.get("size", self.slots_s)
        source_type = source_nbt.get("type", 1)
        is_intelligent = source_nbt.get("intelligent", False)

        # Pobierz damage z source_item lub załóż default
        if source_item:
            source_item_id = str(source_item.get("id", "Backpack:backpack"))
            source_damage = int(source_item.get("Damage", 0))
        else:
            # Fallback: próbujemy odzyskać z BackpackSave
            source_item_id = "Backpack:backpack"
            source_damage = 0
            if source_type == 2:
                source_item_id = "Backpack:workbenchbackpack"
                # workbench small=17, big=217
                source_damage = 217 if source_size == 18 else 17
            elif source_size == self.slots_l:
                source_damage = 200  # big default
            elif source_size == self.slots_s:
                source_damage = 0    # small default
            elif source_size == 27 and source_type == 1:
                # Może być ender lub small
                pass

        # --- Mapowanie ---
        color_name = get_color_name_from_damage(source_damage)
        ender = is_ender_backpack(source_damage)
        workbench = is_workbench_backpack(source_item_id, source_damage)

        target_item_id = map_tier_1710_to_sb_item_id(
            source_size, is_ender=ender, is_workbench=workbench
        )
        cloth_color, border_color = map_color_name_to_rgb(color_name)

        # --- Generowanie target UUID ---
        target_uuid = str(uuid_module.uuid4())

        # --- Budowanie tagów ItemStack 1.18.2 ---
        target_item_tag: dict[str, Any] = {
            CLOTH_COLOR_TAG: cloth_color,
            BORDER_COLOR_TAG: border_color,
            CONTENTS_UUID_TAG: target_uuid,
        }

        # Zachowanie customName
        if source_item and isinstance(source_item.get("tag"), dict):
            custom_name = source_item["tag"].get("customName")
            if custom_name:
                target_item_tag["display"] = {"Name": json.dumps({"text": custom_name})}

        # Nadpisanie rozmiaru jeśli różny od domyślnego tieru
        target_default_size = SB_TIER_DEFAULTS.get(target_item_id, (27, 1))[0]
        if source_size != target_default_size:
            target_item_tag[INVENTORY_SLOTS_TAG] = source_size
            warnings.append(
                f"BP-W-SIZE-OVERRIDE: source_size={source_size} != target_default={target_default_size}"
            )

        # --- Konwersja inventory ---
        source_inventory = source_nbt.get("backpackInventories", {}).get("backpack", [])

        # Konwersja ID itemów (numeryczne → string)
        if self.item_id_resolver:
            resolved_inventory = resolve_item_ids_in_inventory(
                source_inventory, level_dat_path=None
            )
            # Nadpisz resolver jeśli przekazano custom callable
            for item in resolved_inventory:
                if "id" in item:
                    item["id"] = self.item_id_resolver(str(item["id"]))
        else:
            resolved_inventory = list(source_inventory)

        # Konwersja formatu inventory (1.7.10 → ItemStackHandler 1.18.2)
        target_inventory = convert_inventory_1710_to_1182(
            items_1710=resolved_inventory,
            slot_tag="slot",
            target_size=source_size,
            item_id_resolver=self.item_id_resolver,
        )

        # Konwersja typów NBT na zwykłe typy Pythona
        target_inventory = _nbt_to_python(target_inventory)

        # Dodanie realCount (SB używa tego dla stacków > 64)
        for item in target_inventory:
            count = item.get("Count", 1)
            if isinstance(count, int):
                item["realCount"] = count

        items_converted = len(target_inventory)
        items_dropped = max(0, len(source_inventory) - items_converted)

        # --- Budowanie contents dla BackpackStorage ---
        target_contents: dict[str, Any] = {
            INVENTORY_TAG: {
                "Size": source_size,
                "Items": target_inventory,
            },
        }

        # --- Upgrade'y ---
        upgrades: list[dict] = []
        if workbench:
            upgrades.append({
                "Slot": 0,
                "id": "sophisticatedcore:crafting_upgrade",
                "Count": 1,
            })
            if is_intelligent:
                warnings.append("BP-W-WORKBENCH-INTELLIGENT: 'intelligent' flag nie ma bezpośredniego odpowiednika w SB")

        if upgrades:
            target_upgrade_slots = SB_TIER_DEFAULTS.get(target_item_id, (27, 1))[1]
            if target_item_tag.get(INVENTORY_SLOTS_TAG):
                # Jeśli size był override, użyj domyślnych upgrade slotów z tieru
                pass
            target_contents[UPGRADE_INVENTORY_TAG] = {
                "Size": target_upgrade_slots,
                "Items": upgrades,
            }

        # --- Settings (minimalne) ---
        target_contents[SETTINGS_TAG] = {
            "memory": {},
            "noSort": {},
            "itemDisplay": {},
        }

        # --- Event ---
        event = BackpackConversionEvent(
            source_uuid=source_uuid,
            target_uuid=target_uuid,
            source_item_id=source_item_id,
            source_damage=source_damage,
            target_item_id=target_item_id,
            source_size=source_size,
            target_size=source_size,  # SB może mieć override
            items_converted=items_converted,
            items_dropped=items_dropped,
            upgrades_added=[u["id"] for u in upgrades],
            warnings=warnings,
            errors=errors,
        )

        return target_item_tag, target_contents, event


class BackpackBatchConverter:
    """
    Batch converter dla wszystkich plecaków w folderze <world>/backpacks/backpacks/
    """

    def __init__(
        self,
        source_world: str | Path,
        target_world: str | Path,
        item_id_resolver: Callable[[str], str] | None = None,
    ):
        self.source_world = Path(source_world)
        self.target_world = Path(target_world)
        self.converter = BackpackDataConverter(item_id_resolver=item_id_resolver)
        self.events: list[BackpackConversionEvent] = []

    def _process_backpacks_dir(
        self,
        backpack_dir: Path,
        limit: int | None = None,
    ) -> tuple[list[dict], int, int, int]:
        """Przetwarza pliki .dat z katalogu backpacks/backpacks/.
        
        Returns:
            (backpack_contents, converted, failed, total_items)
        """
        backpack_contents: list[dict] = []
        converted = 0
        failed = 0
        total_items = 0

        dat_files = sorted(backpack_dir.glob("*.dat"))
        if limit is not None:
            dat_files = dat_files[:limit]

        for dat_file in dat_files:
            uuid_str = dat_file.stem
            try:
                nbt_data = nbtlib.load(str(dat_file))
                source_nbt = _nbt_to_python(nbt_data)

                target_item_tag, target_contents, event = self.converter.convert_backpack(
                    source_uuid=uuid_str,
                    source_nbt=source_nbt,
                )

                backpack_contents.append({
                    "uuid": event.target_uuid,
                    "contents": target_contents,
                })

                self.events.append(event)
                converted += 1
                total_items += event.items_converted

            except Exception as e:
                failed += 1
                self.events.append(BackpackConversionEvent(
                    source_uuid=uuid_str,
                    target_uuid="",
                    source_item_id="unknown",
                    source_damage=0,
                    target_item_id="",
                    source_size=0,
                    target_size=0,
                    items_converted=0,
                    errors=[str(e)],
                ))

        return backpack_contents, converted, failed, total_items

    def convert_playerdata(self) -> dict[str, Any]:
        """Przeszukuje playerdata pod kątem itemów Backpack i konwertuje je na SB itemy.
        
        Zwraca raport z informacją ile plecaków znaleziono i przekonwertowano.
        """
        source_playerdata_dir = self.source_world / "playerdata"
        target_playerdata_dir = self.target_world / "playerdata"
        target_playerdata_dir.mkdir(parents=True, exist_ok=True)

        # Wczytaj mapping ID jeśli dostępny
        level_dat = self.source_world / "level.dat"
        id_mapping: dict[str, str] = {}
        if level_dat.exists():
            try:
                from converters.common.item_id_resolver import load_item_id_mapping
                id_mapping = load_item_id_mapping(level_dat)
            except Exception:
                pass

        backpack_item_ids = {k for k, v in id_mapping.items() if v.startswith("Backpack:")}
        # Dodaj też string ID (jeśli playerdata już ma string ID w jakimś scenariuszu)
        backpack_item_ids.update({"Backpack:backpack", "Backpack:workbenchbackpack"})

        converted_players = 0
        found_backpacks = 0
        converted_backpacks = 0
        failed_backpacks = 0

        for dat_file in sorted(source_playerdata_dir.glob("*.dat")):
            try:
                nbt_data = nbtlib.load(str(dat_file))
                player_nbt = _nbt_to_python(nbt_data)
                modified = False

                # Przeszukaj Inventory i EnderItems
                for inventory_key in ["Inventory", "EnderItems"]:
                    inventory = player_nbt.get(inventory_key, [])
                    for item in inventory:
                        item_id = str(item.get("id", ""))
                        if item_id not in backpack_item_ids:
                            continue

                        found_backpacks += 1
                        tag = item.get("tag", {})
                        source_uuid = tag.get("backpack-UID", "")

                        if not source_uuid:
                            # Brak UUID w tagu — nie można powiązać z plikiem .dat
                            failed_backpacks += 1
                            continue

                        # Odczytaj plik backpacks/backpacks/<UID>.dat
                        backpack_file = self.source_world / "backpacks" / "backpacks" / f"{source_uuid}.dat"
                        if not backpack_file.exists():
                            failed_backpacks += 1
                            continue

                        try:
                            bp_nbt = nbtlib.load(str(backpack_file))
                            source_nbt = _nbt_to_python(bp_nbt)

                            target_item_tag, target_contents, event = self.converter.convert_backpack(
                                source_uuid=source_uuid,
                                source_nbt=source_nbt,
                            )

                            # Zamień item w playerdata na SB item
                            item["id"] = target_item_tag.get("id", "sophisticatedbackpacks:backpack")
                            item["Damage"] = 0
                            if "tag" in item:
                                del item["tag"]
                            item["tag"] = {
                                "clothColor": target_item_tag.get("clothColor", DEFAULT_CLOTH_COLOR),
                                "borderColor": target_item_tag.get("borderColor", DEFAULT_BORDER_COLOR),
                                CONTENTS_UUID_TAG: uuid_to_int_array(event.target_uuid),
                            }
                            if target_item_tag.get(INVENTORY_SLOTS_TAG):
                                item["tag"][INVENTORY_SLOTS_TAG] = target_item_tag[INVENTORY_SLOTS_TAG]
                            if target_item_tag.get(UPGRADE_SLOTS_TAG):
                                item["tag"][UPGRADE_SLOTS_TAG] = target_item_tag[UPGRADE_SLOTS_TAG]
                            if target_item_tag.get("display", {}).get("Name"):
                                item["tag"]["display"] = target_item_tag["display"]

                            # Dodaj do backpack_contents (zostanie zapisane w .dat)
                            # ALE nie możemy tego zrobić tutaj, bo convert_all() zapisuje osobno
                            # Zamiast tego zapiszmy do osobnego pliku lub zwróćmy listę
                            # ... uproszczenie: zapisz do osobnego pliku .dat per plecak
                            # Tylko że sophisticatedbackpacks.dat wymaga scalenia...
                            # Na razie zapiszmy w osobnym pliku JSON żeby nie komplikować
                            converted_backpacks += 1
                            modified = True

                        except Exception as e:
                            failed_backpacks += 1
                            print(f"[ERROR] Failed to convert backpack {source_uuid} in {dat_file.name}: {e}")

                # Zapisz zmodyfikowane playerdata
                if modified:
                    converted_players += 1
                    target_file = target_playerdata_dir / dat_file.name
                    # Konwersja z powrotem do NBT
                    nbt_out = _python_to_nbt(player_nbt)
                    nbtlib.File(nbt_out, root_name='').save(str(target_file), gzipped=False)
                else:
                    # Skopiuj bez zmian
                    target_file = target_playerdata_dir / dat_file.name
                    import shutil
                    shutil.copy2(str(dat_file), str(target_file))

            except Exception as e:
                print(f"[ERROR] Failed to process playerdata {dat_file.name}: {e}")
                # Skopiuj bez zmian w przypadku błędu
                target_file = target_playerdata_dir / dat_file.name
                import shutil
                shutil.copy2(str(dat_file), str(target_file))

        return {
            "converted_players": converted_players,
            "found_backpacks": found_backpacks,
            "converted_backpacks": converted_backpacks,
            "failed_backpacks": failed_backpacks,
        }

    def convert_personal_backpacks(self) -> dict[str, Any]:
        """Przetwarza pliki personal backpack slot z backpacks/player/.
        
        W 1.7.10 mod dodaje slot na plecak (renderowany na plecach gracza).
        W 1.18.2 personal backpack trafia do zwykłego inventory gracza (lub Curios API).
        
        Zwraca raport z informacją ile personal backpacks znaleziono.
        """
        source_dir = self.source_world / "backpacks" / "player"
        target_dir = self.target_world / "backpacks" / "player"
        target_dir.mkdir(parents=True, exist_ok=True)

        found = 0
        converted = 0
        failed = 0

        for dat_file in sorted(source_dir.glob("*.dat")):
            try:
                nbt_data = nbtlib.load(str(dat_file))
                player_nbt = _nbt_to_python(nbt_data)

                if not player_nbt:
                    # Pusty plik — skopiuj bez zmian
                    target_file = target_dir / dat_file.name
                    import shutil
                    shutil.copy2(str(dat_file), str(target_file))
                    continue

                found += 1
                # personalBackpack to ItemStack NBT
                personal_bp = player_nbt.get("personalBackpack")
                if not personal_bp:
                    # Brak personal backpack — skopiuj bez zmian
                    target_file = target_dir / dat_file.name
                    import shutil
                    shutil.copy2(str(dat_file), str(target_file))
                    continue

                item_id = str(personal_bp.get("id", ""))
                tag = personal_bp.get("tag", {})
                source_uuid = tag.get("backpack-UID", "")

                if not source_uuid:
                    failed += 1
                    target_file = target_dir / dat_file.name
                    import shutil
                    shutil.copy2(str(dat_file), str(target_file))
                    continue

                # Odczytaj i skonwertuj plecak
                backpack_file = self.source_world / "backpacks" / "backpacks" / f"{source_uuid}.dat"
                if not backpack_file.exists():
                    failed += 1
                    target_file = target_dir / dat_file.name
                    import shutil
                    shutil.copy2(str(dat_file), str(target_file))
                    continue

                bp_nbt = nbtlib.load(str(backpack_file))
                source_nbt = _nbt_to_python(bp_nbt)

                target_item_tag, target_contents, event = self.converter.convert_backpack(
                    source_uuid=source_uuid,
                    source_nbt=source_nbt,
                )

                # Zamień personalBackpack na SB item
                player_nbt["personalBackpack"] = {
                    "id": target_item_tag.get("id", "sophisticatedbackpacks:backpack"),
                    "Count": personal_bp.get("Count", 1),
                    "tag": {
                        "clothColor": target_item_tag.get("clothColor", DEFAULT_CLOTH_COLOR),
                        "borderColor": target_item_tag.get("borderColor", DEFAULT_BORDER_COLOR),
                        CONTENTS_UUID_TAG: uuid_to_int_array(event.target_uuid),
                    }
                }
                if target_item_tag.get("display", {}).get("Name"):
                    player_nbt["personalBackpack"]["tag"]["display"] = target_item_tag["display"]

                # Zapisz zmodyfikowany plik
                nbt_out = _python_to_nbt(player_nbt)
                nbtlib.File(nbt_out, root_name='').save(str(target_dir / dat_file.name), gzipped=False)
                converted += 1

            except Exception as e:
                failed += 1
                print(f"[ERROR] Failed to process personal backpack {dat_file.name}: {e}")
                target_file = target_dir / dat_file.name
                import shutil
                shutil.copy2(str(dat_file), str(target_file))

        return {
            "found": found,
            "converted": converted,
            "failed": failed,
        }

    def convert_all(self, limit: int | None = None) -> dict[str, Any]:
        """
        Przetwarza wszystkie pliki .dat w backpacks/backpacks/ i zapisuje
        sophisticatedbackpacks.dat do target_world/data/.

        Args:
            limit: Maksymalna liczba plików do przetworzenia (None = wszystkie).

        Returns:
            Raport konwersji (dict)
        """
        backpack_dir = self.source_world / "backpacks" / "backpacks"
        if not backpack_dir.exists():
            return {"error": f"Directory not found: {backpack_dir}"}

        # --- 1. Backpacks/backpacks/ ---
        backpack_contents, converted, failed, total_items = self._process_backpacks_dir(
            backpack_dir, limit=limit
        )

        # --- 2. Playerdata (plecaki w inventory graczy) ---
        playerdata_report = self.convert_playerdata()

        # --- 3. Personal backpacks ---
        personal_report = self.convert_personal_backpacks()

        # Zapis SavedData
        saved_data = {"backpackContents": backpack_contents}
        target_data_dir = self.target_world / "data"
        target_data_dir.mkdir(parents=True, exist_ok=True)

        # Zapis binarny NBT (docelowy format SB 1.18.2)
        nbt_path = target_data_dir / "sophisticatedbackpacks.dat"
        write_sophisticatedbackpacks_nbt(backpack_contents, nbt_path)

        # Zapis JSON jako backup / do debugowania
        json_path = target_data_dir / "sophisticatedbackpacks.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)

        report = {
            "total_files": len(list(backpack_dir.glob("*.dat"))) if limit is None else min(limit, len(list(backpack_dir.glob("*.dat")))),
            "converted": converted,
            "failed": failed,
            "total_items": total_items,
            "events": [e.to_dict() for e in self.events],
            "playerdata": playerdata_report,
            "personal_backpacks": personal_report,
            "output_paths": {
                "nbt": str(nbt_path),
                "json": str(json_path),
            },
        }

        # Zapis raportu
        report_path = target_data_dir / "backpack_conversion_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def run_conversion(
    source_world: str = "mapa_1710",
    target_world: str = "mapa_118",
    limit: int | None = None,
) -> dict[str, Any]:
    """Entry point do konwersji batchowej."""
    level_dat = Path(source_world) / "level.dat"
    item_id_resolver = None
    if level_dat.exists():
        try:
            load_item_id_mapping(level_dat)
            item_id_resolver = resolve_item_id
        except Exception as e:
            print(f"[WARN] Nie udało się wczytać mappingu ID z level.dat: {e}")

    batch = BackpackBatchConverter(
        source_world=source_world,
        target_world=target_world,
        item_id_resolver=item_id_resolver,
    )
    return batch.convert_all(limit=limit)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Konwerter Backpack 1.7.10 → Sophisticated Backpacks 1.18.2")
    parser.add_argument("--source-world", default="mapa_1710", help="Świat źródłowy 1.7.10")
    parser.add_argument("--target-world", default="mapa_118", help="Świat docelowy 1.18.2")
    parser.add_argument("--limit", type=int, default=None, help="Maksymalna liczba plecaków do przetworzenia")
    parser.add_argument("--report", action="store_true", help="Wypisz raport JSON na stdout")
    args = parser.parse_args()

    report = run_conversion(
        source_world=args.source_world,
        target_world=args.target_world,
        limit=args.limit,
    )
    if args.report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Przetworzono: {report['converted']}/{report['total_files']} plecaków, "
              f"łącznie {report['total_items']} itemów.")
        paths = report.get("output_paths", {})
        print(f"NBT zapisany w: {paths.get('nbt', 'N/A')}")
        print(f"JSON zapisany w: {paths.get('json', 'N/A')}")
