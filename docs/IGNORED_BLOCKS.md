# Bloki i Tile Entities do ignorowania podczas konwersji

> **Ostatnia aktualizacja:** 2026-01-30

Ten dokument zawiera listę bloków i tile entities z modów, które **NIE POWINNY BYĆ KONWERTOWANE** z wersji 1.7.10 na 1.18.2.

## Dlaczego niektóre elementy są ignorowane?

- **Techniczne Tile Entities** - Używane przez silnik gry/mody do wewnętrznej logiki, niewidoczne dla gracza
- **Markery/Placeholder'y** - Służą do oznaczania obszarów, nie są właściwymi blokami
- **Systemowe bloki** - Część implementacji mechanizmów (np. windy), nie mają odpowiedników
- **Usunięte funkcjonalności** - Mody w 1.18.2 mogą nie mieć tych funkcji

---

## Lista ignorowanych Tile Entities

### Railcraft

| ID | Powód ignorowania | Uwagi |
|----|-------------------|-------|
| `RCHiddenTile` | Tile entity techniczne, część systemu wind/elevatorów | Niewidoczne w grze, używane do logiki transportu między poziomami |

---

## Lista ignorowanych Bloków

### (Do uzupełnienia w razie potrzeby)

---

## Jak dodać nowy element do ignorowania?

1. Dodaj wpis do odpowiedniej tabeli powyżej
2. Podaj nazwę modu, ID bloku/TE i krótkie uzasadnienie
3. Zaktualizuj datę w nagłówku dokumentu

---

## Związane dokumenty

- `PLAN_KONWERSJI.md` - Główny plan konwersji
- `LISTA_KONWERSJI_MODOW.md` - Lista modów i ich mapowanie
- Wizualizacje znajdują się w `output/visualizations/`
