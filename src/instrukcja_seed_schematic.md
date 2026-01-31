# Instrukcja dla agenta: generowanie schematica z poprawnym stanem początkowym (ring counter na dropperach)

Cel: wygenerować schematic/structure tak, żeby po wklejeniu na mapę układ **od razu działał** (bez ręcznych poprawek), tzn.:
- ring counter ma **dokładnie 1 token (1 item)** w jednym dropperze,
- reszta dropperów jest pusta,
- komparatory mają co czytać, a “cyfry” mają się zmieniać cyklicznie,
- jeśli pipeline JSON→schematic nie wspiera TileEntities/NBT, agent ma to wykryć i zaproponować bezpieczny fallback.

> Kontekst: w ring counterze na dropperach **zawsze** potrzebujesz tokena (1 item w jednym dropperze), inaczej układ nie ma stanu i “nie liczy”.

---

## 1) Czy format `.schematic`/NBT potrafi przenosić zawartość droppera/skrzyni?

Tak — klasyczny format MCEdit `.schematic` jest plikiem **NBT** i zawiera listę **TileEntities**, w których jest m.in. inwentarz (`Items`) dla droppera, chest, furnance itd.

**Wniosek:** da się zrobić schematic, który po wklejeniu ma dropper z itemem w środku.

**Warunek:** Twój konwerter `voxel_grid.json → schematic` musi:
- emitować `TileEntities` dla bloków typu tile entity,
- przepisać zawartość `nbt` z voxel grid do NBT tile entity.

Jeśli konwerter tego nie robi, to mimo poprawnego `voxel_grid.json` schematic będzie “pusty” (bez tokena) i ring counter nie zadziała.

---

## 2) Zasada stanu początkowego ring countera

### 2.1 Wymóg twardy: dokładnie 1 token
Agent musi wymusić, że:
- **dokładnie jeden** dropper w pierścieniu ma 1 item (token),
- **żaden inny** dropper nie ma itemów.

Jeżeli tokenów jest:
- 0 → układ nie działa,
- >1 → układ może “skakać”, duplikować sekwencję lub odpalać kilka cyfr.

### 2.2 Gdzie umieszczać token
Domyślnie: **D0** (pierwszy dropper pierścienia), zgodnie z designem.

Jeśli w spec jest inny start (np. D7), token ma trafić do wskazanego droppera.

---

## 3) Jak kodować zawartość droppera w `voxel_grid.json`

### 3.1 Konwencja JSON (w tym projekcie)
W voxel grid każdy voxel może mieć pole:
- `nbt` → obiekt, który konwerter powinien przepisać do NBT tile entity.

Dla droppera z tokenem ustaw:

```json
{
  "x": 6, "y": 1, "z": 6,
  "block": "minecraft:dropper",
  "properties": {"facing": "east"},
  "purpose": "D0",
  "nbt": {
    "Items": [
      {"Slot": 0, "id": "minecraft:cobblestone", "Count": 1}
    ]
  }
}
```

Dla pozostałych dropperów:
- `nbt` pomiń albo ustaw `"Items": []`.

### 3.2 Token: jaki item wybrać
Użyj dowolnego “bezpiecznego” itemu:
- `minecraft:cobblestone` (najprostsze),
- ewentualnie `minecraft:stone`.

Ważne: **zawsze 1 sztuka** (Count = 1), nie stack.

---

## 4) Walidacja “seed token” (obowiązkowa przed uznaniem schematica za gotowy)

Agent ma dodać do walidatora/debuggera (np. `debug_redstone.py`) check:

1) Zidentyfikuj wszystkie droppery w ring counterze (np. po `purpose` D0..D9 albo po sekcji `ring_counter_10`).
2) Policz ile z nich ma niepuste `nbt.Items`.
3) Jeśli wynik != 1 → zgłoś błąd krytyczny:

- `SEED: ring counter must contain exactly 1 item in exactly 1 dropper (found N)`

Dodatkowo:
- jeśli token jest w dropperze, który **nie należy** do pierścienia → błąd,
- jeśli token jest w dropperze, ale `facing` nie prowadzi do kolejnego droppera → ostrzeżenie / błąd routing.

---

## 5) Walidacja “TileEntities rzeczywiście trafią do schematica” (weryfikacja pipeline)

Ponieważ konwersja JSON→schematic robi “coś innego”, agent ma wykonać przynajmniej jedną z metod weryfikacji:

### Metoda A (najlepsza): test round-trip w grze
1) Wygeneruj schematic.
2) Wklej w świecie testowym.
3) Otwórz GUI droppera D0.
4) Sprawdź, czy token (1 item) jest w środku.

Jeśli nie ma tokena, to konwerter nie przenosi TE/NBT.

### Metoda B (jeśli masz dostęp do NBT w pipeline)
1) Otwórz wynikowy plik `.schematic` (NBT).
2) Sprawdź, czy istnieje lista `TileEntities`.
3) Sprawdź, czy jest wpis TE dla (x,y,z) droppera D0 i czy ma `Items`.

---

## 6) Fallback, jeśli konwerter nie przenosi NBT/TileEntities

Jeśli token nie pojawia się po wklejeniu (czyli TE/NBT nie jest w schematiku), agent ma **nie zgadywać** i zastosować jeden z tych wariantów:

### Fallback 1: Instrukcja post-setup (najprostsze)
Po wklejeniu schematica użytkownik:
1) otwiera dropper D0,
2) wkłada 1× cobblestone,
3) zamyka GUI.

To gwarantuje start.

### Fallback 2: Moduł “auto-seed” w samym schematiku
Agent dokłada do schematica mały moduł startowy:
- chest z 1 itemem + hopper lub dropper, który jednorazowo poda item do D0 (na impuls startowy).
To zwiększa układ, ale działa bez ręcznych działań.

### Fallback 3: Command block seeding (tylko jeśli to akceptujesz)
Jeśli command blocki są dozwolone:
- dodaj jednorazowy command block, który wstawi item do TE (np. `/blockdata` / inne mechaniki zależne od wersji).
Uwaga: w 1.7.10 i na serwerach bywa to ograniczone — to opcja awaryjna.

---

## 7) Checklista “schematic readiness” (przed oddaniem układu jako gotowy)

**A. Spójność danych**
- [ ] `voxel_grid.json` ma ring counter w `sections.ring_counter_10`
- [ ] `expected_behavior` i `timing` są spójne z zegarem

**B. Seed token**
- [ ] dokładnie jeden dropper ma `nbt.Items` z 1 itemem
- [ ] pozostałe droppery mają pusto
- [ ] walidator zgłasza PASS dla reguły SEED

**C. Połączenia**
- [ ] bus zasilania dropperów jest połączony z `clock_out` (BFS po redstone)
- [ ] komparatory stoją poprawnie (czytają droppery)
- [ ] command blocki są na wyjściach komparatorów

**D. Test w grze**
- [ ] po wklejeniu, otwarcie D0 pokazuje token
- [ ] po uruchomieniu zegara cyfra zmienia się co ~1s
- [ ] w 10 sekund widzisz pełny cykl 0..9 (lub w logu/trace)

---

## 8) Minimalny pakiet screenów, jeśli pojawi się problem (procedura dowodowa)

Jeżeli po wklejeniu układ nie działa, agent ma poprosić o:
1) Screen z otwartym GUI droppera D0 (czy jest token).
2) Screen z F3 celując w komparator (potwierdzenie “Redstone Comparator”).
3) Screen zegara (czy bus jest stale zasilony, czy pulsuje).
4) Screen całego pierścienia z góry (czy redstone bus jest ciągły).

To pozwala szybko stwierdzić: brak tokena vs brak impulsów vs błąd routingu.

---

## 9) Kluczowa zasada
Ring counter na dropperach jest **maszyną stanową**. Stanem jest **pozycja tokena (itemu)**.  
Jeśli schematic nie zawiera tokena (TE/NBT) albo zegar nie daje impulsów (OFF→ON), to układ nie będzie liczył, nawet jeśli geometria bloków jest idealna.
