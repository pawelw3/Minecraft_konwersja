# Changelog - Digital Counter Vanilla

## Wersja 2.0 - Dropper Ring Counter z Validator/Simulator (2026-01-30)

### Zmiana architektury

**Z:**
- Zegar 1Hz → Licznik 4-bit → Dekoder BCD → Command Blocks
- Problemy: brak resetu mod-10, skomplikowany dekoder, trudny w debugowaniu

**Na:**
- Zegar 1Hz → Dropper Ring Counter (10 stanów) → Komparatory → Command Blocks
- Zalety: naturalna pętla 0-9, prostsza konstrukcja, łatwiejszy w debugowaniu

### Zmiany w plikach

#### `circuit_design.json`
- ✅ Usunięto: `counter_4bit`, `bcd_decoder`
- ✅ Dodano: `ring_counter_10` z definicją 10 dropperów i komparatorów
- ✅ Zaktualizowano połączenia (teraz prostsze: clock → ring → outputs)
- ✅ Zaktualizowano truth_table (one-hot: state 0-9)
- ✅ Dodano sekcję `semantics` opisującą znaczenie properties
- ✅ Dodano sekcję `timing` z dokładnymi czasami (game ticks)
- ✅ Dodano sekcję `blocks_availability` (potwierdzenie dla 1.7.10)

#### `voxel_grid.json`
- ✅ Usunięto sekcje: `counter_bit0`, `counter_bit1`, `counter_bit2`, `counter_bit3`, `bcd_decoder`
- ✅ Usunięto wszystkie stringi z tablic `voxels` (przeniesiono do description)
- ✅ Dodano sekcję `semantics` opisującą format properties
- ✅ Dodano sekcję `ring_counter_10` z:
  - 10 dropperami (y=1) z podparciem (y=0)
  - 10 komparatorami (y=1) z podparciem (y=0)
  - 10 command blockami (y=1) z podparciem (y=0)
  - Magistralą zasilania dropperów (y=3) z podparciem (y=2)
- ✅ Zaktualizowano `clock_generator` (nowy: torch inverter + repeater loop)
- ✅ Zaktualizowano `signal_routing` (prostsze połączenia)
- ✅ Dodano `checklist` (8 punktów weryfikacji)
- ✅ Dodano `blocks_availability` (potwierdzenie bloków dla 1.7.10)
- ✅ Poprawiono notki o wersji (usunięto odniesienia do 1.18.2)

#### `debug_redstone.py` - KOMPLETNA REWRITE
- ✅ Zmieniono z "scenario runner" na WALIDATOR zgodny z redstone
- ✅ Zaimplementowano model świata z geometrii (Position, Block, RedstoneWorld)
- ✅ Zaimplementowano propagację mocy 0-15 (weak/strong power)
- ✅ Zaimplementowano scheduled tick queue dla repeater/comparator/torch/dropper
- ✅ Dodano walidator budowalności sprawdzający:
  - Czy redstone ma podparcie (stone pod spodem)
  - Czy torch/lever ma poprawne attachment
  - Czy droppery wskazują na następny w pętli
  - Czy komparatory czytają droppery
  - Czy command blocki są podłączone do komparatorów
- ✅ Symulacja oparta na geometrii (nie na "purpose")
- ✅ Zaimplementowano ring counter z dropperów z przenoszeniem itemu
- ✅ Zaimplementowano zegar torch+repeater z realnymi opóźnieniami
- ✅ Zaimplementowano komparatory czytające zawartość dropperów

### Weryfikacja dostępności bloków w 1.7.10

| Blok | Wersja dodania | Dostępny w 1.7.10 |
|------|---------------|-------------------|
| `minecraft:stone` | Od początku | ✅ Tak |
| `minecraft:redstone_wire` | Od classic | ✅ Tak |
| `minecraft:redstone_torch` | Od classic | ✅ Tak |
| `minecraft:repeater` | Beta 1.3 | ✅ Tak |
| `minecraft:comparator` | 1.5 (13w01a) | ✅ Tak |
| `minecraft:dropper` | 1.5.2 (13w03a) | ✅ Tak |
| `minecraft:command_block` | 1.4 | ✅ Tak |
| `minecraft:lever` | Od classic | ✅ Tak |

**Wszystkie bloki potwierdzone dostępne w 1.7.10!**

### Checklist "perfekcyjności" - Status

1. ✅ **Brak kolizji współrzędnych** - sprawdzone, każdy voxel ma unikalne (x,y,z)
2. ✅ **Podparcie redstone** - wszystkie komponenty redstone mają stone pod spodem
3. ✅ **Facing dropperów** - każdy dropper wskazuje na następny w pętli
4. ✅ **Facing komparatorów** - każdy komparator czyta droppera (tył do droppera)
5. ✅ **Command blocki** - stoją na wyjściach komparatorów
6. ✅ **Bus zasilania** - spójna sieć na y=3 łącząca wszystkie droppery
7. ✅ **Zegar** - torch inverter + repeater loop (~20 ticków okres)
8. ✅ **Stan startowy** - dokumentacja wskazuje: 1 cobblestone w D0

### Zasady redstone zaimplementowane w debuggerze

- **Game tick**: 0.05s (20 TPS)
- **Redstone tick**: 2 game ticks
- **Repeater delay**: 1-4 redstone ticks (konfigurowalne)
- **Dropper**: aktywacja na rising edge (OFF→ON), opóźnienie 4 game ticks
- **Comparator**: czyta zawartość kontenera, daje sygnał 0-15
- **Scheduled ticks**: kolejka zdarzeń dla bloków (repeater, dropper, comparator)

### Testy

- ✅ Walidator wykrywa błędy budowalności (brak podparcia)
- ✅ Symulator generuje poprawną sekwencję 0-9
- ✅ Zapętlenie działa (po 9 wraca do 0)
- ✅ Pełny cykl trwa ~10 sekund

### Co zostało do zrobienia

- [ ] Budowa fizyczna w Minecraft 1.7.10
- [ ] Test na headless server
- [ ] Ewentualne drobne poprawki po testach w grze

---

**Autor zmian**: Agent AI  
**Data**: 2026-01-30  
**Wersja**: 2.0 (Dropper Ring Counter z Validator/Simulator)
