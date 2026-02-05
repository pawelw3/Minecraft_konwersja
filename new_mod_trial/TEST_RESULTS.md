# Testy CuttableBlocks

## Szablon raportu testów

```markdown
# Testy CuttableBlocks v1.0.0

## Data: YYYY-MM-DD
## Tester: [nazwa]
## Wersja moda: [commit/tag]

---

## 1. Testy integracyjne (headless server)

### 1.1 Podstawowa integracja
- [ ] T1: Serwer startuje z modem
- [ ] T2: Wczytanie chunków z Cuttable Blocks
- [ ] T3: Tick serwera (30s) bez błędów
- [ ] T4: Restart serwera - dane zachowane
- [ ] T5: Inspekcja NBT w region files

**Uwagi:**
- 

**Logi:**
```
[ Path do logów lub wklej istotne fragmenty ]
```

---

## 2. Testy funkcjonalne (manualne)

### 2.1 Podstawowe cięcie
- [ ] M1: Cięcie Stone z różnych kierunków
- [ ] M2: Drop oryginalnego bloku po zniszczeniu
- [ ] M3: Middle-click daje oryginalny blok
- [ ] M4: Restart serwera zachowuje stan

### 2.2 Metadane i różne bloki
- [ ] M5: Cięcie Wool z różnymi kolorami (metadata)
- [ ] M6: Cięcie Wood (różne typy)
- [ ] M7: Cięcie bloku z innego moda (AE2, itp.)

### 2.3 Renderowanie
- [ ] M8: Bloki renderują się poprawnie z różnych kątów
- [ ] M9: Tekstury oryginalnych bloków są zachowane
- [ ] M10: Brak z-fighting lub innych artefaktów

### 2.4 Kolizje
- [ ] M11: Gracz nie przechodzi przez przycięte bloki
- [ ] M12: Raycasting (celowanie) działa poprawnie

**Uwagi:**
- 

---

## 3. Podsumowanie

**Status:** [PASS / FAIL / PARTIAL]

**Krytyczne błędy:**
- 

**Znane problemy (niekrytyczne):**
- 

**Rekomendacje:**
- 
```

---

## Historia testów

### Test #1 - [Data]
**Wersja:** [tag/commit]
**Tester:** [nazwa]
**Status:** [PASS/FAIL]

**Podsumowanie:**
[Krótki opis wyników]

**Link do szczegółowego raportu:**
[Raport wypełniony powyższym szablonem]
