"""NBT converters for Thermal Dynamics 1.7.10 -> 1.18.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NBTConversionResult:
    success: bool
    nbt_1182: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    # Dodatkowe itemy do zrzutu (np. załączniki)
    extra_items: list[dict[str, Any]] = field(default_factory=list)


class BaseTDNBTConverter:
    def convert(self, nbt_1710: dict[str, Any], target_block_id: str) -> NBTConversionResult:
        raise NotImplementedError


class IdentityTDConverter(BaseTDNBTConverter):
    """Minimalny konwerter: zachowuje tylko pozycję x,y,z."""

    def convert(self, nbt_1710: dict[str, Any], target_block_id: str) -> NBTConversionResult:
        nbt_1182: dict[str, Any] = {}
        for key in ("x", "y", "z"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]
        return NBTConversionResult(True, nbt_1182)


class DuctNBTConverter(BaseTDNBTConverter):
    """Konwerter dla ductów TD 1.18.2 (energy/fluid).

    TD 1.18.2 używa dynamicznych gridów — nie przechowuje topologii w NBT bloku.
    Załączniki (Servo/Filter/Retriever) nie mają bezpośredniego odpowiednika w TD 1.18.2
    (dla Itemductów) lub są kompatybilne (dla Energy/Fluid).
    """

    def convert(self, nbt_1710: dict[str, Any], target_block_id: str) -> NBTConversionResult:
        nbt_1182: dict[str, Any] = {}
        for key in ("x", "y", "z"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]

        warnings: list[str] = []
        extra_items: list[dict[str, Any]] = []

        # Odczytaj załączniki (attachment0..attachment5)
        for side in range(6):
            att_key = f"attachment{side}"
            if att_key in nbt_1710:
                att = nbt_1710[att_key]
                if isinstance(att, dict):
                    item = self._attachment_to_item(att)
                    if item:
                        extra_items.append(item)
                        warnings.append(
                            f"TD-W-ATTACHMENT-DROPPED: {item.get('id', 'unknown')} "
                            f"from side {side} dropped to chest (no direct 1.18.2 equivalent)."
                        )

        # Odczytaj facades/covery (facade0..facade5)
        for side in range(6):
            facade_key = f"facade{side}"
            if facade_key in nbt_1710:
                facade = nbt_1710[facade_key]
                if isinstance(facade, dict) and facade.get("block"):
                    warnings.append(
                        f"TD-W-FACADE-LOST: cover on side {side} "
                        f"({facade.get('block', 'unknown')}) lost during conversion."
                    )

        return NBTConversionResult(
            True,
            nbt_1182,
            warnings=warnings,
            extra_items=extra_items,
        )

    def _attachment_to_item(self, att_nbt: dict[str, Any]) -> dict[str, Any] | None:
        """Konwertuje NBT załącznika 1.7.10 na item do zrzutu.

        Załączniki w 1.7.10 mają pole 'type' które określa rodzaj i tier.
        Z dekompilacji: Servo/Filter/Retriever mają 5 tierów (meta % 5).
        """
        att_type = att_nbt.get("type", 0)
        # W ConnectionBase: type to int określający rodzaj załącznika
        # W praktyce: 0=brak, 1=Servo, 2=Filter, 3=Retriever (prawdopodobne wartości)
        # Tier określany przez metadata itemu (0=basic, 1=hardened, 2=reinforced, 3=signalum, 4=resonant)

        # Pobierz tier z NBT (jeśli dostępny)
        tier_meta = att_nbt.get("metadata", 0)
        if isinstance(tier_meta, str):
            try:
                tier_meta = int(tier_meta)
            except ValueError:
                tier_meta = 0
        tier = tier_meta % 5

        tier_names = ["basic", "hardened", "reinforced", "signalum", "resonant"]
        tier_name = tier_names[tier] if 0 <= tier < len(tier_names) else "basic"

        # Rozpoznaj typ załącznika na podstawie pól w NBT
        # Jeśli ma "filter" compound, to prawdopodobnie Filter lub Servo z filtrem
        # Jeśli ma "speed", to prawdopodobnie Servo
        has_filter = "filter" in att_nbt
        has_speed = "speed" in att_nbt

        item_id: str | None = None
        if has_speed and not has_filter:
            item_id = f"thermaldynamics:{tier_name}_servo"
        elif has_filter and not has_speed:
            item_id = f"thermaldynamics:{tier_name}_filter"
        elif has_speed and has_filter:
            # Servo z filtrem — zrzucamy jako Servo (filter jest wbudowany w TD 1.18.2 servo)
            item_id = f"thermaldynamics:{tier_name}_servo"
        else:
            # Domyślnie: Retriever lub inny typ
            item_id = f"thermaldynamics:{tier_name}_retriever"

        return {
            "id": item_id,
            "Count": 1,
            "tag": { "original_td_attachment_nbt": att_nbt },
        }


class MekanismTransporterConverter(BaseTDNBTConverter):
    """Konwerter dla Itemductów -> Mekanism Logistical Transporter.

    Mekanism transportery używają dynamicznej sieci — nie przechowują topologii w NBT.
    Załączniki (Servo/Filter/Retriever) nie mają odpowiednika w Mekanism.
    """

    def convert(self, nbt_1710: dict[str, Any], target_block_id: str) -> NBTConversionResult:
        nbt_1182: dict[str, Any] = {}
        for key in ("x", "y", "z"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]

        warnings: list[str] = []
        extra_items: list[dict[str, Any]] = []

        for side in range(6):
            att_key = f"attachment{side}"
            if att_key in nbt_1710:
                att = nbt_1710[att_key]
                if isinstance(att, dict):
                    item = self._attachment_to_mekanism_item(att)
                    if item:
                        extra_items.append(item)
                        warnings.append(
                            f"TD-W-ATTACHMENT-DROPPED: Mekanism transporters do not support "
                            f"Servo/Filter attachments. Dropped {item.get('id', 'unknown')} from side {side}."
                        )

        if extra_items:
            warnings.append(
                "TD-W-MEKANISM-ATTACHMENTS: Consider placing a mekanism:logistical_sorter "
                "nearby to replicate Servo/Filter functionality."
            )

        return NBTConversionResult(True, nbt_1182, warnings=warnings, extra_items=extra_items)

    def _attachment_to_mekanism_item(self, att_nbt: dict[str, Any]) -> dict[str, Any] | None:
        # Dla Itemductów konwertowanych na Mekanism, zrzucamy oryginalne załączniki TD
        # jako itemy (gracz może je użyć w TD 1.18.2 na energy/fluid ductach, lub sprzedać/zutylizować)
        att_type = att_nbt.get("type", 0)
        tier_meta = att_nbt.get("metadata", 0)
        if isinstance(tier_meta, str):
            try:
                tier_meta = int(tier_meta)
            except ValueError:
                tier_meta = 0
        tier = tier_meta % 5
        tier_names = ["basic", "hardened", "reinforced", "signalum", "resonant"]
        tier_name = tier_names[tier] if 0 <= tier < len(tier_names) else "basic"

        has_filter = "filter" in att_nbt
        has_speed = "speed" in att_nbt

        if has_speed and not has_filter:
            item_id = f"thermaldynamics:{tier_name}_servo"
        elif has_filter and not has_speed:
            item_id = f"thermaldynamics:{tier_name}_filter"
        elif has_speed and has_filter:
            item_id = f"thermaldynamics:{tier_name}_servo"
        else:
            item_id = f"thermaldynamics:{tier_name}_retriever"

        return {
            "id": item_id,
            "Count": 1,
            "tag": { "original_td_attachment_nbt": att_nbt },
        }


class MekanismTeleporterConverter(BaseTDNBTConverter):
    """Konwerter dla Viaductów -> Mekanism Teleporter.

    Teleporter wymaga częstotliwości. Viaducty w 1.7.10 nie mają częstotliwości,
    więc generujemy pustą/pobieżną konfigurację.
    """

    def convert(self, nbt_1710: dict[str, Any], target_block_id: str) -> NBTConversionResult:
        nbt_1182: dict[str, Any] = {}
        for key in ("x", "y", "z"):
            if key in nbt_1710:
                nbt_1182[key] = nbt_1710[key]

        # Teleporter w Mekanism 1.18.2 używa NBT z częstotliwością
        # Ponieważ Viaduct nie miał częstotliwości, ustawiamy domyślną 0
        nbt_1182["frequency"] = { "type": 0, "name": "" }
        nbt_1182["color"] = 0  # brak koloru

        warnings = [
            "TD-W-TELEPORTER-FREQ: Viaduct had no frequency. "
            "Teleporter set to default frequency 0. Manual reconfiguration required."
        ]

        return NBTConversionResult(True, nbt_1182, warnings=warnings)


__all__ = [
    "NBTConversionResult",
    "BaseTDNBTConverter",
    "IdentityTDConverter",
    "DuctNBTConverter",
    "MekanismTransporterConverter",
    "MekanismTeleporterConverter",
]
