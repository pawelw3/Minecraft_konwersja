# Handoff: CuttableBlocks 1.7.10 - MVP Carpenter's Blocks

## Podsumowanie sesji

Rozbudowano `new_mod_trial` o pierwsza wersje MVP dla Carpenter's Blocks w modzie `CuttableBlocks` 1.7.10. Istniejace wlasne funkcje `cuttable_block`, `cutting_tool`, `collapsible_block` i `collapsible_hammer` zostaly zachowane bez usuwania.

## Ukonczono

- [x] Dodano wspolny `TileEntityCoverable` z cover block/meta, facing, shape, flags i sourceCarpentersTeId.
- [x] Dodano bloki MVP: carpenter block, slope, stairs, barrier i door.
- [x] Dodano `carpenter_hammer` do ustawiania covera i przelaczania wariantow/orientacji.
- [x] Dodano renderer coverable dla pelnego bloku, slope, stairs, barrier i door.
- [x] Poprawiono `carpenter_slope` z aproksymacji schodkowej na prawdziwy klin renderowany recznie w tessellatorze.
- [x] Zweryfikowano, ze klasy istniejacych `cuttable_block` i `collapsible_block` nie zostaly bezposrednio zmienione.
- [x] Dodano testowy migrator raportujacy Carpenter MVP do `cuttableblocks:*`.
- [x] Podpieto rejestracje blokow, itemow, TE, renderera i wpisy lang.

## Nowe pliki

- `new_mod_trial/src/main/java/com/cuttableblocks/tileentities/TileEntityCoverable.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/blocks/BlockCoverable.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/blocks/BlockCoverableDoor.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/items/ItemCarpenterHammer.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/client/CoverableBlockRenderer.java`
- `new_mod_trial/migrate_carpenters_mvp.py`

## Zmodyfikowane pliki

- `new_mod_trial/src/main/java/com/cuttableblocks/blocks/ModBlocks.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/items/ModItems.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/tileentities/ModTileEntities.java`
- `new_mod_trial/src/main/java/com/cuttableblocks/client/ClientProxy.java`
- `new_mod_trial/src/main/resources/assets/cuttableblocks/lang/en_US.lang`
- `new_mod_trial/src/main/resources/assets/cuttableblocks/lang/pl_PL.lang`

## Testy

Uruchomiono:

```powershell
new_mod_trial\gradlew.bat -p new_mod_trial build --no-daemon --console=plain
python new_mod_trial\migrate_carpenters_mvp.py new_mod_trial\build\tmp\carpenters_mvp_sample.json new_mod_trial\build\tmp\carpenters_mvp_report.json
```

Wynik: build OK. Migrator: 1/2 converted, 1 unsupported dla `GarageDoor`, zgodnie z zakresem MVP. Po poprawce slope ponownie uruchomiono build Gradle: OK.

## Nastepne kroki

1. [ ] Odpalic smoke test w kliencie/serwerze 1.7.10 i sprawdzic rendering nowych blokow w swiecie.
2. [ ] Doprecyzowac realne pola NBT oryginalnego Carpenter's Blocks dla cover/shape/facing i podpiac je do migratora.
3. [ ] Rozszerzyc migrator z raportu JSON do patchera MCA dopiero po potwierdzeniu mapowania NBT na malej mapie testowej.
