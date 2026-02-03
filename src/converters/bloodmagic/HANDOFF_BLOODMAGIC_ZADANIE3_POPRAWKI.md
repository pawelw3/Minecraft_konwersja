# Handoff: Blood Magic - Zadanie 3 Poprawki (Weryfikacja kodu źródłowego)

## Podsumowanie wykonanych poprawek

Wszystkie poprawki zostały wprowadzone na podstawie **dokładnej analizy kodu źródłowego** Blood Magic 1.18.2 (wersja 3.2.6).

---

## 1) Poprawka: Blood Rune - osobne bloki w 1.18.2

### Problem
W poprzedniej implementacji zakładano, że Blood Runes w 1.18.2 używają blockstate "type" podobnie jak w 1.7.10 metadata. To było błędne.

### Rozwiązanie
W 1.18.2 (Source: `BlockBloodRune.java`, `BloodRuneType.java`) każda runa to **osobny blok**:

```java
// 1.18.2 BloodRuneType.java
public enum BloodRuneType implements StringRepresentable {
    BLANK, SPEED, EFFICIENCY, SACRIFICE, SELF_SACRIFICE,
    DISPLACEMENT, CAPACITY, AUGMENTED_CAPACITY, ORB,
    ACCELERATION, CHARGING;
}
```

### Mapowanie (zweryfikowane w kodzie źródłowym)

**Osobne bloki w 1.7.10 → osobne bloki w 1.18.2:**
| 1.7.10 | 1.18.2 |
|--------|--------|
| `AWWayofTime:speedRune` | `bloodmagic:speed_rune` |
| `AWWayofTime:efficiencyRune` | `bloodmagic:efficiency_rune` |
| `AWWayofTime:runeOfSacrifice` | `bloodmagic:sacrifice_rune` |
| `AWWayofTime:runeOfSelfSacrifice` | `bloodmagic:self_sacrifice_rune` |

**BloodRune z metadanymi (1.7.10) → osobne bloki (1.18.2):**
| Metadata | 1.18.2 |
|----------|--------|
| 0 | `bloodmagic:blank_rune` |
| 1 | `bloodmagic:dislocation_rune` |
| 2 | `bloodmagic:capacity_rune` |
| 3 | `bloodmagic:better_capacity_rune` |
| 4 | `bloodmagic:orb_rune` |
| 5 | `bloodmagic:acceleration_rune` |

### Pliki zmienione
- `src/converters/bloodmagic/block_mappings.py` - nowa struktura mapowania

---

## 2) Poprawka: Master Ritual Stone - klucze NBT

### Problem
W poprzedniej implementacji używano niepoprawnych kluczy NBT (np. `ritualID`, `active`, `ownerUUID`, `willDrain`).

### Rozwiązanie
Zweryfikowano w kodzie źródłowym 1.18.2 (`TileMasterRitualStone.java`, `Constants.NBT`):

```java
// Source: TileMasterRitualStone.java serialize()
tag.putUUID("owner", owner);
tag.putString(Constants.NBT.CURRENT_RITUAL, ritualId);
tag.putBoolean(Constants.NBT.IS_RUNNING, isActive());
tag.putInt(Constants.NBT.RUNTIME, getActiveTime());
tag.putInt(Constants.NBT.DIRECTION, direction.get3DDataValue());
tag.putBoolean(Constants.NBT.IS_REDSTONED, redstoned);
```

### Mapowanie kluczy NBT
| 1.7.10 | 1.18.2 | Uwagi |
|--------|--------|-------|
| `ritualType` | `currentRitual` | ResourceLocation jako string |
| `isActive` | `isRunning` | boolean |
| `runningTime` | `runtime` | int |
| `owner` (nazwa) | `owner` (UUID) | Konwersja nazwa → UUID |
| - | `direction` | int 0-5 (nowe pole) |
| - | `isStoned` | boolean (redstone state) |
| `cooldown` | - | Nie jest zapisywany w NBT 1.18.2 |

### Pliki zmienione
- `src/converters/bloodmagic/ritual_converter.py`

---

## 3) Poprawka: Blood Altar - klucze NBT

### Problem
W poprzedniej implementacji używano niepoprawnych kluczy (np. `altarTier`, `altarActive`, `altarLiquidReq`).

### Rozwiązanie
Zweryfikowano w kodzie źródłowym 1.18.2 (`BloodAltar.java`, `Constants.NBT`):

```java
// Source: BloodAltar.java writeToNBT()
tagCompound.putString(Constants.NBT.ALTAR_TIER, altarTier.name()); // "upgradeLevel"
tagCompound.putBoolean(Constants.NBT.ALTAR_ACTIVE, isActive);      // "isActive"
tagCompound.putInt(Constants.NBT.ALTAR_LIQUID_REQ, liquidRequired); // "liquidRequired"
tagCompound.putBoolean(Constants.NBT.ALTAR_FILLABLE, canBeFilled);  // "fillable"
```

### Struktura NBT (zweryfikowana)
Dane są zagnieżdżone w tagu `bloodAltar`:
```nbt
{
  "id": "bloodmagic:altar",
  "x": int, "y": int, "z": int,
  "bloodAltar": {
    "upgradeLevel": "ONE",      // string enum (nie int!)
    "isActive": boolean,
    "liquidRequired": int,
    "fillable": boolean,
    "progress": int,
    // ... multiplikatory
  }
}
```

### Pliki zmienione
- `src/converters/bloodmagic/altar_converter.py`

---

## 4) Poprawka: Dodanie x/y/z do BlockEntity NBT

### Problem
W poprzedniej implementacji nie dodawano pozycji (x, y, z) do NBT BlockEntity.

### Rozwiązanie
Dodano automatyczne dodawanie pozycji podczas konwersji TE:

```python
# W BloodMagicConverter._convert_tile_entity()
if be_nbt and pos:
    be_nbt["x"] = pos[0]
    be_nbt["y"] = pos[1]
    be_nbt["z"] = pos[2]
```

### Pliki zmienione
- `src/converters/bloodmagic/converter.py`

---

## 5) Poprawka: Soul Network - format NBT

### Problem
W poprzedniej implementacji używano niepoprawnych kluczy.

### Rozwiązanie
Zweryfikowano w kodzie źródłowym 1.18.2 (`SoulNetwork.java`):

```java
// Source: SoulNetwork.java serializeNBT()
tagCompound.putString("playerId", getPlayerId().toString());
tagCompound.putInt("currentEssence", getCurrentEssence());
tagCompound.putInt("orbTier", getOrbTier());
```

### Mapowanie kluczy NBT
| 1.7.10 | 1.18.2 | Uwagi |
|--------|--------|-------|
| `currentEssence` | `currentEssence` | Bez zmian |
| `maxOrb` | `orbTier` | Bez zmian |
| `ownerName` | `playerId` | UUID jako string |

**WAŻNE:** Soul Network w 1.18.2 jest przechowywane w `BMWorldSavedData` (per świat), nie w NBT gracza.

### Pliki zmienione
- `src/converters/bloodmagic/soul_network_converter.py`

---

## 6) Poprawka: Blood Orb Binding - format NBT

### Problem
W poprzedniej implementacji używano niepoprawnych kluczy dla bindingu.

### Rozwiązanie
Zweryfikowano w kodzie źródłowym 1.18.2 (`Binding.java`):

```java
// Source: Binding.java serializeNBT()
tag.put("id", NbtUtils.createUUID(uuid));  // UUID
tag.putString("name", name);                // string
```

### Struktura NBT (zweryfikowana)
```nbt
{
  "tag": {
    "binding": {
      "id": UUID,      // W 1.7.10: "ownerName" (string)
      "name": string
    }
  }
}
```

### Pliki zmienione
- `src/converters/bloodmagic/soul_network_converter.py`

---

## Pliki zmienione (podsumowanie)

| Plik | Zmiany |
|------|--------|
| `block_mappings.py` | Nowe mapowanie run (osobne bloki) |
| `altar_converter.py` | Poprawne klucze NBT, zagnieżdżony tag `bloodAltar` |
| `ritual_converter.py` | Poprawne klucze NBT (`currentRitual`, `isRunning`, `runtime`) |
| `soul_network_converter.py` | Poprawne klucze NBT (`playerId`, `id`+`name` w bindingu) |
| `converter.py` | Dodanie x/y/z do BE NBT, obsługa nowego mapowania run |
| `__init__.py` | Eksport nowych funkcji |
| `tests/test_converters.py` | 33 testy weryfikujące poprawne klucze NBT |
| `BLOOD_MAGIC_BLOCKS_AND_TE.md` | Zaktualizowana dokumentacja |

---

## Testy

Wszystkie 33 testy przechodzą:
```
Ran 33 tests in 0.004s
OK
```

Testy weryfikują:
- Poprawne mapowanie bloków (w tym run jako osobne bloki)
- Poprawne klucze NBT dla Blood Altar (zgodnie z `Constants.NBT`)
- Poprawne klucze NBT dla Master Ritual Stone (zgodnie z `Constants.NBT`)
- Poprawne klucze NBT dla Soul Network (zgodnie z `SoulNetwork.serializeNBT()`)
- Poprawne klucze NBT dla Blood Orb Binding (zgodnie z `Binding.serializeNBT()`)
- Obecność x/y/z w BlockEntity NBT

---

## Kluczowe wnioski

1. **Blood Runes** - W 1.18.2 każda runa to osobny blok, nie blockstate. To fundamentalna zmiana względem 1.7.10.

2. **NBT Keys** - Klucze w 1.18.2 są zdefiniowane w `Constants.NBT` i należy ich ściśle przestrzegać:
   - Blood Altar: `upgradeLevel` (string!), `isActive`, `liquidRequired`, `fillable`
   - Master Ritual Stone: `currentRitual`, `isRunning`, `runtime`, `direction`
   - Soul Network: `playerId`, `currentEssence`, `orbTier`
   - Binding: `id` (UUID), `name`

3. **Zagnieżdżone NBT** - Blood Altar przechowuje dane w tagu `bloodAltar`, nie bezpośrednio w root.

4. **Pozycja BE** - BlockEntity wymaga pól `x`, `y`, `z` w NBT.

---

**Status:** ✅ Wszystkie poprawki wprowadzone i zweryfikowane  
**Data:** 2026-02-03  
**Agent:** AI Konwersji Blood Magic
