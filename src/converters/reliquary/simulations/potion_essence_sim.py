"""
Symulacja konwersji PotionEssence: format XR 1.7.10 → PotionContents 1.18.2

Source 1.7.10:
  xreliquary.util.potions.PotionEssence.writeToNBT() / constructor(NBTTagCompound)
  Format NBT: {effects: [{id:<int>, duration:<int>, potency:<int>}, ...]}

Source 1.18.2:
  reliquary.util.potions.PotionHelper.addPotionContentsToCompoundTag()
  reliquary.util.potions.PotionHelper.getPotionContentsFromCompoundTag()
  Format NBT: {effects: <PotionContents_codec_output>}
  gdzie PotionContents codec produkuje: {custom_effects: [{id:<str>, duration:<int>,
    amplifier:<int>, ambient:<bool>, show_particles:<bool>, show_icon:<bool>}, ...]}

Kluczowa różnica:
  - 1.7.10: id jest int (vanilla numeric potion ID), potency=amplifier
  - 1.18.2: id jest string ResourceLocation, pola ambient/show_particles/show_icon dodane
  - Klucz zewnętrzny "effects" to samo (EFFECTS_TAG = "effects" w PotionHelper)

Mapowanie efektów instant vs. timed:
  - 1.7.10: Potion.potionTypes[id].isInstant() → zapisuje duration=1
  - 1.18.2: analogicznie, instant effects mają duration=1
  - Efekty instant (ID 6 = instant_health, ID 7 = instant_damage): duration ignorowany w grze
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


# Mapowanie numerycznych potion ID (1.7.10 vanilla) → ResourceLocation (1.18.2)
# Źródło: net.minecraft.potion.Potion w 1.7.10 i net.minecraft.world.effect.MobEffects w 1.18.2
POTION_ID_TO_RESOURCE = {
    1:  "minecraft:speed",
    2:  "minecraft:slowness",
    3:  "minecraft:haste",
    4:  "minecraft:mining_fatigue",
    5:  "minecraft:strength",
    6:  "minecraft:instant_health",
    7:  "minecraft:instant_damage",
    8:  "minecraft:jump_boost",
    9:  "minecraft:nausea",
    10: "minecraft:regeneration",
    11: "minecraft:resistance",
    12: "minecraft:fire_resistance",
    13: "minecraft:water_breathing",
    14: "minecraft:invisibility",
    15: "minecraft:blindness",
    16: "minecraft:night_vision",
    17: "minecraft:hunger",
    18: "minecraft:weakness",
    19: "minecraft:poison",
    20: "minecraft:wither",
    21: "minecraft:health_boost",
    22: "minecraft:absorption",
    23: "minecraft:saturation",
}

# Efekty instant (duration = 1 zawsze, niezależnie od zapisanego)
INSTANT_EFFECT_IDS = {6, 7}  # instant_health, instant_damage


@dataclass
class PotionEffect1710:
    """Efekt eliksiru w formacie 1.7.10 XR NBT."""
    id: int           # numeryczny ID efektu
    duration: int     # czas trwania w tickach (1 dla instant)
    potency: int      # amplifier (0-based: 0 = poziom I)

    @classmethod
    def from_nbt(cls, nbt: Dict[str, Any]) -> "PotionEffect1710":
        return cls(
            id=nbt["id"],
            duration=nbt["duration"],
            potency=nbt["potency"],
        )

    def to_nbt(self) -> Dict[str, Any]:
        return {"id": self.id, "duration": self.duration, "potency": self.potency}

    def is_instant(self) -> bool:
        return self.id in INSTANT_EFFECT_IDS


@dataclass
class PotionEffect1182:
    """Efekt eliksiru w formacie 1.18.2 PotionContents codec."""
    id: str           # ResourceLocation, np. "minecraft:speed"
    duration: int     # czas trwania w tickach
    amplifier: int    # 0-based
    ambient: bool = False
    show_particles: bool = True
    show_icon: bool = True

    def to_nbt(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "duration": self.duration,
            "amplifier": self.amplifier,
            "ambient": self.ambient,
            "show_particles": self.show_particles,
            "show_icon": self.show_icon,
        }

    def is_instant(self) -> bool:
        return self.id in {"minecraft:instant_health", "minecraft:instant_damage"}


class PotionEssenceConverter:
    """
    Konwertuje PotionEssence z formatu NBT 1.7.10 (XR) na PotionContents 1.18.2.

    W kodzie 1.18.2:
      - TE zapisuje przez: PotionHelper.addPotionContentsToCompoundTag(tag, potionContents)
        → tag.put("effects", POTION_CONTENTS_CODEC.encode(potionContents))
      - TE wczytuje przez: PotionHelper.getPotionContentsFromCompoundTag(tag)
        → POTION_CONTENTS_CODEC.parse(tag.get("effects"))

    Symulacja operuje na Python dict reprezentującym NBT.
    """

    def convert_effect(self, effect_1710: PotionEffect1710) -> Optional[PotionEffect1182]:
        """
        Konwertuje jeden efekt 1.7.10 → 1.18.2.

        Returns None jeśli ID efektu nie jest znane (nie jest vanilla efektem).
        """
        resource_loc = POTION_ID_TO_RESOURCE.get(effect_1710.id)
        if resource_loc is None:
            return None

        duration = 1 if effect_1710.is_instant() else effect_1710.duration
        return PotionEffect1182(
            id=resource_loc,
            duration=duration,
            amplifier=effect_1710.potency,
        )

    def convert_essence_nbt(self, essence_nbt_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT PotionEssence 1.7.10 → NBT w formacie PotionContents 1.18.2.

        Args:
            essence_nbt_1710: dict z kluczem "effects" (lista efektów 1.7.10).
                Odpowiada zawartości {effects:[{id,duration,potency},...]} zapisanej
                przez PotionEssence.writeToNBT() w 1.7.10.

        Returns:
            dict w formacie wyjścia DataComponents.POTION_CONTENTS.codec().encode(),
            czyli {custom_effects:[{id,duration,amplifier,ambient,...}]}.
            Ten dict jest wstawiany pod kluczem "effects" w NBT TE.
        """
        raw_effects = essence_nbt_1710.get("effects", [])
        converted: List[Dict[str, Any]] = []
        warnings: List[str] = []

        for raw in raw_effects:
            eff_1710 = PotionEffect1710.from_nbt(raw)
            eff_1182 = self.convert_effect(eff_1710)
            if eff_1182 is None:
                warnings.append(f"Nieznany potion ID {eff_1710.id} – pomijam efekt")
                continue
            converted.append(eff_1182.to_nbt())

        result = {}
        if converted:
            result["custom_effects"] = converted

        return result, warnings

    def build_cauldron_effects_tag(self, essence_nbt_1710: Dict[str, Any]) -> tuple:
        """
        Zwraca (effects_tag_1182, warnings) do wstawienia jako tag["effects"] w NBT kauldron.

        Odpowiada wywołaniu PotionHelper.addPotionContentsToCompoundTag(tag, potionContents).
        """
        return self.convert_essence_nbt(essence_nbt_1710)


# --- Przykładowe dane 1.7.10 ---

SAMPLE_ESSENCE_SPEED_REGEN = {
    "effects": [
        {"id": 1,  "duration": 900,  "potency": 0},  # Speed I, 45s
        {"id": 10, "duration": 300,  "potency": 0},  # Regeneration I, 15s
    ]
}

SAMPLE_ESSENCE_STRENGTH_FIRE = {
    "effects": [
        {"id": 5,  "duration": 1800, "potency": 1},  # Strength II, 90s
        {"id": 12, "duration": 3600, "potency": 0},  # Fire Resistance I, 3min
    ]
}

SAMPLE_ESSENCE_INSTANT_HARM = {
    "effects": [
        {"id": 7,  "duration": 1, "potency": 0},  # Instant Damage I (instant)
        {"id": 18, "duration": 300, "potency": 0}, # Weakness I, 15s
    ]
}

SAMPLE_ESSENCE_MULTI = {
    "effects": [
        {"id": 1,  "duration": 900,  "potency": 0},  # Speed
        {"id": 3,  "duration": 300,  "potency": 0},  # Haste
        {"id": 10, "duration": 600,  "potency": 1},  # Regeneration II (30s)
        {"id": 22, "duration": 1200, "potency": 0},  # Absorption
    ]
}

SAMPLE_ESSENCE_UNKNOWN_ID = {
    "effects": [
        {"id": 99, "duration": 300, "potency": 0},  # Nieznany ID (mod efekt)
        {"id": 1,  "duration": 900, "potency": 0},  # Speed
    ]
}


def run_demo():
    """Demonstracja konwersji wszystkich próbek."""
    converter = PotionEssenceConverter()
    samples = [
        ("Speed + Regeneration", SAMPLE_ESSENCE_SPEED_REGEN),
        ("Strength II + Fire Resistance", SAMPLE_ESSENCE_STRENGTH_FIRE),
        ("Instant Damage + Weakness", SAMPLE_ESSENCE_INSTANT_HARM),
        ("Multi-efekt (4 efekty)", SAMPLE_ESSENCE_MULTI),
        ("Nieznany ID (mod efekt)", SAMPLE_ESSENCE_UNKNOWN_ID),
    ]

    for name, sample in samples:
        print(f"\n=== {name} ===")
        result, warnings = converter.build_cauldron_effects_tag(sample)
        print(f"  Wejście (1.7.10): {sample['effects']}")
        print(f"  Wyjście (1.18.2 tag[\"effects\"]): {result}")
        if warnings:
            print(f"  OSTRZEŻENIA: {warnings}")


if __name__ == "__main__":
    run_demo()
