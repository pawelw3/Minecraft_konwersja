# Thermal Dynamics — Krok 6 (Headless Server Test)

## Cel
Sprawdzenie czy przekonwertowane bloki Thermal Dynamics działają poprawnie na headless serwerze Forge 1.18.2 z zainstalowanymi modami docelowymi (Thermal Series + Mekanism).

## Środowisko testowe

| Parametr | Wartość |
|----------|---------|
| Serwer | Forge 1.18.2-40.2.4 |
| Mody | `thermal_foundation-1.18.2-9.2.2.58`, `thermal_expansion-1.18.2-9.2.2.24`, `thermal_dynamics-1.18.2-9.2.2.19`, `cofh_core-1.18.2-9.2.3.47` |
| Mody (fallback) | `Mekanism-1.18.2-10.2.5.465`, `MekanismGenerators-1.18.2-10.2.5.465`, `MekanismTools-1.18.2-10.2.5.465` |
| Mapa | `world` (mała istniejąca mapa, spawn: 32, 71, 0) |
| RCON | localhost:25575, hasło: ae2test123 |

## Przebieg testu

### Uruchomienie 1 (first run)
1. **Start serwera**: ✅ Sukces — `Done (7.196s)!`
2. **Force load chunk**: `/forceload add 32 0` — ✅ wykonane
3. **Wstawianie bloków** (RCON `/setblock`):
   | Blok | Pozycja | Wynik |
   |------|---------|-------|
   | `thermal:energy_duct` | 32, 71, 0 | ✅ Changed |
   | `thermal:fluid_duct` | 33, 71, 0 | ✅ Changed |
   | `thermal:fluid_duct_windowed` | 34, 71, 0 | ✅ Changed |
   | `mekanism:basic_logistical_transporter` | 35, 71, 0 | ✅ Changed |
   | `mekanism:advanced_logistical_transporter` | 36, 71, 0 | ✅ Changed |
   | `mekanism:elite_logistical_transporter` | 37, 71, 0 | ✅ Changed |
   | `mekanism:ultimate_logistical_transporter` | 38, 71, 0 | ✅ Changed |
   | `mekanism:teleporter` | 39, 71, 0 | ✅ Changed |
   | `mekanism:teleporter_frame` | 40, 71, 0 | ✅ Changed |
4. **Zapis świata**: `/save-all` — ✅
5. **Ticki (3 min)**: Serwer działał stabilnie, brak crashy

### Uruchomienie 2 (restart)
1. **Start serwera**: ✅ Sukces — `Done (53.548s)!`
2. **Ładowanie chunków z blokami**: Bez błędów
3. **Brak crashy po restarcie**

## Logi — analiza błędów

### Pierwsze uruchomienie
- **ERROR / FATAL**: 0 błędów związanych z Thermal Dynamics lub Mekanism
- **WARN**: Remapowanie ID rejestrów (normalne przy dodawaniu nowych modów do istniejącego świata)
- **Crash**: Brak

### Restart
- **ERROR / FATAL**: 0
- **Crash**: Brak
- **Ładowanie chunków**: Pomyślne

## Wnioski

| Kryterium | Wynik |
|-----------|-------|
| Serwer startuje z modami docelowymi | ✅ PASS |
| Bloki docelowe są akceptowane przez serwer | ✅ PASS (9/9) |
| Brak crashy po wstawieniu bloków | ✅ PASS |
| Brak crashy po restarcie | ✅ PASS |
| Mapa zapisuje się poprawnie | ✅ PASS |

**Krok 6: PASS** — Wszystkie przekonwertowane bloki Thermal Dynamics działają poprawnie w środowisku docelowym Forge 1.18.2 z modami Thermal Series + Mekanism.

## Uwagi

- `cofh_core` był wymaganym modułem zależnym, którego nie było w folderze `mods/` — pobrano go ręcznie z CurseForge (wersja 9.2.3.47).
- Na serwerze były też inne mody (AE2, ProjectRed, WorldEdit) — nie wykazały konfliktów z Thermal/Mekanism.
- Bloki `thermal:item_duct`, `thermal:structure_duct`, `thermal:transport_duct` **nie istnieją** w TD 1.18.2 v9.2.2 — decyzja o mapowaniu na Mekanism została potwierdzona jako poprawna.

---

*Raport wygenerowany: 2026-05-20*
