# ComputerCraft / CC:Tweaked — Zadanie 2: Symulacje funkcjonalności

> **Zadanie 2:** Przygotowanie symulacji działania funkcjonalności ComputerCraft
> **Wersje:** 1.7.10 (1.75) → 1.18.2 (CC:Tweaked 1.101.x)

---

## Spis symulacji

| # | Plik | Temat | Opis |
|---|------|-------|------|
| 1 | `computer_simulation.py` | Komputer | NBT komputera, rodzina (normal/advanced/command), mapping tagów |
| 2 | `monitor_multiblock_simulation.py` | Monitor multiblock | `dir` → `orientation` + `facing`, indeksy wieloblokowe, blockstate |
| 3 | `turtle_simulation.py` | Żółw | Inventory, fuel, upgrade IDs (legacy numeric → string), colour, overlay |
| 4 | `network_simulation.py` | Sieć (cable/modem) | `peripheralID` → `PeripheralId`, blockstate kabla |

---

## Uruchamianie

```bash
# Pojedyncze symulacje
python -m src.converters.computercraft.simulations.computer_simulation
python -m src.converters.computercraft.simulations.monitor_multiblock_simulation
python -m src.converters.computercraft.simulations.turtle_simulation
python -m src.converters.computercraft.simulations.network_simulation

# Wszystkie testy
python -m unittest src.converters.computercraft.simulations.test_simulations
```

---

## Struktura kodu

Każda symulacja zawiera:
- **Klasy 1.7.10** — odwzorowanie kodu źródłowego wersji 1.7.10
- **Klasy 1.18.2** — odwzorowanie kodu źródłowego wersji 1.18.2
- **Funkcje konwersji** — mapping NBT i blockstate
- **Testy porównawcze** — weryfikacja zgodności zachowania

---

## Kluczowe wnioski dla Zadania 3

1. **Monitory:** `dir` w 1.7.10 musi być rozkodowane na `orientation` + `facing` w 1.18.2:
   - `dir <= 5` → `orientation=north` (horizontal wall)
   - `dir 8-11` → `orientation=down` (ceiling)
   - `dir 14-17` → `orientation=up` (floor)
   - `facing = dir % 6` mapped to Direction

2. **Turtle upgrades:** Legacy numeric IDs wymagają lookup table:
   - `1 → computercraft:wireless_modem_normal`
   - `-1 → computercraft:wireless_modem_advanced`
   - `computercraft:wireless_modem` (string) → `computercraft:wireless_modem_normal`

3. **Computer ID:** Globalny per świat, flat integer space. Można zachować as-is po przekopiowaniu folderów `computer/<id>/` → `computercraft/computer/<id>/` i ustawieniu `ids.json`.

4. **Cable:** `peripheralAccess` z 1.7.10 nie ma bezpośredniego odpowiednika w NBT 1.18.2 (stan jest runtime'owy). `peripheralID` → `PeripheralId`.

5. **NBT naming:** Globalna zmiana camelCase → PascalCase (`computerID` → `ComputerId`, `fuelLevel` → `Fuel`, itp.)
