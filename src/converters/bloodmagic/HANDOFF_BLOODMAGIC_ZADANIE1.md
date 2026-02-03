# Handoff: Blood Magic - Zadanie 1 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 1** konwersji moda Blood Magic z wersji 1.7.10 na 1.18.2.  
Zadanie polegało na wypisaniu wszystkich bloków i Tile/Block Entities dodawanych przez mod oraz opisaniu ich funkcjonalności.

Blood Magic to mod o tematyce magii krwi, oparty na systemie Life Essence (LP) i Soul Network. Główne mechaniki to transmutacja itemów w Blood Altar oraz rytuały oparte na strukturach run.

## Ukończono

- [x] Analiza dokumentacji Blood Magic 1.7.10 (wersja 1.3.3-17)
- [x] Analiza dokumentacji Blood Magic 1.18.2 (wersja 3.2.6)
- [x] Zebranie informacji o blokach Blood Magic 1.7.10 z FTB Wiki i GitHub
- [x] Zebranie informacji o blokach Blood Magic 1.18.2 z dokumentacji
- [x] Stworzenie pełnej listy bloków z mapowaniem ID 1.7.10 → 1.18.2
- [x] Stworzenie pełnej listy Tile/Block Entities
- [x] Opis funkcjonalności każdego kluczowego bloku
- [x] Dokumentacja różnic w strukturze NBT
- [x] Identyfikacja NOWOŚCI w 1.18.2 (Alchemy Table, Incense Altar, Demon Will system)
- [x] Identyfikacja elementów USUNIĘTYCH w 1.18.2 (Soul Forge, Demon Portal)
- [x] Określenie priorytetów konwersji

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/bloodmagic/BLOOD_MAGIC_BLOCKS_AND_TE.md` | Główna dokumentacja zawierająca: <br>- Pełną listę bloków i Tile/Block Entities <br>- Mapowanie ID 1.7.10 → 1.18.2 <br>- Szczegółowy opis funkcjonalności <br>- Struktury NBT dla obu wersji <br>- Porównanie zmian między wersjami <br>- Priorytety konwersji <br>- Listę rytuałów |

## Kluczowe wnioski dla kolejnych zadań

### 🔴 Krytyczne elementy wymagające szczególnej uwagi:

1. **Blood Altar** - zawartość LP (currentEssence) i tier muszą być zachowane
2. **Master Ritual Stone** - aktywne rytuały (ritualType) i właściciel (owner UUID)
3. **Blood Runes** - typy run w strukturze ołtarza (metadata 0-7 → blockstates)
4. **Soul Network** - binding orbów do graczy (przechowywane w NBT gracza, nie blokach)

### 🆕 NOWOŚCI w 1.18.2 wymagające obsługi:

| Nowość | ID 1.18.2 | Strategia konwersji |
|--------|-----------|---------------------|
| Alchemy Table | `bloodmagic:alchemy_table` | Brak odpowiednika w 1.7.10 - ignorować przy konwersji bloków |
| Incense Altar | `bloodmagic:incense_altar` | Brak odpowiednika - ignorować |
| Demon Crucible/Crystallizer | `bloodmagic:demon_*` | Nowy system Demon Will - nie dotyczy konwersji |
| Routing Nodes | `bloodmagic:*_routing_node` | Nowy system transportu - nie dotyczy konwersji |

### ❌ Elementy usunięte w 1.18.2:

| Element 1.7.10 | Status | Strategia |
|----------------|--------|-----------|
| Soul Forge | Usunięty | Mapować na Alchemy Table lub placeholder |
| Demon Portal | Usunięty | Zamienić na bloki dekoracyjne |

### 📊 Statystyki:

- **Bloki z Tile Entity**: ~10 w 1.7.10, ~15 w 1.18.2
- **Rytuały**: ~30 rytuałów w obu wersjach (zgodność struktur)
- **Typy Blood Runes**: 8 typów (identyczne w obu wersjach)
- **Bezpośrednie mapowanie**: ~80% bloków
- **Wymagające specjalnej logiki**: Blood Runes (metadata → blockstates)

## Następne kroki (Zadanie 2)

Zgodnie z planem konwersji (docs/PLAN.md), kolejne zadanie to:

**Zadanie 2: Przygotowanie symulacji działania funkcjonalności Blood Magic**

Symulacje do przygotowania:
1. Symulacja Blood Altar (transmutacja, zużycie LP, postęp craftingu)
2. Symulacja Soul Network (binding orbów, transfer LP, zużycie przez rytuały)
3. Symulacja Master Ritual Stone (aktywacja rytuału, zużycie LP, efekty)
4. Symulacja tierów ołtarza (obliczanie na podstawie struktury run)
5. Symulacja rytuału Well of Suffering (obrażenia mobów → LP)

Każda symulacja ma być w czystym Pythonie (bez mapy), bazując na kodzie źródłowym obu wersji moda.

## Zalecenia przed Zadaniem 2

1. Zapoznać się ze szczegółami kodu Tile Entities:
   - Struktura NBT Blood Altar w obu wersjach
   - Mechanika obliczania tieru ołtarza
   - System aktywacji rytuałów

2. Sprawdzić strukturę Soul Network w NBT gracza (playerdata)

3. Zrozumieć system rytuałów i ich wzory strukturalne

4. Przeanalizować konwersję metadata run (1.7.10) na blockstates (1.18.2)

---

**Status:** ✅ Zadanie 1 ukończone - gotowe do przeglądu i akceptacji  
**Data:** 2026-02-03  
**Agent:** AI Konwersji Blood Magic
