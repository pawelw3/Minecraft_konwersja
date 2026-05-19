# Analiza funkcjonalnosci modow 1.7.10 - czesc 5

Data: 2026-05-18  
Zakres: `docs/mod_mapping_indepth/from/mod_funkcjonalnosci_1.7.10_cz5.md` + `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz5.md`  
Arkusz zbiorczy: `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`

## Najwazniejsze korekty

1. **Thaumcraft + addony to najwieksze ryzyko czesci 5.**  
   Skorygowany skan TE pokazal `118387` dopasowan, z czego `TileWarded` ma `84068`, `TileNode` `15843`, a `TileManaPod` `14858`. Nie ma portu Thaumcraft 4/6 na 1.18.2, wiec nie istnieje bezpieczna sciezka A->A. Najuczciwszy plan to ratunek danych + placeholdery + odbudowa funkcji w `Ars Nouveau`, `Occultism` i `Botania`.

2. **Thermal Series jest dobrym celem A->A, ale Thermal Dynamics wymaga testu.**  
   `Thermal Expansion/Foundation` sa naturalnym celem. Ducty z `Thermal Dynamics` dominuja jednak w skanie (`ItemDuct` 6518, `FluxDuctSuperConductor` 5940), a dla 1.18.2 ten modul historycznie bywal bardziej ryzykowny niz Foundation/Expansion. W arkuszu zostawilem fallback `Pipez/XNet`.

3. **Witchery nie da sie zachowac mechanicznie 1:1.**  
   Skan pokazal `5536` TE, glownie `witchery:poppetshelf` (`4076`). `Hexerei` i `Enchanted: Witchcraft` sa najlepszym kierunkiem klimatycznym na Forge 1.18.2, ale poppet bindings, rytualy i progres trzeba potraktowac jako eksport/loot/rekonstrukcje.

4. **Traincraft ma malo TE, ale wymaga skanu encji.**  
   `TileTrainWbench` wystapil `144` razy. Same pociagi/wagony/zeppeliny najpewniej sa encjami, wiec TE scan nie odpowiada na pytanie o skale utraty pojazdow.

5. **Statues nie jest potwierdzony na mapie przez TE scan.**  
   Surowy skan znalazl `witchery:statueofworship`, ale to Witchery, nie mod Statues. Dla Statues potrzebny jest osobny skan ID/itemow, choc port 1.18.2 istnieje.

## Kontekst mapy 5GB

Wykonano celowany skan `TileEntity.id` po `1195` regionach. Skan przeczytal `665995` chunkow z danymi i `2447396` tile entities. Jeden chunk w `r.-10.2.mca` zwrocil blad dekompresji (`incomplete or truncated stream`).

Po korekcie recznej:

| Mod / grupa | Dopasowania TE | Najwazniejsze ID |
|---|---:|---|
| Thaumcraft + addony | 118387 | `TileWarded` 84068, `TileNode` 15843, `TileManaPod` 14858 |
| Thermal Series | 14213 | `ItemDuct` 6518, `FluxDuctSuperConductor` 5940, `Tesseract` 128 |
| Witchery | 5536 | `poppetshelf` 4076, `coffinblock` 870, `altar` 100 |
| Reliquary | 2148 | `TileCrystal` 1726, `TileSiphon` 163, `TileVatSlave` 124 |
| Traincraft | 144 | `TileTrainWbench` 144 |
| Thaumic Energistics | 10 | providers/inscribers essentii |
| Statues | 0 pewnych TE | surowe `witchery:statueofworship` odrzucone jako Witchery |

Ograniczenie: skan nie obejmuje zwyklych blokow bez TE, encji Traincraft, itemow w inventory ani research/progress playerdata.

## Decyzje per mod

| Mod 1.7.10 | Najlepszy cel 1.18.2 | Ocena planu |
|---|---|---|
| Reliquary | Reliquary Reincarnations | Plan poprawny; potrzebny item remap i blokowy NBT best-effort |
| RadarBro | Xaero's Minimap/JourneyMap/VoxelMap | Klientowe, nie mapowac chunkow |
| Statues | Statues (ShyNieke), fallback armor stands | Port istnieje, ale brak pewnych TE na mapie |
| Thaumcraft | Ars Nouveau + Occultism + Botania | Brak A->A, wymagany ratunek danych i placeholdery |
| Thaumcraft NEI Plugin | JEI + ksiegi docelowych modow | Ignorowac jako plugin UI |
| Thaumic Energistics | AE2 + Occultism / brak essentia | Funkcja nieprzenosna bez Thaumcraft |
| Thaumic Exploration/Horizons/Tinkerer | Ars/Occultism/Botania + Enchanting Infuser dla enchanting | Rozbic po funkcjach, nie jako jeden mod |
| Thermal Foundation/Expansion/Dynamics | Thermal Series 1.18.2, fallback Pipez/XNet dla ductow | Dobry cel, ale NBT/duct filters wymagaja testow |
| Traincraft | Create + Steam'n'Rails; Eureka/VS dla sterowcow | Encje do recznej rekonstrukcji |
| uuid offline | Brak; standard UUID 1.18.2 | Nie mapowac blokow; uwaga na owner UUID w NBT innych modow |
| Witchery | Hexerei + Enchanted: Witchcraft + Occultism | Klimat tak, dane/NBT nie |
| WorldEdit | WorldEdit 7.2.x | Narzedzie, nie mapowac chunkow |

## Priorytet implementacji

1. **Thaumcraft/addony**: najpierw eksport inventory, essentia, waznych TE i research/playerdata do raportow. Bez tego podmiana blokow bedzie nieodwracalna strata.
2. **Thermal Dynamics/Expansion**: test 1.18.2 na headless, potem ducty i maszyny jako osobne konwertery NBT.
3. **Witchery**: poppet shelf i rituały jako eksport/loot + placeholdery; dekoracje osobno do Hexerei/Enchanted.
4. **Reliquary**: ten sam mod, wiec relatywnie dobry kandydat do item/block remapu.
5. **Traincraft**: osobny skan encji, bo same TE workbencha nie wystarcza.
6. **Statues**: niski priorytet, dopoki skan blokow/itemow nie potwierdzi uzycia.

## Zrodla zewnetrzne sprawdzone

- Reliquary Reincarnations 1.18.2: https://www.curseforge.com/minecraft/mc-mods/reliquary-reincarnations/files/all?page=1&pageSize=20&version=1.18.2
- Thermal Expansion 1.18.2: https://minecraftmonitoring.com/mods/thermal-expansion
- Thermal Dynamics 1.18.2: https://files.xmdhs.com/curseforge/info?id=227443
- Botania 1.18.2: https://files.xmdhs.com/curseforge/history?id=225643&ver=1.18.2
- Hexerei 1.18.2: https://www.curseforge.com/minecraft/mc-mods/hexerei/files/all?page=1&pageSize=20&version=1.18.2
- Enchanted: Witchcraft: https://www.curseforge.com/minecraft/mc-mods/enchanted-witchcraft/
- Create: Steam 'n' Rails 1.18.2: https://files.xmdhs.com/curseforge/history?id=688231&ver=1.18.2
- Eureka / Valkyrien Skies: https://wiki.valkyrienskies.org/wiki/Eureka
