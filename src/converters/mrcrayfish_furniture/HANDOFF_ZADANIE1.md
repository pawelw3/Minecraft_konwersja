# Handoff: MrCrayfish Furniture Mod — Zadanie 1 (Analiza blokow i TE/BE)

## Podsumowanie sesji

Wykonano kompletna analize MrCrayfish Furniture Mod w wersjach 1.7.10 i 1.18.2. Zebrano wszystkie registry names blokow, tile entities (28 w 1.7.10) oraz block entities (13 w 1.18.2). Okazalo sie ze pomimo iz jest to "ten sam mod", wersja 1.18.2 zostala calkowicie przebudowana — wiele "elektrycznych" urzadzen (TV, Computer, Printer, Stereo, Microwave, Oven, WashingMachine, Dishwasher itp.) zostalo usunietych, a w zamian dodano nowe bloki dekoracyjne i funkcjonalne (Crate, Desk, Grill, Cooler, Trampoline, DivingBoard, DoorMat, KitchenCounter/Drawer/Sink, ParkBench, UpgradedFence/Gate, PicketFence/Gate).

## Ukonczono

- [x] Identyfikacja 65+ blokow w 1.7.10 z dokladnymi registry names (np. `cfm:oven`, `cfm:fridge`, `cfm:tv`)
- [x] Identyfikacja 28 Tile Entities w 1.7.10 z dokladnymi registry strings (np. `cfmOven`, `cfmFridge`, `cfmTV` — UWAGA: bez dwukropka!)
- [x] Identyfikacja 300+ blokow w 1.18.2 (wliczajac warianty materialowe i kolorowe) z prefixem `cfm:`
- [x] Identyfikacja 13 Block Entities w 1.18.2 z prefixem `cfm:`
- [x] Szczegolowa analiza NBT dla kazdego TE/BE (inventory, UUID, plyny, kolory)
- [x] Porownanie 1.7.10 vs 1.18.2 z mapowaniem wspolnych funkcjonalnosci
- [x] Wskazanie blokow usunietych w 1.18.2 wymagajacych decyzji co do konwersji
- [x] Wskazanie 8 kluczowych decyzji do podjecia przez wlasciciela projektu

## Nowe pliki

- `src/converters/mrcrayfish_furniture/ANALIZA_BLOKOW_TE_ZADANIE1.md` — pelny raport analizy (619 linii, ~29 KB)
- `src/converters/mrcrayfish_furniture/gen_report.py` — skrypt pomocniczy generujacy raport (opcjonalny)

## Zmodyfikowane pliki

- Brak (nowy folder `mrcrayfish_furniture`)

## Kluczowe wnioski dla kolejnych zadan

### Bloki z bezposrednim mapowaniem (latwe)
| 1.7.10 | 1.18.2 | Uwaga |
|--------|--------|-------|
| tablewood | oak_table | Domyslnie oak, brak metadanych drewna w 1.7.10 |
| chairwood | oak_chair | Domyslnie oak |
| coffeetablewood | oak_coffee_table | Domyslnie oak |
| cabinet | oak_cabinet | Domyslnie oak |
| bedsidecabinet | oak_bedside_cabinet | Domyslnie oak |
| mailbox | oak_mail_box | Domyslnie oak |
| fridge + freezer | fridge_light + freezer_light | Wieloblok zachowany |
| couch (kolor) | <color>_sofa | Metadata colour 0-15 -> DyeColor |
| blinds | oak_blinds | Domyslnie oak |
| curtains | oak_curtains | Domyslnie oak |
| hedge | oak_hedge | Domyslnie oak |
| stonepath | rock_path | 1:1 |

### Bloki usuniete w 1.18.2 (wymagaja decyzji)
- **Inventory + funkcjonalnosc**: Oven, Microwave, Computer, Printer, TV, Stereo, WashingMachine, Dishwasher, Blender, Toaster, Plate, Cup, ChoppingBoard, CookieJar, Present, WallCabinet, Bin
- **Woda/lazienka**: Basin, Bath, ShowerBottom/Top, ShowerHead, CounterSink, Tap
- **Inne**: ElectricFence, DoorBell, FireAlarm, CeilingLight, Lamp, BirdBath, Tree, BarStool, CounterDoored, KitchenCabinet
- **Dekoracyjne**: Hey, Nyan, Pattern, YellowGlow, WhiteGlass

### Kluczowe roznice techniczne
1. **Inventory format**: 1.7.10 uzywa custom nazw list (np. `fridgeItems` ze slot tag `fridgeSlot`), 1.18.2 uzywa standardowego `Items` list ze slotami 0- N
2. **UUID**: 1.7.10 = string, 1.18.2 = int-array (MailBox)
3. **Plyny**: 1.7.10 = boolean/poziom, 1.18.2 = FluidTank z pelnym NBT (tylko KitchenSink)
4. **Kolor**: 1.7.10 = int 0-15, 1.18.2 = String/DyeColor
5. **Wielobloki**: Fridge/Freezer zachowane, ale Bath/Shower usuniete

## Decyzje do podjecia (przed Zadaniem 2 / 3)

1. Co zrobic z itemami z usunietych blokow (Oven, Microwave itp.)? — Drop / utrata / mapowanie na Crate?
2. Czy mapowac usuniete bloki dekoracyjne/lazienkowe na placeholdery czy air?
3. Czy mapowac Bin -> Crate (oba maja inventory)?
4. Czy mapowac WallCabinet -> Cabinet?
5. Czy mapowac CounterSink -> KitchenSink?

## Nastepne kroki (zgodnie z PLAN.md)

1. **[Zadanie 2]** Przygotowanie symulacji dzialania funkcjonalnosci (Python) — np. symulacja inventory conversion, symulacja Fridge/Freezer wielobloku
2. **[Zadanie 3]** Napisanie kodu konwersji blokow i TE/BE z eventami kompatybilnymi z ogolnym handlerem
3. **[Zadanie 4]** Sprawdzenie pokrycia na strefach glownej mapy
4. **[Zadanie 5A]** Budowa testowej mapy 1.7.10 z wszystkimi blokami i konwersja
5. **[Zadanie 5B + 6]** Testy na headless serwerze

---

*Data handoffu: 2026-05-19*
*Mod: MrCrayfish Furniture Mod (v3.4.8 -> 7.0.x)*
*Status: Zadanie 1 UKONCZONE, oczekuje na decyzje przed Zadaniem 2*
