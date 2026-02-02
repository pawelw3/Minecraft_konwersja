# Raport: Problem konwersji mapy do Minecraft 1.14.4 Vanilla

**Data utworzenia:** 2026-02-02  
**Mapa:** `headless_server\1.14\world_no_mods`  
**Docelowa wersja:** Minecraft 1.14.4 Vanilla

---

## 1. Opis problemu

Serwer Minecraft 1.14.4 Vanilla nie może załadować mapy `world_no_mods` z powodu niekompatybilnych Tile Entities (TE) pochodzących z modów Minecraft 1.7.10.

W wersji 1.14+ wprowadzono restrykcyjną walidację identyfikatorów (ID) bloków i Tile Entities - dozwolone są wyłącznie znaki:
```
[a-z0-9/._-]
```

Tile Entities z modów 1.7.10 używają jednak wielkich liter w nazwach (np. `TileEntityCarpentersBlock`), co powoduje błąd parsowania i zatrzymanie serwera podczas ładowania świata.

---

## 2. Symptomy błędu

### Logi serwera
```
[Server thread/WARN]: Exception loading entity: 
n: Non [a-z0-9/._-] character in path of location: minecraft:TileEntityCarpentersBlock
    at qv.<init>(SourceFile:38) ~[server.jar:?]
    ...
Caused by: n: Non [a-z0-9/._-] character in path of location: minecraft:TileEntityCarpentersBlock
```

### Zachowanie serwera
- Serwer startuje poprawnie
- Zatrzymuje się na 95-97% przy "Preparing spawn area"
- Nie odpowiada na połączenia
- Proces Java działa ale nie przetwarza chunków

---

## 3. Lista problematycznych Tile Entities

### Zidentyfikowane Tile Entities powodujące błędy:

| Nazwa Tile Entity | Mod źródłowy | Opis |
|------------------|--------------|------|
| `TileEntityCarpentersBlock` | Carpenter's Blocks | Bloki dekoracyjne z możliwością zmiany wyglądu |
| `container.betterstorage.reinforcedLocker` | BetterStorage | Wzmocnione skrzynie/lockery |
| `TileTrainWbench` | Traincraft | Warsztat pociągów |
| `tileLantern` | *Nieznany mod* | Latarnie dekoracyjne |
| `grc.tileentity.fermentBarrel` | Growthcraft | Beczki fermentacyjne |
| `savedMultipart` | ForgeMultipart | System mikro-bloków |
| `ItemFrame` | Vanilla (stary format) | Ramki na przedmioty zapisane z wielką literą |
| `MG` | *Nieznany mod* | Niezidentyfikowany obiekt modowy |

### Dodatkowe problematyczne identyfikatory (z logów FML):

```
CarpentersBlocks:blockCarpentersSlope
CarpentersBlocks:blockCarpentersStairs
CarpentersBlocks:blockCarpentersBlock
Growthcraft|Bamboo:grc.bambooStairs
Growthcraft|Bamboo:grc.bambooDoor
eplus:advancedEnchantmentTable
eplus:arcane_inscriber
```

---

## 4. Próby rozwiązania

### Próba 1: Użycie map_cleaner
**Status:** ❌ Nieudane

Narzędzie `map-cleaner` zostało zaprojektowane dla formatu Minecraft 1.7.10 (Anvil z ID numerycznymi 0-4095), podczas gdy mapa `world_no_mods` jest już w formacie 1.14+ (Paletted Container).

**Wynik:**
- Przetworzono 767 regionów
- Zmodyfikowane chunki: 0
- Tile Entities usunięte: 0

Narzędzie nie potrafi odczytać nowego formatu sekcji chunków i nie widzi Tile Entities do usunięcia.

### Próba 2: Uruchomienie serwera Vanilla 1.14.4
**Status:** ❌ Nieudane

Serwer zatrzymuje się na 95-97% przygotowania spawn area z powodu wyjątków parsowania Tile Entities.

---

## 5. Rekomendowane rozwiązania

### Opcja 1: Ręczna edycja NBT (Najbardziej niezawodna)
Użyć narzędzia **NBTExplorer** lub **MCEdit Unified** do:
1. Otwarcia plików regionów (`.mca`)
2. Usunięcia wszystkich Tile Entities z listy problematycznych
3. Zapisania zmian

**Zalety:** Pełna kontrola nad danymi  
**Wady:** Czasochłonne przy dużej liczbie chunków

### Opcja 2: Serwer Forge 1.14.4 z modami kompatybilności
Zainstalować Forge 1.14.4 i spróbować uruchomić mapę - Forge może być bardziej tolerancyjny dla błędnych Tile Entities i automatycznie je usunąć.

**Zalety:** Automatyczne czyszczenie  
**Wady:** Wymaga instalacji Forge i testów

### Opcja 3: Użycie narzędzia do konwersji formatu
Skrypt Python z biblioteką `anvil-parser` lub `nbtlib` do:
1. Odczytania wszystkich chunków
2. Usunięcia Tile Entities pasujących do wzorca (uppercase w ID)
3. Zapisania zmodyfikowanych chunków

**Zalety:** Automatyzacja  
**Wady:** Wymaga implementacji obsługi formatu 1.14+

### Opcja 4: Użycie innej mapy
Wykorzystać mapę która nie zawiera danych z modów (czysta mapa vanilla lub już wyczyszczona).

---

## 6. Techniczne szczegóły

### Format Tile Entity w 1.14+
```java
// Walidacja ID w Minecraft 1.14+
if (!id.matches("^[a-z0-9/._-]+$")) {
    throw new IllegalArgumentException(
        "Non [a-z0-9/._-] character in path of location: " + id
    );
}
```

### Różnice w formatach

| Aspekt | 1.7.10 | 1.14+ |
|--------|--------|-------|
| ID bloków | Numeryczne (0-4095) | String ID (`minecraft:stone`) |
| Tile Entities | Dowolne stringi | Tylko lowercase `[a-z0-9/._-]` |
| Format chunk | Blocks/Add/Data | Paletted Container |

---

## 7. Podsumowanie

Mapa `world_no_mods` wymaga głębokiego czyszczenia Tile Entities z modów 1.7.10 przed załadowaniem na serwerze 1.14+. Standardowe narzędzia nie są w stanie poradzić sobie z problemem ze względu na różnice w formatach zapisu danych między wersjami.

**Priorytet:** Wysoki - blokuje możliwość testowania migracji mapy  
**Sugerowane działanie:** Implementacja skryptu czyszczącego Tile Entities dla formatu 1.14 lub ręczna edycja NBT

---

## 8. Pliki do analizy

Główne pliki regionów do sprawdzenia (najbliższe spawnu):
```
headless_server\1.14\world_no_mods\region\r.0.0.mca
headless_server\1.14\world_no_mods\region\r.-1.0.mca
headless_server\1.14\world_no_mods\region\r.0.-1.mca
headless_server\1.14\world_no_mods\region\r.-1.-1.mca
```

---

*Raport wygenerowany automatycznie na podstawie analizy logów serwera.*
