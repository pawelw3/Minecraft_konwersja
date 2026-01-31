# Środowisko testowe: Redstone + Command Block

## Target Environment

| Parametr | Wartość |
|----------|---------|
| Minecraft | 1.7.10 |
| Forge | 10.13.4.1614 |
| Mody | Brak (vanilla) |
| Świat testowy | map_read_write_tests/kimi1 |
| Współrzędne testu | x=50, y=64, z=50 (offset 50 bloków od 0,0,0) |

## Cel testu

Weryfikacja poprawności wstawiania bloków redstone oraz tile entities (Command Block) na mapę Minecraft 1.7.10.

Układ testowy składa się z:
1. **Dźwigni** (Lever) jako źródła sygnału redstone
2. **Kabla redstone** (Redstone Dust) propagującego sygnał
3. **Repeaterów** z opóźnieniem 4 ticków każdy (łącznie 16 ticków = ~1.6s)
4. **Command Blocka** na końcu łańcucha, wykonującego komendę logującą na konsolę

## Oczekiwane zachowanie

Po uruchomieniu serwera i przełączeniu dźwigni:
1. Sygnał redstone rozchodzi się przez kabel
2. Po opóźnieniu w repeaterach dociera do Command Blocka
3. Command Block wykonuje komendę `/say [TEST_REDSTONE] Układ działa!`
4. Wiadomość pojawia się w konsoli serwera

## Kryteria sukcesu

| Test | Opis | Wynik pozytywny |
|------|------|-----------------|
| Weryfikacja bloków | Sprawdzenie czy wszystkie bloki zostały wstawione | Wszystkie 12 bloków na swoich miejscach |
| Weryfikacja TE | Sprawdzenie Command Blocka i jego NBT | Tile Entity z poprawnym polem Command |
| Test w grze | Włączenie dźwigni i obserwacja konsoli | Wiadomość w konsoli po ~1.6s |

## Debugowanie

Punkty pomiarowe w świecie:
- (50, 64, 50) - dźwignia (źródło)
- (54, 64, 50) - pierwszy repeater (delay=4)
- (58, 64, 50) - drugi repeater (delay=4)
- (60, 64, 50) - command block (cel)

Komendy diagnostyczne:
```
/blockdata 60 64 50 {}  - wyświetla dane Command Blocka
/testforblock 60 64 50 minecraft:command_block  
```
