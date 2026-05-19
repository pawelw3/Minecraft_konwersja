# Handoff: MrCrayfish Furniture Mod — Zadanie 4 (Pokrycie mapy + weryfikacja 1.18.2)

## Podsumowanie sesji

Przeskanowano wszystkie 5 stref glownej mapy 1.7.10 oraz dodatkowe losowe regiony pod katem blokow MrCrayfish Furniture Mod. Znaleziono 2834 bloki/TE CFM w 337 chunkach. Wszystkie znalezione TE ID sa obslugiwane przez konwerter (brak nieznanych). Zweryfikowano zgodnosc symulacji i konwertera z kodem zrodlowym moda 1.18.2 — wykryto i poprawiono jedna niezgodnosc w formacie NBT FluidTank.

## Ukonczono

- [x] Przeskanowanie 5 stref: billund, choroszcz, iii_rzesza, rzym, zsrr (7777 chunkow)
- [x] Przeskanowanie dodatkowych regionow: r.0.0, r.1.1, r.-1.-1, r.10.10, r.-10.-10
- [x] Znaleziono 2834 bloki/TE CFM w 337 chunkach
- [x] Wygenerowano raporty: `output/mrcrayfish_task4/mrcrayfish_coverage.json` i `.md`
- [x] Weryfikacja zgodnosci z kodem zrodlowym 1.18.2 (repo /tmp/cfm-118)
- [x] Poprawka formatu NBT FluidTank (usunieto wrapper `Tank`, Forge zapisuje bezposrednio `FluidName` + `Amount` w root compound)

## Wyniki per strefa

| Strefa | Chunki | Z CFM | Bloki CFM | Najczestsze bloki |
|--------|--------|-------|-----------|-------------------|
| billund | 378 | 33 | 454 | kitchencabinet(164), bedsidecabinet(52), printer(38) |
| choroszcz | 121 | 0 | 0 | — |
| iii_rzesza | 1122 | 6 | 15 | bedsidecabinet(5), washingmachine(1) |
| rzym | 2205 | 103 | 594 | bedsidecabinet(162), computer(67), kitchencabinet(65) |
| zsrr | 3850 | 94 | 1267 | kitchencabinet(452), bedsidecabinet(155), printer(127) |
| random | 101 | 101 | 504 | bedsidecabinet(174), computer(63), kitchencabinet(47) |

## Pokrycie konwersji (top 10)

| Blok 1.7.10 | Liczba | Event | Blok 1.18.2 |
|-------------|--------|-------|-------------|
| kitchencabinet | 681 | remap | white_kitchen_drawer |
| bedsidecabinet | 374 | remap | oak_bedside_cabinet |
| printer | 179 | remove | air |
| fridge | 153 | remap | fridge_light |
| freezer | 153 | remap | freezer_light |
| countersink | 139 | remap | kitchen_sink |
| cabinet | 125 | remap | oak_cabinet |
| washingmachine | 102 | remove | air |
| oven | 95 | remove | air |
| computer | 75 | remove | air |

## Weryfikacja zgodnosci z kodem 1.18.2

### ✅ Zweryfikowane i poprawne

| Element | Kod 1.18.2 | Symulacja / Konwerter | Status |
|---------|------------|----------------------|--------|
| Inventory format | `ContainerHelper.saveAllItems(tag, items)` w `BasicLootBlockEntity` | `Items` list ze `Slot` | ✅ |
| Cabinet size | `getContainerSize() = 18` | 18 slotow | ✅ |
| Fridge size | `getContainerSize() = 27` | 27 slotow | ✅ |
| Freezer slots | `SLOTS_SOURCE[0], SLOTS_FUEL[1], SLOTS_RESULT[2]` | 3 sloty | ✅ |
| MailBox UUID | `compound.putUUID("OwnerUUID", ...)` | int-array | ✅ |
| KitchenSink capacity | `FluidAttributes.BUCKET_VOLUME * 10` = 10000 mB | 10000 mB | ✅ |
| SofaBlock | Brak BE w `ModBlockEntities`, osobne bloki per color | `cfm:<color>_sofa` | ✅ |
| Registry names | `ModBlocks.java` — wszystkie target names istnieja | — | ✅ |

### 🔧 Poprawka po weryfikacji

**FluidTank NBT format:**
- PRZED: `{"Tank": {"FluidName": "...", "Amount": N}}`
- PO: `{"FluidName": "...", "Amount": N}` (bez wrappera)
- Uzasadnienie: `FluidHandlerSyncedBlockEntity.saveAdditional()` wywoluje `this.tank.writeToNBT(tag)` bezposrednio na root compound, bez wrappera.
- Pliki poprawione: `mrcrayfish_converter.py`, `simulation_kitchen_fluid.py`

## Pliki wygenerowane / zmodyfikowane

### Nowe
- `output/mrcrayfish_task4/mrcrayfish_coverage.json` — surowe dane analizy
- `output/mrcrayfish_task4/mrcrayfish_coverage.md` — czytelny raport

### Zmodyfikowane
- `src/converters/mrcrayfish_furniture/mrcrayfish_converter.py` — poprawka formatu FluidTank NBT
- `src/converters/mrcrayfish_furniture/simulation_kitchen_fluid.py` — poprawka formatu FluidTank NBT + test

## Ograniczenia i decyzje

1. **Chunk parser szuka tylko po Tile Entity ID** — bloki CFM bez TE (np. tablewood, chairwood, coffeetablewood, hedge, stonepath, blinds, curtains) nie sa wykrywane bez parsowania sekcji blokow. W praktyce wiekszosc funkcjonalnych blokow CFM ma TE (inventory, kolor, plyny), wiec pokrycie jest wystarczajace do oceny.
2. **Choroszcz ma 0 blokow CFM** — strefa nie zawiera mebli CFM (lub sa one w chunkach bez TE).
3. **Metadata bloku** — w 1.7.10 metadata (np. kolor couch) nie jest przechowywana w TE. W pelnej konwersji wymagane byloby parsowanie sekcji chunka (Blocks/Data arrays). Dla couch z TE `Colour` mamy fallback, ale dla blokow bez TE metadata jest domyslna (0).

## Nastepne kroki (Zadanie 5A)

Wykonanie testowej mapy 1.7.10 ze wszystkimi blokami i BE danego moda, a nastepnie konwersja tej mapy.

---

*Data handoffu: 2026-05-19*
*Mod: MrCrayfish Furniture Mod (v3.4.8 -> 7.0.x)*
*Status: Zadanie 4 UKONCZONE, gotowe do Zadania 5A*
