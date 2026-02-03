# Handoff: Blood Magic - Zadanie 2 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 2** konwersji moda Blood Magic - przygotowano 5 symulacji funkcjonalności w czystym Pythonie, bazujących na dokładnej analizie kodu źródłowego obu wersji moda (1.7.10 i 1.18.2).

Symulacje odwzorowują kluczowe mechaniki Blood Magic i pozwalają na testowanie konwersji NBT oraz logiki moda bez potrzeby uruchamiania gry.

---

## Ukończono

- [x] Analiza kodu źródłowego TEAltar.java (1.7.10) i BloodAltar.java (1.18.2)
- [x] Analiza kodu źródłowego SoulNetworkHandler.java (1.7.10) i SoulNetwork.java (1.18.2)
- [x] Analiza kodu źródłowego RitualEffectWellOfSuffering.java
- [x] Analiza kodu źródłowego UpgradedAltars.java i struktur tierów
- [x] Symulacja Blood Altar (transmutacja, zużycie LP, postęp craftingu)
- [x] Symulacja Soul Network (binding orbów, transfer LP)
- [x] Symulacja Master Ritual Stone (aktywacja rytuału, zużycie LP)
- [x] Symulacja tierów ołtarza (obliczanie na podstawie struktury run)
- [x] Symulacja rytuału Well of Suffering (obrażenia mobów → LP)
- [x] Dokumentacja Source Mapping dla każdej symulacji
- [x] Funkcje testujące dla wszystkich symulacji

---

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/bloodmagic/simulations/__init__.py` | Inicjalizacja pakietu symulacji |
| `src/converters/bloodmagic/simulations/blood_altar_sim.py` | Symulacja Blood Altar - transmutacja, zużycie LP, NBT |
| `src/converters/bloodmagic/simulations/soul_network_sim.py` | Symulacja Soul Network - binding, transfer LP, Blood Orbs |
| `src/converters/bloodmagic/simulations/ritual_stone_sim.py` | Symulacja Master Ritual Stone - aktywacja rytuałów |
| `src/converters/bloodmagic/simulations/altar_tier_sim.py` | Kalkulator tierów ołtarza - walidacja struktury run |
| `src/converters/bloodmagic/simulations/well_of_suffering_sim.py` | Symulacja Well of Suffering - obrażenia mobów → LP |

---

## Szczegóły symulacji

### 1. BloodAltarSimulation (`blood_altar_sim.py`)

**Zakres:**
- Symulacja stanu ołtarza (LP, tier, progress craftingu)
- Konwersja NBT między wersjami 1.7.10 i 1.18.2
- Obliczanie multiplikatorów na podstawie run
- Symulacja ticków (zużycie LP, postęp craftingu)

**Source Mapping:**
- 1.7.10: `TEAltar.java` - readFromNBT/writeToNBT (linie 128-246)
- 1.7.10: `TEAltar.java` - updateEntity (linie 444-641)
- 1.18.2: `BloodAltar.java` - readFromNBT/writeToNBT (linie 87-181)
- 1.18.2: `BloodAltar.java` - update/updateAltar (linie 229-444)

**Kluczowe różnice NBT:**
| Pole | 1.7.10 | 1.18.2 |
|------|--------|--------|
| Tier | `upgradeLevel` (int) | `altarTier` (string enum) |
| LP | `currentEssence` | `currentEssence` |
| Nowe | - | `chargingRate`, `totalCharge` (nowa mechanika) |

**Formuły (z kodu źródłowego):**
- `consumptionMultiplier = 0.20 * speed_upgrades`
- `efficiencyMultiplier = 0.85 ^ efficiency_upgrades`
- `sacrificeMultiplier = 0.10 * sacrifice_upgrades`
- `capacityMultiplier = (1 * 1.10^aug_cap + 0.20 * cap)`

---

### 2. SoulNetworkSimulation (`soul_network_sim.py`)

**Zakres:**
- Zarządzanie globalnym zbiornikiem LP gracza
- Konwersja bindingu Blood Orbów
- Symulacja syphon/add (zużycie/dodawanie LP)

**Source Mapping:**
- 1.7.10: `SoulNetworkHandler.java` - getCurrentEssence (linie 231-248)
- 1.7.10: `SoulNetworkHandler.java` - syphonFromNetwork (linie 111-135)
- 1.7.10: `SoulNetworkHandler.java` - getMaximumForOrbTier (linie 79-98)
- 1.18.2: `SoulNetwork.java` - syphon/add metody

**Kluczowe różnice:**
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Klucz | `ownerName` (string) | UUID gracza |
| Storage | `LifeEssenceNetwork` (MapStorage) | `SoulNetwork` (Capability) |
| Orb binding | `ownerName` w NBT | `Binding` (UUID + nazwa) |

**Pojemności Blood Orbów (identyczne):**
| Tier | Pojemność |
|------|-----------|
| Weak | 5,000 LP |
| Apprentice | 25,000 LP |
| Magician | 150,000 LP |
| Master | 1,000,000 LP |
| Archmage | 10,000,000 LP |
| Transcendent (1.7.10) | 30,000,000 LP |

---

### 3. MasterRitualStoneSimulation (`ritual_stone_sim.py`)

**Zakres:**
- Aktywacja rytuałów
- Zużycie LP z Soul Network
- Konwersja ID rytuałów między wersjami

**Source Mapping:**
- 1.7.10: `TEMasterStone.java` - NBT handling
- 1.7.10: `Rituals.java` - rejestracja rytuałów
- 1.18.2: `TileMasterRitualStone.java` - NBT handling

**Mapowanie rytuałów:**
| Nazwa | 1.7.10 ID | 1.18.2 ID | Koszt |
|-------|-----------|-----------|-------|
| Full Spring | `water` | `bloodmagic:water` | 500 |
| Green Grove | `greenGrove` | `bloodmagic:growth` | 1000 |
| Well of Suffering | `suffering` | `bloodmagic:well_of_suffering` | 5000 |
| Feathered Knife | `featheredKnife` | `bloodmagic:feathered_knife` | 2000 |
| Crusher | `crushing` | `bloodmagic:crushing` | 10000 |

---

### 4. AltarTierCalculator (`altar_tier_sim.py`)

**Zakres:**
- Walidacja struktur ołtarzy (Tier 1-6)
- Zliczanie run ulepszeń
- Obliczanie multiplikatorów

**Source Mapping:**
- 1.7.10: `UpgradedAltars.java` - isAltarValid, checkAltarIsValid (linie 30-192)
- 1.7.10: `UpgradedAltars.java` - getUpgrades (linie 194-262)
- 1.7.10: `UpgradedAltars.java` - loadAltars (linie 264-361)
- 1.18.2: `AltarUtil.java` - getTier, getUpgrades

**Struktury ołtarzy:**
- **Tier 2:** 8 run wokół ołtarza (3x3 minus środek)
- **Tier 3:** 7x7 perimeter, 4 pillars z glowstone
- **Tier 4:** 11x11 perimeter, 4 pillars z large bloodstone brick
- **Tier 5:** 17x17 perimeter, 4 beacony na rogach
- **Tier 6:** 23x23 perimeter, 4 crystal na rogach

**Typy run (metadata -> blockstate):**
| Metadata | Nazwa | Efekt |
|----------|-------|-------|
| 0 | Blank | Podstawowa runa |
| 1 | Speed | +20% consumption rate |
| 2 | Efficiency | 0.85^n efficiency |
| 3 | Sacrifice | +10% LP z mobów |
| 4 | Self-Sacrifice | +10% LP z self-damage |
| 5 | Displacement | 1.2^n transfer rate |
| 6 | Capacity | +20% capacity |
| 7 | Orb | +2% orb capacity |
| 8 | Augmented Capacity | 1.10^n capacity |

---

### 5. WellOfSufferingSimulation (`well_of_suffering_sim.py`)

**Zakres:**
- Symulacja obrażeń mobów
- Generowanie LP w ołtarzu
- Obsługa reagentów (1.7.10)

**Source Mapping:**
- 1.7.10: `RitualEffectWellOfSuffering.java` - performEffect (linie 28-109)
- 1.7.10: `RitualEffectWellOfSuffering.java` - getRitualComponentList (linie 118-158)

**Parametry rytuału:**
| Parametr | Wartość |
|----------|---------|
| Czas odświeżania | 25 ticków (1.25s) |
| Zasięg horyzontalny | 10 bloków |
| Zasięg wertykalny | 10 bloków (20 z Potentia) |
| LP za moba | 10 (20 z Tennebrae, 20 z Offensa, 40 z oboma) |
| Obrażenia | 1 (2 z Offensa) |
| Koszt aktywacji | ~5000 LP |

**Reagenty (1.7.10):**
| Reagent | Efekt | Koszt |
|---------|-------|-------|
| Tennebrae | Podwaja LP | 5 |
| Potentia | Podwaja zasięg wertykalny | 10 |
| Offensa | Podwija obrażenia i LP | 3 |

---

## Użycie symulacji

```python
from src.converters.bloodmagic.simulations import (
    BloodAltarSimulation, AltarTier,
    SoulNetworkSimulation,
    MasterRitualStoneSimulation,
    AltarTierCalculator,
    WellOfSufferingSimulation
)

# 1. Symulacja Blood Altar
altar = BloodAltarSimulation("1.7.10")
altar.load_from_nbt_1710({
    "currentEssence": 15000,
    "upgradeLevel": 3,
    "isActive": True,
    "progress": 500,
})

# Konwersja do 1.18.2
nbt_1182 = altar.convert_to_1182_nbt(player_uuid)

# 2. Symulacja Soul Network
network = SoulNetworkSimulation("1.7.10")
network.load_from_nbt_1710({"currentEssence": 50000, "maxOrb": 3}, "Player123")

# 3. Walidacja struktury ołtarza
calculator = AltarTierCalculator()
tier = calculator.check_tier(blocks_list)  # AltarTier.THREE
upgrades = calculator.get_upgrades(tier, blocks_list)
multipliers = calculator.calculate_multipliers(upgrades)

# 4. Symulacja rytuału
ritual = WellOfSufferingSimulation("1.7.10")
ritual.set_altar_position(0, -5, 0)
ritual.add_mob(MobEntity("zombie", 3.0, 0.0, 4.0, 20.0, 20.0))
result = ritual.simulate_tick(0, 50000)
```

---

## Kluczowe wnioski dla konwersji

### 🔴 Krytyczne dla konwersji:

1. **Blood Altar:**
   - `upgradeLevel` (int) → `altarTier` (string enum: "ONE", "TWO", ...)
   - Wszystkie multiplikatory przenoszone bez zmian
   - Nowe pola w 1.18.2 (charging) ustawiane na 0

2. **Soul Network:**
   - Konwersja nazwy gracza → UUID wymaga mapowania z playerdata
   - Blood Orbs: `ownerName` → `binding` z UUID

3. **Rytuały:**
   - ID rytuałów: `"water"` → `"bloodmagic:water"`
   - Struktury rytualne identyczne
   - Reagenty (1.7.10) → Demon Will (1.18.2) - brak bezpośredniej konwersji

4. **Tier ołtarza:**
   - Struktury identyczne
   - Runy: metadata (0-8) → blockstate (string)

---

## Następne kroki (Zadanie 3)

Zgodnie z planem konwersji (docs/PLAN.md), kolejne zadanie to:

**Zadanie 3: Napisanie kodu konwersji**

Plany do wykonania:
1. Implementacja konwertera NBT Blood Altar
2. Implementacja konwertera Soul Network
3. Implementacja konwertera Master Ritual Stone
4. Mapowanie ID bloków (AWWayofTime:* → bloodmagic:*)
5. Obsługa Blood Orb binding
6. Testy jednostkowe dla konwerterów

---

**Status:** ✅ Zadanie 2 ukończone - gotowe do przeglądu i akceptacji  
**Data:** 2026-02-03  
**Agent:** AI Konwersji Blood Magic
