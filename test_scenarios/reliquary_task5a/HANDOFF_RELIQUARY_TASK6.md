# Handoff: Reliquary – Zadanie 6

## Podsumowanie sesji

Wykonano headless tick/restart verification dla `world_reliquary_task5b`. Runner uruchomił Forge 1.18.2,
wykonał funkcję datapacka `reliquary_task5b:apply`, sprawdził 14 skonwertowanych bloków, odczekał
ticki, zapisał świat, zrestartował serwer i powtórzył sprawdzenie.

## Wynik

- Status: `passed`
- Overall pass: `True`
- Tick wait: 60 s
- Apply marker found: 3×
- Critical log lines: 0

## Pliki

- `test_scenarios/reliquary_task5a/run_task6_headless_tick_restart.py`
- `test_scenarios/reliquary_task5a/reliquary_task6_headless_tick_restart_report.json`
- `test_scenarios/reliquary_task5a/RELIQUARY_TASK6_REPORT.md`
- `test_scenarios/reliquary_task5a/HANDOFF_RELIQUARY_TASK6.md`

## Następne kroki

1. [ ] Zainstalować Reliquary JAR na headless serwerze
2. [ ] Powtórzyć 5B bez fallbacków (`--overwrite`)
3. [ ] Powtórzyć Task 6 i zweryfikować rzeczywiste TE Reliquary
4. [ ] Sprawdzić kauldron NBT w grze: `liquidLevel`, `glowstoneCount`, `effects`

---

**Status:** ✅ Zadanie 6 ukończone
**Data:** 2026-05-28
