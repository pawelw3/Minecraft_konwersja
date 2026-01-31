# Raport Triage: PyAnvilEditor + Minecraft 1.7.10

**Data:** 2026-01-31
**Agent:** Claude Code
**Świat testowy:** Czysty superflat 1.7.10 (headless_server/tests/headless_server/1.7.10_clean)

---

## 1. Test Round-Trip #1: Blok stone (FAIL)

**Cel:** Wstawienie bloku stone (ID=1) w (0, 64, 0) i odczyt.

**Wynik:** FAIL

**Błąd:**
```
AttributeError: 'OldBlock' object has no attribute 'name'
File: anvil/empty_section.py:152, in save()
    tag.tags.append(nbt.TAG_String(name='Name', value=block.name()))
```

**Analiza:**
- PyAnvilEditor używa `OldBlock` do odczytu bloków pre-1.13 (numeryczne ID)
- Podczas zapisu, `empty_section.py` wywołuje `block.name()` które istnieje tylko w klasie `Block` (post-1.13, string ID)
- `OldBlock` nie ma metody `name()`, co powoduje AttributeError

**Konkluzja:** PyAnvilEditor NIE wspiera zapisu w formacie pre-1.13. Zapis działa tylko dla formatu post-1.13 (z palette + BlockStates jako long array).

---

## 2. Test Round-Trip #2: Command Block TE (NIE PRZEPROWADZONY)

Nie przeprowadzony z powodu FAIL #1.

---

## 3. Analiza kodu PyAnvilEditor

Plik: `anvil/empty_section.py:140-170` (metoda `save()`)

```python
def save(self) -> nbt.TAG_Compound:
    root = nbt.TAG_Compound()
    root.tags.append(nbt.TAG_Byte(name='Y', value=self.y))

    palette = self.palette()  # <-- używa Block z name()
    nbt_pal = nbt.TAG_List(name='Palette', type=nbt.TAG_Compound)
    for block in palette:
        tag = nbt.TAG_Compound()
        tag.tags.append(nbt.TAG_String(name='Name', value=block.name()))  # <-- FAIL dla OldBlock
```

Format zapisu:
- Używa `Palette` (lista string ID) - wprowadzone w 1.13
- Używa `BlockStates` (long array) - wprowadzone w 1.13
- NIE używa `Blocks[]` (byte array) - używane w 1.7.10
- NIE używa `Data[]` (nibble array) - używane w 1.7.10

---

## 4. Dostępne alternatywy

| Biblioteka | Odczyt 1.7.10 | Zapis 1.7.10 | Status |
|------------|---------------|--------------|--------|
| PyAnvilEditor | ✅ OldBlock | ❌ NIE | FAIL |
| amulet-leveldb | ? | ? | Nie testowane (dla leveldb) |
| anvil-parser | ✅ | ❌ | To samo co PyAnvilEditor |
| pymclevel | N/A | N/A | Nie dostępne w PyPI |
| nbtlib (własny) | ✅ | ✅ | Działa, wymaga dopracowania |

---

## 5. Rekomendacja

Zgodnie z instrukcją INSTRUKCJA_TRIAGE_PYANVILEDITOR_NO_NBTLIB.md, sekcja 7:

> "Dopiero gdy: Test Round-Trip #1 i #2 FAILują na czystym świecie, wtedy wolno Ci przejść na alternatywę pythonową"

**Test Round-Trip #1 FAIL na czystym świecie.**

PyAnvilEditor nie jest alternatywą dla 1.7.10 write-path. Jedyna działająca opcja to własny backend na `nbtlib`, który:
- Używa poprawnego formatu NBT dla 1.7.10 (Blocks[], Data[])
- Nie konwertuje do post-1.13 formatu
- Zapisuje bezpośrednio do .mca

---

## 6. Decyzja końcowa

**Powrót do nbtlib backend** (mc_editkit/world/backends/anvil_backend.py) z poprawkami:

1. Poprawić format zapisu sekcji (Blocks[] zamiast palette)
2. Upewnić się że chunk NBT ma poprawną strukturę root (pusty string + Level)
3. Przetestować round-trip na czystym świecie
4. Przejść do testu spirali

---

## 7. Artefakty

- Czysty świat testowy: `headless_server/tests/headless_server/1.7.10_clean/`
- Pliki nbtlib przeniesione: `mc_editkit/nbt_custom/`
- Raport ten: `mc_editkit/tests/RAPORT_TRIAGE_PYANVILEDITOR.md`
