# Handoff: Poprawki Map Cleaner - logowanie i fragmentacja

## Podsumowanie sesji

Naprawiono dwa główne problemy zgłoszone przez użytkownika:
1. **Brak logowania podczas zapisu** - program wydawał się "zawieszony"
2. **Puchnięcie plików regionów** - wzrost rozmiaru o ~100%

## Wprowadzone poprawki

### A) Logowanie postępu zapisu (RegionProcessor.kt)

**Lokalizacja:** `writeModifiedChunks()` 

**Zmiany:**
- Log na początku: `"Zapisywanie N zmodyfikowanych chunków..."`
- Log co 100 chunków: `"Zapisano X/Y chunków..."`
- Log na końcu: `"Zapis zakończony: N chunków (in-place: X, append: Y)"`

### B) Naprawa fragmentacji - nadpisywanie w starym miejscu (RegionProcessor.kt)

**Problem:** Poprzednia wersja ZAWSZE dopisywała na koniec pliku (`append-only`), pozostawiając stare sektory jako martwe.

**Rozwiązanie:** 
- Odczytaj stary offset i rozmiar z nagłówka regionu
- Jeśli `newSectorCount <= oldSectorCount` → nadpisz w starym miejscu (`in-place`)
- Jeśli nowy chunk większy → dopisz na końcu (`append`)

**Efekt:** Większość chunków po czyszczeniu nie zmienia rozmiaru drastycznie → znacznie mniej fragmentacji.

### C) Timeout dla wątków (WorldScanner.kt)

**Zmiany:**
- Dry-run: timeout 5 minut
- Zapis: timeout 30 minut
- Jeśli timeout → komunikat diagnostyczny + `shutdownNow()`

## Pliki zmodyfikowane

```
map_cleaning/jvm/src/main/kotlin/mapcleaner/
├── RegionProcessor.kt    # Logowanie + nadpisywanie in-place
└── WorldScanner.kt       # Timeout dla executor
```

## Przykładowe nowe logi

```
Znaleziono 9 regionów w 1 wymiarach
[9/9] Przetworzono r.0.0.mca (overworld)
  Zapisywanie 760 zmodyfikowanych chunków...
    Zapisano 100/760 chunków...
    Zapisano 200/760 chunków...
    ...
  Zapis zakończony: 760 chunków (in-place: 680, append: 80)
```

## Zalecenia przed uruchomieniem

1. **Zawsze najpierw dry-run:**
   ```bash
   java -jar map-cleaner.jar map_1710_no_mods --dry-run
   ```

2. **Jeśli mapa duża lub dysk wolny - zmniejsz wątki:**
   ```bash
   java -jar map-cleaner.jar map_1710_no_mods --threads 2
   ```

3. **Obserwuj logi** - teraz widać postęp zapisu i liczbę "in-place" vs "append"

## Jeśli nadal są problemy

- Timeout 30 minut może być za krótki dla bardzo dużych map na wolnym dysku
- W razie kolejnego "zawieszenia" sprawdź czy w logach pojawił się komunikat timeout
- Jeśli "append" jest bardzo częste (>50%) - chunki faktycznie rosną (np. przez zmianę kompresji)
