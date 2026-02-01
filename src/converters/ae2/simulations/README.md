# Symulacje AE2 - Zadanie 2

> **Zadanie 2:** Przygotowanie symulacji działania funkcjonalności AE2  
> **Wersje:** 1.7.10 (rv3-beta-6) → 1.18.2 (11.7.6)  
> **Data:** 2026-02-01

---

## Spis symulacji

| # | Plik | Temat | Opis |
|---|------|-------|------|
| 1 | `me_network_simulation.py` | ME Network | Symulacja kanałów (channels), topologii sieci, kontrolera |
| 2 | `storage_cell_simulation.py` | Storage Cell | Symulacja komórek pamięci, zapisu/odczytu NBT |
| 3 | `autocrafting_simulation.py` | Autocrafting | Symulacja Crafting CPU, Pattern, Molecular Assembler |
| 4 | `quantum_bridge_simulation.py` | Quantum Bridge | Symulacja połączenia dwóch sieci przez Quantum Ring |
| 5 | `spatial_io_simulation.py` | Spatial IO | Symulacja zapisu/odczytu przestrzeni 3D |

---

## Uruchamianie symulacji

```bash
# Symulacja ME Network
python -m src.converters.ae2.simulations.me_network_simulation

# Symulacja Storage Cell
python -m src.converters.ae2.simulations.storage_cell_simulation

# Symulacja Autocrafting
python -m src.converters.ae2.simulations.autocrafting_simulation

# Symulacja Quantum Bridge
python -m src.converters.ae2.simulations.quantum_bridge_simulation

# Symulacja Spatial IO
python -m src.converters.ae2.simulations.spatial_io_simulation
```

---

## Struktura kodu

Każda symulacja zawiera:
- **Klasy 1.7.10** - odwzorowanie kodu źródłowego wersji 1.7.10
- **Klasy 1.18.2** - odwzorowanie kodu źródłowego wersji 1.18.2
- **Test porównawczy** - weryfikacja zgodności zachowania
- **Przykład użycia** - demonstracja działania

---

## Uwagi implementacyjne

1. **Cel symulacji:** Zrozumienie logiki działania AE2 przed pisaniem kodu konwersji
2. **Źródło:** Kod źródłowy obu wersji (patrz `mod_src/1710/actual_src/1.7.10/AppliedEnergistics2` i `mod_src/118/actual_src/1.18.2/AppliedEnergistics2`)
3. **Język:** Python 3.10+
4. **Zależności:** Tylko standardowa biblioteka Python (brak zewnętrznych modułów)

---

*Symulacje przygotowane na podstawie analizy kodu źródłowego AE2 rv3-beta-6 (1.7.10) i AE2 11.7.6 (1.18.2)*
