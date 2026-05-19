# Analiza funkcjonalnosci modow 1.7.10 - czesc 4

Data: 2026-05-18  
Zakres: `docs/mod_mapping_indepth/from/mod_funkcjonalnosci_1.7.10_cz4.md` + `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz4.md`  
Arkusz zbiorczy: `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`

## Najwazniejsze korekty

1. **MrCrayfish Furniture ma port 1.18.2 i powinien byc pierwszym celem.**  
   Stary `cz4` sugeruje Macaw/Another/Decocraft jako glowne zamienniki. To jest gorsze niz uzycie `MrCrayfish Furniture Mod 7.0.0-pre35` dla 1.18.2. Zamienniki traktowac tylko jako fallback dla brakujacych blokow.

2. **Placeable Items nie wolno ignorowac.**  
   Mod ma wersje 1.18.2 (`placeableitems-4.7.1.jar`) i zostawia trwale obiekty/TE. Na mapie znaleziono tylko 5 TE, ale klasyfikacja “ignoruj” jest bledna.

3. **Railcraft Reborn nie jest obecnie pewnym celem dla twardego targetu 1.18.2.**  
   Aktualne CurseForge pokazuje Railcraft Reborn dla 1.20.1/1.21.x, a lokalne repo `mod_src/118/actual_src/1.18.2/RailcraftReborn` ma `minecraft_version=1.21.1`. Dla strict 1.18.2 najlepszy praktyczny kierunek to `Create + Steam'n'Rails`/`Little Logistics` + `Immersive Engineering`/`Mekanism`/`Thermal` per funkcja. Jesli wersja docelowa zostanie zmieniona na 1.20.1/1.21, wtedy Railcraft Reborn wraca jako najlepszy cel.

4. **ProjectRed ma realne pliki 1.18.2, ale lokalne repo jest nowsze.**  
   CurseForge pokazuje `ProjectRed-1.18.2-4.17.0-beta-4`, wiec dla celu 1.18.2 to nadal najlepszy target. Lokalny checkout jest jednak `mc_version=1.21.1`, wiec przy implementacji trzeba pobrac/weryfikowac konkretnie jar/source 1.18.2, nie opierac sie bezkrytycznie na lokalnym repo.

5. **PowerConverters najczesciej mozna usunac po przejsciu na FE.**  
   Na mapie znaleziono tylko 21 TE. Po remapie IC2/BuildCraft do Mekanism/Thermal/FE mostki energii staja sie zwykle zbedne.

## Kontekst mapy 5GB

Wykonano celowany skan `TileEntity.id` po `1195` regionach. Skan przeczytal `665995` chunkow z danymi i `2447396` tile entities. Jeden chunk w `r.-10.2.mca` zwrocil blad dekompresji (`incomplete or truncated stream`).

| Mod / grupa | Dopasowania TE | Najwazniejsze ID |
|---|---:|---|
| Railcraft | 85818 | `tileTCRailGag` 32600, `RCHiddenTile` 22283, `tileTCRail` 18088, `RCSteelTankWallTile` 5867 |
| ProjectRed | 17761 | `lamp` 8818, `lily` 8706, `barrel` 130 |
| MrCrayfish Furniture | 14313 | `TableTile` 5180, `seatTile` 2155, `cfmCabinetKitchen` 1562 |
| Open Modular Turrets | 2158 | `laserTurret` 1067, `turretBaseFour` 909 |
| Pam's HarvestCraft | 170 | `PamOven` 91, `PamFishTrap` 43 |
| PowerConverters | 21 | `EnergyBridge/RFConsumer/IC2Producer` po 7 |
| Placeable Items | 5 | `fishBlockPlaceable` 4, `placeableEnderPearlBlock` 1 |

Ograniczenie: to skan TE, nie pelny skan blokow. Nie obejmuje zwyklych crops/gardens/fruit trees Pam, itemow w inventory, minecart entities, ani partow ProjectRed schowanych w `savedMultipart` z czesci 3.

## Decyzje per mod

| Mod 1.7.10 | Najlepszy cel 1.18.2 | Ocena planu |
|---|---|---|
| MrCrayfish Furniture | MrCrayfish Furniture Mod 7.0.0-pre35 | Plan z samymi zamiennikami jest nieaktualny; port 1.18.2 istnieje |
| MrTJPCore | dependency only | Ignorowac jako content |
| NoMoreRecipeConflict | Polymorph | Poprawne jako QoL, bez konwersji mapy |
| NEI | JEI | Poprawne jako QoL |
| Open Modular Turrets | K-Turrets + ewentualnie Immersive Engineering | K-Turrets jest blizszy OMT niz same IE turrets |
| Opis | spark + Observable | Poprawne jako narzedzie admina |
| Pam's HarvestCraft | Pam's HC2 + Farmer's Delight/Croptopia fallback | PHC2 jest rebootem, nie bezstratnym portem |
| Placeable Items | Placeable Items 4.7.1 | Nie ignorowac; mapowac TE/postawione itemy |
| PowerConverters | FE native, usunac lub zastapic kablami/storage | RF Converter raczej niepotrzebny w tej paczce |
| ProjectRed | ProjectRed 1.18.2 beta + CB Multipart | Dobry target, ale wymaga konkretnej wersji 1.18.2 i konwertera multipart |
| Railcraft | Strict 1.18.2: Create/Steam'n'Rails/Little Logistics + IE/Mekanism/Thermal; po zmianie targetu: Railcraft Reborn | Stary plan “brak portu” byl uproszczeniem, ale “Railcraft Reborn na 1.18.2” tez nie jest teraz pewne |
| Rei's Minimap | JourneyMap albo Xaero's Minimap | QoL, brak konwersji chunkow |

## Priorytet implementacji

1. **Railcraft**: najwiekszy temat cz4 (`85818` TE), ale dla 1.18.2 trzeba najpierw podjac decyzje: strict fallback czy zmiana wersji docelowej pod Railcraft Reborn.
2. **ProjectRed + CB Multipart**: trzeba laczyc z konwerterem `savedMultipart` z czesci 3; same TE ProjectRed to tylko czesc obrazu.
3. **MrCrayfish Furniture**: uzyc portu 1.18.2 i zrobic ratunek inventory dla fridge/cabinets/mailbox.
4. **Open Modular Turrets**: K-Turrets jako glowny target; ammo/upgrades/target list jako raport/loot.
5. **Pam's HarvestCraft**: osobny skan blokow upraw/drzew i inventory itemow, bo TE scan pokazuje tylko 170 maszyn.
6. **Placeable Items**: mala liczba, ale wymaga mapowania TE, nie ignorowania.
7. **PowerConverters**: niski priorytet, najpewniej zastapic FE-infrastrukturą albo usunac z raportem.

## Zrodla zewnetrzne sprawdzone

- MrCrayfish Furniture: https://www.curseforge.com/minecraft/mc-mods/mrcrayfish-furniture-mod/files
- Project Red Core: https://www.curseforge.com/minecraft/mc-mods/project-red-core/description
- Project Red Transmission 1.18.2: https://files.xmdhs.com/curseforge/history?id=478939&ver=1.18.2
- Railcraft Reborn: https://www.curseforge.com/minecraft/mc-mods/railcraft-reborn
- K-Turrets: https://files.xmdhs.com/curseforge/info?id=536437
- Placeable Items 1.18.2: https://files.xmdhs.com/curseforge/history?id=227951&ver=1.18.2
- Pam's HarvestCraft 2 Food Core 1.18.2: https://files.xmdhs.com/curseforge/history?id=372534&ver=1.18.2
- spark: https://www.curseforge.com/minecraft/mc-mods/spark/files?version=1.18.2
