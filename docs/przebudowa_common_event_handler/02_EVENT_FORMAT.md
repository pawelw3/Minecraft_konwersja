# 02. Specyfikacja formatu Event JSON

## Struktura pliku Event JSON

```json
{
  "version": "2.0",
  "metadata": {
    "converter": "betterstorage",
    "source_world": "maps/1.7.10/world",
    "target_world": "maps/1.18.2/world",
    "timestamp": "2026-02-03T12:00:00Z",
    "stats": {
      "total_events": 1500,
      "blocks": 1200,
      "block_entities": 280,
      "entities": 20,
      "warnings": 5
    }
  },
  "events": [
    // Lista eventów - patrz poniżej
  ],
  "warnings": [
    {
      "code": "W001",
      "message": "Item overflow: 5 items couldn't fit in chest",
      "pos": [100, 64, 200],
      "details": {"overflow_count": 5}
    }
  ]
}
```

## Typy eventów

### 1. SET_BLOCK - Ustawienie bloku (bez BlockEntity)

```json
{
  "op": "set_block",
  "pos": [100, 64, 200],
  "block": "minecraft:stone",
  "blockstate": {
    "variant": "granite"
  },
  "source": {
    "mod": "betterstorage",
    "block_id": "betterstorage:reinforcedChest",
    "metadata": 3
  }
}
```

**Pola:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `op` | string | tak | Zawsze `"set_block"` |
| `pos` | [int, int, int] | tak | Pozycja [x, y, z] |
| `block` | string | tak | ID bloku 1.18.2 (np. `"minecraft:chest"`) |
| `blockstate` | object | nie | Właściwości blockstate (np. `{"facing": "north"}`) |
| `source` | object | nie | Informacje o źródle (do debugowania) |

### 2. SET_BLOCK_ENTITY - Ustawienie bloku z BlockEntity

```json
{
  "op": "set_block_entity",
  "pos": [100, 64, 200],
  "block": "minecraft:chest",
  "blockstate": {
    "facing": "north",
    "type": "single"
  },
  "nbt": {
    "id": "minecraft:chest",
    "Items": [
      {
        "Slot": 0,
        "id": "minecraft:diamond",
        "Count": 64
      },
      {
        "Slot": 1,
        "id": "minecraft:iron_ingot",
        "Count": 32,
        "tag": {
          "display": {"Name": "{\"text\":\"Special Iron\"}"}
        }
      }
    ],
    "Lock": ""
  },
  "source": {
    "mod": "betterstorage",
    "block_id": "betterstorage:reinforcedChest",
    "te_id": "container.reinforcedChest",
    "metadata": 3
  }
}
```

**Pola NBT:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `id` | string | tak | ID BlockEntity (np. `"minecraft:chest"`) |
| `Items` | list | zależy | Lista itemów (dla kontenerów) |
| `Lock` | string | nie | Zamek kontenera |
| ... | ... | ... | Inne pola specyficzne dla typu BE |

### 3. REMOVE_BLOCK - Usunięcie bloku

```json
{
  "op": "remove_block",
  "pos": [100, 64, 200],
  "source": {
    "mod": "betterstorage",
    "reason": "Block not convertible"
  }
}
```

### 4. SET_ENTITY - Dodanie entity

```json
{
  "op": "set_entity",
  "pos": [100.5, 64.0, 200.5],
  "nbt": {
    "id": "minecraft:item",
    "Item": {
      "id": "minecraft:diamond",
      "Count": 1
    },
    "Motion": [0.0, 0.0, 0.0],
    "Pos": [100.5, 64.0, 200.5],
    "UUID": [I; 123456789, 987654321, 111222333, 444555666]
  },
  "source": {
    "mod": "betterstorage",
    "reason": "Overflow item spawned"
  }
}
```

**Pola:**
| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `pos` | [double, double, double] | tak | Pozycja [x, y, z] (floating point!) |
| `nbt` | object | tak | Pełne NBT entity |
| `nbt.id` | string | tak | ID entity (np. `"minecraft:item"`) |
| `nbt.UUID` | int array | nie | UUID entity (generowane jeśli brak) |

### 5. REMOVE_ENTITY - Usunięcie entity

```json
{
  "op": "remove_entity",
  "uuid": [I; 123456789, 987654321, 111222333, 444555666],
  "source": {
    "mod": "bloodmagic",
    "reason": "Demon replaced with vanilla mob"
  }
}
```

### 6. MODIFY_NBT - Modyfikacja istniejącego NBT

```json
{
  "op": "modify_nbt",
  "pos": [100, 64, 200],
  "target": "block_entity",
  "operations": [
    {"path": "Items[0].Count", "op": "set", "value": 32},
    {"path": "Lock", "op": "set", "value": "secret"},
    {"path": "CustomName", "op": "remove"}
  ],
  "source": {
    "mod": "betterstorage",
    "reason": "Adjust item counts"
  }
}
```

## Typy danych NBT

### Reprezentacja typów w JSON

```json
{
  "byte_value": {"_type": "byte", "value": 127},
  "short_value": {"_type": "short", "value": 32000},
  "int_value": 12345,
  "long_value": {"_type": "long", "value": "9223372036854775807"},
  "float_value": {"_type": "float", "value": 3.14},
  "double_value": 3.14159265359,
  "string_value": "Hello World",
  "byte_array": {"_type": "byte_array", "value": [1, 2, 3, 4]},
  "int_array": [I; 1, 2, 3, 4],
  "long_array": [L; 1, 2, 3, 4],
  "list": [1, 2, 3],
  "compound": {"nested": "value"}
}
```

**Konwencje:**
- `int` - domyślnie jako JSON number
- `double` - domyślnie jako JSON number
- `string` - jako JSON string
- `list` - jako JSON array
- `compound` - jako JSON object
- Pozostałe typy - wymagają `{"_type": "...", "value": ...}`
- Int/Long arrays - notacja `[I; ...]` lub `[L; ...]`

## Blockstate mappings

### Typowe blockstate properties

```json
{
  "facing": "north|south|east|west|up|down",
  "axis": "x|y|z",
  "half": "top|bottom",
  "type": "single|left|right|top|bottom",
  "waterlogged": "true|false",
  "lit": "true|false",
  "powered": "true|false",
  "open": "true|false",
  "level": "0-15",
  "age": "0-7",
  "rotation": "0-15"
}
```

### Przykład konwersji metadata → blockstate

```
Blok 1.7.10: betterstorage:reinforcedChest, metadata=3
  ↓ konwersja
Blok 1.18.2: minecraft:chest
  blockstate: {facing: "north", type: "single", waterlogged: "false"}
```

## Schema walidacji (JSON Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["version", "events"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^2\\.\\d+$"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "converter": {"type": "string"},
        "source_world": {"type": "string"},
        "target_world": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "stats": {
          "type": "object",
          "properties": {
            "total_events": {"type": "integer"},
            "blocks": {"type": "integer"},
            "block_entities": {"type": "integer"},
            "entities": {"type": "integer"},
            "warnings": {"type": "integer"}
          }
        }
      }
    },
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["op"],
        "properties": {
          "op": {
            "type": "string",
            "enum": ["set_block", "set_block_entity", "remove_block",
                     "set_entity", "remove_entity", "modify_nbt"]
          }
        },
        "allOf": [
          {
            "if": {"properties": {"op": {"const": "set_block"}}},
            "then": {
              "required": ["pos", "block"],
              "properties": {
                "pos": {"type": "array", "items": {"type": "integer"}, "minItems": 3, "maxItems": 3},
                "block": {"type": "string"},
                "blockstate": {"type": "object"}
              }
            }
          },
          {
            "if": {"properties": {"op": {"const": "set_block_entity"}}},
            "then": {
              "required": ["pos", "block", "nbt"],
              "properties": {
                "pos": {"type": "array", "items": {"type": "integer"}, "minItems": 3, "maxItems": 3},
                "block": {"type": "string"},
                "blockstate": {"type": "object"},
                "nbt": {"type": "object", "required": ["id"]}
              }
            }
          }
        ]
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
          "code": {"type": "string"},
          "message": {"type": "string"},
          "pos": {"type": "array"},
          "details": {"type": "object"}
        }
      }
    }
  }
}
```

## Przykłady pełnych plików

### events/betterstorage_events.json

```json
{
  "version": "2.0",
  "metadata": {
    "converter": "betterstorage",
    "source_world": "maps/1.7.10/world",
    "target_world": "maps/1.18.2/world",
    "timestamp": "2026-02-03T12:00:00Z",
    "stats": {
      "total_events": 3,
      "blocks": 0,
      "block_entities": 2,
      "entities": 1,
      "warnings": 1
    }
  },
  "events": [
    {
      "op": "set_block_entity",
      "pos": [100, 64, 200],
      "block": "minecraft:chest",
      "blockstate": {"facing": "north", "type": "single", "waterlogged": "false"},
      "nbt": {
        "id": "minecraft:chest",
        "Items": [
          {"Slot": 0, "id": "minecraft:diamond", "Count": 64}
        ],
        "Lock": ""
      },
      "source": {"mod": "betterstorage", "block_id": "betterstorage:reinforcedChest"}
    },
    {
      "op": "set_block_entity",
      "pos": [102, 64, 200],
      "block": "minecraft:barrel",
      "blockstate": {"facing": "up", "open": "false"},
      "nbt": {
        "id": "minecraft:barrel",
        "Items": [
          {"Slot": 0, "id": "minecraft:iron_ingot", "Count": 64},
          {"Slot": 1, "id": "minecraft:gold_ingot", "Count": 32}
        ]
      },
      "source": {"mod": "betterstorage", "block_id": "betterstorage:crate"}
    },
    {
      "op": "set_entity",
      "pos": [100.5, 65.0, 200.5],
      "nbt": {
        "id": "minecraft:item",
        "Item": {"id": "minecraft:diamond", "Count": 10},
        "Motion": [0.0, 0.0, 0.0],
        "Pos": [100.5, 65.0, 200.5]
      },
      "source": {"mod": "betterstorage", "reason": "Overflow from reinforcedChest"}
    }
  ],
  "warnings": [
    {
      "code": "BS-W-001",
      "message": "Item overflow: 10 diamonds couldn't fit in converted chest",
      "pos": [100, 64, 200],
      "details": {"overflow_item": "minecraft:diamond", "overflow_count": 10}
    }
  ]
}
```

## Konwencje nazewnictwa

### Block IDs (1.18.2)
- Format: `namespace:block_name`
- Przykłady: `minecraft:chest`, `minecraft:barrel`, `minecraft:hopper`

### BlockEntity IDs (1.18.2)
- Format: `namespace:block_entity_type`
- Przykłady: `minecraft:chest`, `minecraft:barrel`, `minecraft:hopper`
- Uwaga: często takie same jak block ID

### Entity IDs (1.18.2)
- Format: `namespace:entity_type`
- Przykłady: `minecraft:item`, `minecraft:armor_stand`, `minecraft:villager`

### Warning/Error codes
- Format: `MOD-TYPE-NUMBER`
- Przykłady: `BS-W-001` (BetterStorage Warning 001), `BM-E-002` (BloodMagic Error 002)
