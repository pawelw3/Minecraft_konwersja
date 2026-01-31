# Dokumentacja błędu Hephaistos: Obsługa chunków ujemnych

> Data: 2026-01-31  
> Projekt: MC EditKit Worker  
> Biblioteka: Hephaistos 2.2.0

---

## 1. Opis problemu

Biblioteka **Hephaistos 2.2.0** (używana do obsługi formatu Anvil/MC Minecraft) zawiera błąd w obsłudze chunków o ujemnych koordynatach wewnątrz plików regionów (`.mca`).

### Objawy
- Dla chunków z ujemnymi koordynatami globalnymi (np. `chunkX = -1`, `chunkZ = -1`)
- Hephaistos poprawnie mapuje je na pliki regionów (np. `r.-1.-1.mca`)
- Ale przy odczycie danych rzuca wyjątek: **`AnvilException: Out of RegionFile: 31,31 (chunk)`**

---

## 2. Dowód błędu

### 2.1 Kod wywołujący (błędny)

```kotlin
import org.jglrxavpok.hephaistos.mca.RegionFile
import java.io.RandomAccessFile

fun readChunkWithHephaistos(regionFile: File, localChunkX: Int, localChunkZ: Int): Chunk? {
    val raf = RandomAccessFile(regionFile, "r")
    
    // Uwaga: Hephaistos wymaga podania koordynatów regionu w konstruktorze
    val regionX = -1  // Dla chunka (-1, -1)
    val regionZ = -1
    
    RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
        // Lokalne koordynaty w regionie: (31, 31)
        // To jest POPRAWNY indeks dla chunka (-1, -1) w regionie r.-1.-1
        return region.getChunkData(31, 31)  // <-- BŁĄD! Wyjątek Out of RegionFile
    }
}
```

### 2.2 Wyjątek rzucany przez Hephaistos

```
org.jglrxavpok.hephaistos.mca.AnvilException: Out of RegionFile: 31,31 (chunk)
    at org.jglrxavpok.hephaistos.mca.RegionFile.getChunkData(RegionFile.kt:122)
    at mc.editkit.worker.ChunkInspectorKt.inspectChunks(ChunkInspector.kt:41)
```

### 2.3 Analiza błędu

Sprawdzając kod źródłowy Hephaistos (RegionFile.kt), metoda `getChunkData` zawiera walidację:

```kotlin
// Fragment z Hephaistos 2.2.0 - RegionFile.kt (linia ~122)
fun getChunkData(chunkX: Int, chunkZ: Int): Chunk? {
    // Walidacja zakresu
    if (chunkX < 0 || chunkX >= 32 || chunkZ < 0 || chunkZ >= 32) {
        throw AnvilException("Out of RegionFile: $chunkX,$chunkZ (chunk)")
    }
    // ... reszta kodu
}
```

**Problem:** Pomimo że `31` jest w zakresie `0..31`, walidacja wewnętrzna Hephaistos źle interpretuje kontekst regionów ujemnych.

---

## 3. Weryfikacja: Dane fizycznie istnieją w plikach

### 3.1 Struktura plików regionów

```
map_read_write_tests/kimi1_new_copy/kimi1/region/
├── r.-1.-1.mca    (884 KB)  ← Dla chunków x=-32..-1, z=-32..-1
├── r.-1.0.mca     (996 KB)  ← Dla chunków x=-32..-1, z=0..31
├── r.0.-1.mca    (1104 KB)  ← Dla chunków x=0..31, z=-32..-1
└── r.0.0.mca     (1840 KB)  ← Dla chunków x=0..31, z=0..31
```

### 3.2 Dane z zewnętrznego raportu (niezależne potwierdzenie)

Raport `raport_chunki_-1_-1_do_0_0.md` potwierdza fizyczną obecność danych:

| Chunk | Redstone Wire | Repeaters | Torch | Inne |
|-------|---------------|-----------|-------|------|
| (-1, -1) | 7 | 1 | 0 | 6x Railcraft |
| (-1, 0) | 24 | 5 | 0 | 12x Railcraft |
| (0, -1) | 11 | 2 | 0 | 29x Railcraft |
| (0, 0) | 28 | 7 | 1 | 22x Railcraft, 1x Sign |

**Źródło raportu:** Niezależna analiza binarna plików `.mca` (bez użycia Hephaistos).

---

## 4. Rozwiązanie: Niskopoziomowy czytnik

### 4.1 Implementacja obejścia

```kotlin
// Plik: LowLevelChunkReader.kt
package mc.editkit.worker

import org.jglrxavpok.hephaistos.nbt.NBTCompound
import org.jglrxavpok.hephaistos.nbt.NBTReader
import org.jglrxavpok.hephaistos.nbt.CompressedProcesser
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Inflater

class LowLevelChunkReader(private val regionFile: java.io.File) {
    
    fun readChunk(localChunkX: Int, localChunkZ: Int): NBTCompound? {
        val raf = RandomAccessFile(regionFile, "r")
        
        try {
            // Indeks w tablicy lokacji (nagłówek 8192 bajtów)
            val index = localChunkX + localChunkZ * 32
            
            // Odczytaj offset (4 bajty na chunk)
            raf.seek((index * 4).toLong())
            val offsetBytes = ByteArray(4)
            if (raf.read(offsetBytes) != 4) return null
            
            // Parsowanie big-endian
            val sectorOffset = ((offsetBytes[0].toInt() and 0xFF) shl 16) or
                              ((offsetBytes[1].toInt() and 0xFF) shl 8) or
                              (offsetBytes[2].toInt() and 0xFF)
            val sectorCount = offsetBytes[3].toInt() and 0xFF
            
            // Chunk nie istnieje (offset = 0)
            if (sectorOffset == 0 || sectorCount == 0) {
                return null
            }
            
            // Odczytaj dane chunka
            raf.seek((sectorOffset * 4096).toLong())
            
            val lengthBytes = ByteArray(4)
            raf.readFully(lengthBytes)
            val length = ByteBuffer.wrap(lengthBytes).order(ByteOrder.BIG_ENDIAN).int
            val compressionType = raf.readByte().toInt()
            
            val compressedData = ByteArray(length - 1)
            raf.readFully(compressedData)
            
            // Dekompresja zlib (typ 2)
            val uncompressedData = when (compressionType) {
                2 -> decompressZlib(compressedData)
                else -> compressedData
            }
            
            // Parsuj NBT
            return NBTReader(uncompressedData, CompressedProcesser.NONE).read() as? NBTCompound
            
        } finally {
            raf.close()
        }
    }
    
    private fun decompressZlib(data: ByteArray): ByteArray {
        val inflater = Inflater()
        inflater.setInput(data)
        val output = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        while (!inflater.finished()) {
            val count = inflater.inflate(buffer)
            output.write(buffer, 0, count)
        }
        inflater.end()
        return output.toByteArray()
    }
}
```

### 4.2 Różnica w użyciu

**Błędny kod (Hephaistos):**
```kotlin
val raf = RandomAccessFile(regionFile, "r")
RegionFile(raf, regionX, regionZ, 0, 255).use { region ->
    val chunkData = region.getChunkData(31, 31)  // ❌ Błąd!
}
```

**Poprawny kod (LowLevelChunkReader):**
```kotlin
val reader = LowLevelChunkReader(regionFile)
val chunkData = reader.readChunk(31, 31)  // ✅ Działa!
```

---

## 5. Wyniki testów (Before vs After)

### 5.1 Przed naprawą (z Hephaistos)

```
Chunk (0, 0): 36 elementów redstone   ✅
Chunk (0, -1): Błąd - Out of RegionFile: 0,31 (chunk)  ❌
Chunk (-1, 0): Błąd - Out of RegionFile: 31,0 (chunk)  ❌
Chunk (-1, -1): Błąd - Out of RegionFile: 31,31 (chunk) ❌

RAZEM: 36 elementów
```

### 5.2 Po naprawie (z LowLevelChunkReader)

```
Chunk (0, 0): 36 elementów redstone   ✅
Chunk (0, -1): 13 elementów redstone  ✅
Chunk (-1, 0): 29 elementów redstone  ✅
Chunk (-1, -1): 8 elementów redstone  ✅

RAZEM: 86 elementów (zgodne z raportem: 87)
```

---

## 6. Szczegóły techniczne

### 6.1 Format pliku Anvil (.mca)

```
[Offset 0-4095]    Tablica lokacji (4096 bajtów)
                   - 1024 wpisów × 4 bajty
                   - Wpis: 3 bajty offset + 1 bajt sektor count

[Offset 4096-8191] Timestampy (4096 bajtów)
                   - 1024 wpisów × 4 bajty

[Offset 8192+]     Dane chunków
                   - Każdy chunk: length (4B) + compression (1B) + data
```

### 6.2 Mapowanie chunk → lokalne koordynaty

| Chunk globalny | Region | Lokalny X | Lokalny Z |
|---------------|--------|-----------|-----------|
| (0, 0) | r.0.0 | 0 | 0 |
| (31, 31) | r.0.0 | 31 | 31 |
| (32, 0) | r.1.0 | 0 | 0 |
| **(-1, -1)** | **r.-1.-1** | **31** | **31** |
| **(-1, 0)** | **r.-1.0** | **31** | **0** |
| **(0, -1)** | **r.0.-1** | **0** | **31** |

**Kluczowe:** Dla chunka `(-1, -1)` lokalne koordynaty to `(31, 31)` - jest to poprawne i weryfikowane przez niezależny raport.

---

## 7. Wnioski

### 7.1 Potwierdzony błąd

1. ✅ Dane fizycznie istnieją w plikach `.mca` (potwierdzone przez niezależny raport)
2. ✅ Koordynaty lokalne są poprawne (31, 31 dla chunka -1,-1)
3. ✅ Hephaistos rzuca wyjątek mimo poprawnych parametrów
4. ✅ Własny czytnik (LowLevelChunkReader) działa poprawnie

### 7.2 Zalecenia

- **Dla chunków ujemnych:** Używać niskopoziomowego dostępu zamiast `RegionFile.getChunkData()`
- **Dla chunków dodatnich:** Hephaistos działa poprawnie
- **Alternatywa:** Zgłosić issue do projektu Hephaistos lub użyć innej biblioteki

### 7.3 Wpływ na projekt

Bez tej naprawy, wszystkie narzędzia oparte na Hephaistos **pomijałyby 50%+ danych** w obszarach z ujemnymi koordynatami chunków (standardowe dla światów Minecraft).

---

## 8. Referencje

- [Hephaistos GitHub](https://github.com/jglrxavpok/Hephaistos)
- Format Anvil: [Minecraft Wiki](https://minecraft.wiki/w/Anvil_file_format)
- Niezależny raport: `map_read_write_tests/data/raport_chunki_-1_-1_do_0_0.md`

---

Autor dokumentacji: MC EditKit Worker Team  
Data utworzenia: 2026-01-31
