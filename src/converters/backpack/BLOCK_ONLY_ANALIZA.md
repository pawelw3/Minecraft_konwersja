# Backpack (Eydamos) - Block-Only Analiza (Krok 1)

> **Mod:** Backpack 2.0.1 (Eydamos) 1.7.10 → Sophisticated Backpacks 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

Mod Backpack (Eydamos) **nie dodaje żadnych bloków** do świata Minecraft. Jest wyłącznie modem itemów i danym pozachunkowych.

Źródło: `BACKPACK_ELEMENTS_AND_DATA.md` (Zadanie 1) – dekompilacja JAR potwierdza brak klas `Block*` w pakiecie moda.

---

## 2. Bloki bez TileEntity

**Brak.**

| # | Registry name | Klasa | Opis |
|---|--------------|-------|------|
| — | — | — | — |

---

## 3. Elementy moda (dla referencji)

| Typ | Element | Konwersja |
|-----|---------|-----------|
| Item | `Backpack:backpack` | `sophisticatedbackpacks:backpack` itp. |
| Item | `Backpack:workbenchbackpack` | SB + crafting upgrade |
| Item | `Backpack:boundLeather`, `tannedLeather` | — (materiały craftingowe) |
| Dane | `backpacks/backpacks/<UUID>.dat` | `data/sophisticatedbackpacks.dat` |
| Dane | `backpacks/player/<UUID>.dat` | `playerdata/<UUID>.dat` / Curios |

---

## 4. Decyzja

**Warstwa block-only NIE JEST POTRZEBNA** dla moda Backpack.

Konwersja odbywa się wyłącznie przez:
- Transformację itemów w inventory graczy i skrzyniach
- Migrację plików `.dat` z folderu `backpacks/`

---

## 5. Handoff

- [ ] Brak bloków do mapowania w warstwie block-only.
- [ ] Konwersja tego moda to wyłącznie item + saved data migration.
