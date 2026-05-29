# Armourer's Workshop - Block-Only Analiza (Krok 1)

> **Mod:** Armourer's Workshop 1.7.10  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczne

Armourer's Workshop w 1.7.10 to mod całkowicie oparty na TileEntity. **Każdy blok moda przechowuje dane** (skiny, kolory, konfigurację) w TileEntity i nie istnieją w nim zwykłe bloki dekoracyjne bez NBT.

Weryfikacja wykonana przez inspekcję bytecode JAR `Armourers-Workshop-1.7.10-0.48.5.jar`:
- `AbstractModBlockContainer` dziedziczy po `BlockContainer` (TE).
- `AbstractModBlock` dziedziczy po `Block`, ale WSZYSTKIE konkretne bloki z wyjątkiem `BlockGlobalSkinLibrary` dziedziczą po `AbstractModBlockContainer`.
- `BlockGlobalSkinLibrary` dziedziczy po `AbstractModBlock`, ale implementuje `ITileEntityProvider` (więc też tworzy TE).

---

## 2. Bloki bez TileEntity

**Brak.**

| # | Registry name | Klasa | TE? |
|---|--------------|-------|-----|
| — | — | — | — |

---

## 3. Lista bloków z TileEntity (poza zakresem block-only)

| Registry name | Klasa | Opis |
|---------------|-------|------|
| `armourersWorkshop:armourer` | `BlockArmourer` | Stół do tworzenia skinów |
| `armourersWorkshop:skinLibrary` | `BlockSkinLibrary` | Lokalna biblioteka skinów |
| `armourersWorkshop:globalSkinLibrary` | `BlockGlobalSkinLibrary` | Globalna biblioteka (TE przez ITileEntityProvider) |
| `armourersWorkshop:colourable` | `BlockColourable` | Blok do malowania |
| `armourersWorkshop:colourableGlass` | `BlockColourableGlass` | Wariant szklany |
| `armourersWorkshop:colourMixer` | `BlockColourMixer` | Mieszalnik kolorów |
| `armourersWorkshop:doll` | `BlockDoll` | Lalka (mini manekin) |
| `armourersWorkshop:dyeTable` | `BlockDyeTable` | Stół z farbami |
| `armourersWorkshop:skinnable` | `BlockSkinnable` | Blok z nałożonym skinem |
| `armourersWorkshop:hologramProjector` | `BlockHologramProjector` | Projektor hologramów |
| `armourersWorkshop:mannequin` | `BlockMannequin` | Manekin |
| `armourersWorkshop:miniArmourer` | `BlockMiniArmourer` | Mini armourer |
| `armourersWorkshop:outfitMaker` | `BlockOutfitMaker` | Tworzenie outfitów |
| `armourersWorkshop:skinningTable` | `BlockSkinningTable` | Stół do nakładania skinów |

---

## 4. Decyzja

**Warstwa block-only NIE JEST POTRZEBNA** dla Armourer's Workshop.

Cała konwersja tego moda odbywa się przez:
- Konwersję TileEntity (skiny, kolory, NBT)
- Migrację biblioteki skinów (`skin_library_migrator.py`)
- JVM worker do materializowania bloków w 1.18.2

---

## 5. Handoff

- [ ] Brak bloków do mapowania w warstwie block-only.
- [ ] Wszystkie bloki AW wymagają pełnego konwertera TE/NBT.
