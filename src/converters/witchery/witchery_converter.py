"""Witchery mod converter: 1.7.10 → 1.18.2.

UWAGA – UPROSZCZONA KONWERSJA (TYLKO PLACEHOLDERY)
===================================================
Witchery nie ma portu na 1.18.2.  Wszystkie TileEntities są konwertowane
na ``conversion_placeholders:block_entity_placeholder`` (lub
``inventory_placeholder`` gdy TE zawiera przedmioty).

Pełne oryginalne NBT jest zachowywane w polu ``original_nbt`` placeholdera,
co umożliwia ręczne odtworzenie zawartości po ewentualnej przyszłej instalacji
zamiennika (Hexerei, Enchanted: Witchcraft itp.).

Nie jest wykonywana żadna faktyczna konwersja danych – jest to świadomy wybór
wynikający z braku odpowiednika moda w docelowej paczce 1.18.2.
"""
from __future__ import annotations

from typing import Any

from converters.common.placeholders import make_block_entity_placeholder_event
from converters.witchery.mappings import (
    WITCHERY_TE_IDS,
    TE_ID_TO_BLOCK_REGISTRY,
    TE_ID_TO_GROUP,
)

_SOURCE_MOD = "witchery"
_CONVERSION_REASON = "no_118_equivalent"


class WitcheryConverter:
    """Konwertuje wszystkie TileEntities Witchery na placeholder eventy.

    UPROSZCZONA KONWERSJA – żadne dane nie są przekształcane.
    Oryginalne NBT (inwentarze, stan pieca, dane gracza itp.) jest
    zachowywane w polu ``original_nbt`` placeholdera.
    """

    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = _SOURCE_MOD
    CONVERSION_TYPE = "placeholder_only"  # jawne oznaczenie trybu

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> list[dict[str, Any]]:
        """Zwraca pojedynczy placeholder event dla dowolnego TE Witchery.

        Wszystkie oryginalne pola NBT (inwentarze, power, owner, stan rytuału
        itp.) są zachowywane w ``original_nbt``.  Jeśli TE zawiera przedmioty
        (pole ``Items``, ``contents`` itp.), event używa ``inventory_placeholder``
        żeby sygnalizować że zawartość powinna być odtworzona ręcznie.

        Zwraca listę z jednym eventem (dla spójności z interfejsem routera).
        """
        block_registry = TE_ID_TO_BLOCK_REGISTRY.get(te_id, te_id)
        group = TE_ID_TO_GROUP.get(te_id, "witchery_unknown")

        event = make_block_entity_placeholder_event(
            position=position,
            source_mod=_SOURCE_MOD,
            source_te_id=te_id,
            source_block_id=block_registry,
            source_metadata=metadata,
            original_nbt=nbt_1710,
            conversion_reason=_CONVERSION_REASON,
            conversion_stage=group,
        )
        return [event]

    def is_known_te(self, te_id: str) -> bool:
        """Zwraca True gdy te_id należy do Witchery."""
        return te_id in WITCHERY_TE_IDS or te_id.startswith("witchery:")
