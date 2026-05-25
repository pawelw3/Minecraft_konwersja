# EnderStorage - Inwentarz bloków i TE

## Wersja 1.7.10

### Bloki
| Blok | ID | Metadata | TE ID | Opis |
|------|-----|----------|-------|------|
| Ender Chest | `EnderStorage:enderChest` | 0 | `Ender Chest` | Wspólna skrzynia ender z kolorowym kodem |
| Ender Tank | `EnderStorage:enderChest` | 1 | `Ender Tank` | Wspólny zbiornik płynów z kolorowym kodem |

### Tile Entities
| TE ID | Klasa | Opis |
|-------|-------|------|
| `Ender Chest` | `TileEnderChest` | Skrzynia z `freq` (int, kolor) i `owner` (string) |
| `Ender Tank` | `TileEnderTank` | Zbiornik z `freq` (int, kolor) i `owner` (string) |

### NBT (1.7.10)
```java
// TileFrequencyOwner (bazowa klasa)
{
  "id": "Ender Chest" | "Ender Tank",
  "x": int, "y": int, "z": int,
  "freq": int,  // 0-4095, kod koloru (3 kolory: góra, lewo, prawo)
  "owner": string  // "global" lub UUID gracza
}
```

## Wersja 1.18.2

### Bloki
| Blok | ID | BE ID | Opis |
|------|-----|-------|------|
| Ender Chest | `enderstorage:ender_chest` | `enderstorage:ender_chest` | Wspólna skrzynia ender |
| Ender Tank | `enderstorage:ender_tank` | `enderstorage:ender_tank` | Wspólny zbiornik płynów |

### Block Entities
| BE ID | Klasa | Opis |
|-------|-------|------|
| `enderstorage:ender_chest` | `TileEnderChest` | Skrzynia z `Frequency` (CompoundTag) |
| `enderstorage:ender_tank` | `TileEnderTank` | Zbiornik z `Frequency` (CompoundTag) |

### NBT (1.18.2)
```java
// TileFrequencyOwner
{
  "id": "enderstorage:ender_chest" | "enderstorage:ender_tank",
  "x": int, "y": int, "z": int,
  "Frequency": {
    "left": int,
    "middle": int,
    "right": int
  },
  "Owner": string  // "global" lub UUID
}
```

## Konwersja
- Blok `EnderStorage:enderChest` meta 0 → `enderstorage:ender_chest`
- Blok `EnderStorage:enderChest` meta 1 → `enderstorage:ender_tank`
- NBT: `freq` (int) dekoduje się na 3 kolory. W 1.7.10 `freq` to packed int: `freq = left | (middle << 4) | (right << 8)`.
- NBT: `owner` → `Owner` (string)
