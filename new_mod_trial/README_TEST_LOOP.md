# Pętla Testowa dla CuttableBlocks Mod

## Szybki start

```powershell
# 1. Zbuduj moda
.\gradlew.bat build

# 2. Skopiuj do mods\
Copy-Item build\libs\CuttableBlocks-1.0.0.jar $env:APPDATA\.minecraft\mods\

# 3. Uruchom test (automatycznie)
python test_client_loop.py
```

## Skrypty

### `launch_minecraft.py`
Automatyzacja launchera przez Pywinauto.
- Obsługuje dialog aktualizacji
- Klika Play w launcherze
- Nie wymaga interakcji użytkownika

Uruchomienie:
```bash
python launch_minecraft.py
```

### `test_client_loop.py`
Pełna pętla testowa:
1. ✅ Buduje moda (gradle)
2. ✅ Deploy do mods\
3. ✅ Uruchamia launcher (pywinauto)
4. ✅ Monitoruje logi (60s)
5. ✅ Wykrywa crash-e
6. ✅ Analizuje błędy moda
7. ✅ Generuje raport

Uruchomienie:
```bash
python test_client_loop.py
```

## Ręczna pętla debugowania (bez Pywinauto)

Jeśli Pywinauto nie działa, użyj tej procedury:

### Krok 1: Budowa
```powershell
cd new_mod_trial
.\gradlew.bat build
```

### Krok 2: Deploy
```powershell
Copy-Item build\libs\CuttableBlocks-1.0.0.jar $env:APPDATA\.minecraft\mods\ -Force
```

### Krok 3: Uruchomienie
Ręcznie uruchom Shiginima Launcher i kliknij Play.

### Krok 4: Monitorowanie logów
W osobnym PowerShell:
```powershell
Get-Content $env:APPDATA\.minecraft\logs\fml-client-latest.log -Wait -Tail 100
```

### Krok 5: Szukaj błędów
```powershell
Select-String -Path $env:APPDATA\.minecraft\logs\fml-client-latest.log -Pattern "cuttable|CuttableTE|error|Exception" -CaseSensitive:$false
```

### Krok 6: Sprawdź crash-e
```powershell
Get-ChildItem $env:APPDATA\.minecraft\crash-reports\ -Filter "crash-*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

## Struktura logów klienta

| Plik | Zawartość |
|------|-----------|
| `logs/fml-client-latest.log` | Główny log Forge (szukaj błędów tutaj) |
| `logs/latest.log` | Log gry (mniej szczegółowy) |
| `crash-reports/crash-*.txt` | Raporty crashy (szczegóły błędów) |

## Typowe błędy do szukania

```
cuttableblocks - Exception
CuttableTE - error
ClassNotFoundException - cuttable
NoSuchMethodError - cuttable
Unable to construct
Skipping BlockEntity with id CuttableTE
```

## Co zrobić gdy znajdziesz błąd?

1. Zapisz linię z błędem
2. Sprawdź plik `.java` wskazany w stack trace
3. Popraw kod
4. Wróć do kroku 1 (pętla)

## Architektura pętli

```
┌─────────────────────────────────────────┐
│  1. Zbuduj moda (gradle build)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Deploy (kopiuj do mods\)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Uruchom launcher (pywinauto)        │
│     • Dialog aktualizacji (Cancel)      │
│     • Kliknij Play                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Monitoruj logi (60s)                │
│     • Szukaj błędów "cuttable"          │
│     • Detekcja crashy                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  5. Raport                              │
│     • Błędy krytyczne?                  │
│     • Mod załadowany?                   │
└─────────────────────────────────────────┘
```

## Troubleshooting

### "Pywinauto nie działa"
Zainstaluj: `pip install pywinauto`

### "Nie znaleziono okna launchera"
Sprawdź ścieżkę w skrypcie:
```python
LAUNCHER_PATH = r"F:\Users\pawel\Downloads\ShiginimaSE_v3100\Windows\Shiginima Launcher SE v3.100.exe"
```

### "Gradle build failed"
Sprawdź czy masz JDK 8:
```powershell
$env:JAVA_HOME = "C:\Program Files (x86)\Java\jdk1.8.0_202"
```

### "Brak uprawnień do zapisu w mods\"
Uruchom PowerShell jako Administrator.
