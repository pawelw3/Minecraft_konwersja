# Chisel - Zadanie 2: symulacje kontraktowe

## Podsumowanie

Wykonano symulacje zachowan nietrywialnych dla Chisel/Rechiseled:

- Chisel Auto Chisel: input/output, target, progress, energia, przenoszenie identycznego wariantu.
- Rechiseled chisel item: wybor receptury, filter stored stack, klik 3x3, shift jako pojedynczy blok, zachowanie ksztaltu stairs/slab/block.

Symulacje nie dotykaja mapy. Sa czystym Pythonem i sluza jako kontrakt dla pozniejszego konwertera eventow.

## Pliki

- `src/converters/chisel/simulations/auto_chisel_1710.py`
- `src/converters/chisel/simulations/rechiseled_1182.py`
- `src/converters/chisel/tests/test_chisel_simulations.py`

## Zrodla z kodu

### Chisel Auto Chisel

Plik zrodlowy:

`mod_src/1710/actual_src/1.7.10/Chisel/repo/base/src/main/java/team/chisel/common/block/TileAutoChisel.java`

Kluczowy kontrakt z `tick()`:

```java
private static final int MAX_PROGRESS = 1024;
private static final int BASE_PROGRESS = 16;
private static final int SPEEDUP_PROGRESS = 64;
private static final int POWER_PER_TICK = 20;
```

```java
if (energyStorage.getEnergyStored() == 0 && Configurations.autoChiselNeedsPower) {
    return;
}
```

```java
if (sourceVar != v) {
    if (progress < MAX_PROGRESS) {
        if (!Configurations.autoChiselNeedsPower) {
            progress = Math.min(MAX_PROGRESS, progress + BASE_PROGRESS);
        }
        int toUse = Math.min(MAX_PROGRESS - progress, getPowerProgressPerTick());
        int powerToUse = getUsagePerTick();
        if (toUse > 0 && powerToUse > 0) {
            if (Configurations.autoChiselPowered) {
                int used = energyStorage.extractEnergy(powerToUse, false);
                progress += toUse * ((float) used / powerToUse);
            } else {
                progress += toUse;
            }
        }
    } else {
        // craft target variation, merge output, reset progress
    }
} else {
    // same variation: move source to output without progress
}
```

Wnioski dla konwersji:

- Auto Chisel ma stan dynamiczny: `progress`, `energy`, input/output, chisel slot, target slot.
- Jesli target jest tym samym wariantem co input, maszyna tylko przenosi stack do output.
- Craft nie dzieje sie w tym samym kroku, w ktorym progress pierwszy raz osiaga `MAX_PROGRESS`; zgodnie z kodem dzieje sie przy kolejnym ticku.
- Przy wymaganej energii i pustym buforze maszyna stoi bez resetu inventory.

### Rechiseled chisel item

Plik zrodlowy:

`mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/java/com/supermartijn642/rechiseled/ChiselItem.java`

Kluczowy kontrakt z `findChiselableBlocks()`:

```java
int xRange = isShiftDown || side.getAxis() == Direction.Axis.X ? 0 : 1;
int yRange = isShiftDown || side.getAxis() == Direction.Axis.Y ? 0 : 1;
int zRange = isShiftDown || side.getAxis() == Direction.Axis.Z ? 0 : 1;
```

```java
if(targetShape != null && shape != targetShape)
    continue;
if(filterBlock != null){
    chiselableBlocks.add(Pair.of(pos.immutable(), filterBlock.withPropertiesOf(state)));
    continue;
}
```

Wnioski dla konwersji:

- Rechiseled nie ma block entity maszyny analogicznej do Auto Chisel.
- Narzedzie przechowuje filtr w NBT `stack`.
- Bez shiftu modyfikuje panel 3x3 na plaszczyznie prostopadlej do kliknietej sciany.
- Ze shiftem modyfikuje tylko klikniety blok.
- Filtr zachowuje shape: klikniecie stairs z filtrem block wybiera odpowiadajacy wariant stairs, jesli istnieje.

## Scenariusze testowe

`python -m pytest src/converters/chisel/tests/test_chisel_simulations.py -q`

Pokryte scenariusze:

- Auto Chisel konwertuje input na target po osiagnieciu progress.
- Auto Chisel przenosi identyczny wariant bez naliczania progress.
- Auto Chisel stoi przy `needs_power=True` i `energy=0`.
- Auto Chisel zuzywa energie przy powered progress.
- Rechiseled wybiera widoczne bloki z panelu 3x3.
- Rechiseled + shift ogranicza zmiane do jednego bloku.
- Rechiseled filter zachowuje shape targetu.

Wynik lokalny: `7 passed`.

## Znaczenie dla Zadania 3

Konwerter nie powinien probowac odtwarzac Auto Chisel jako Rechiseled block entity, bo Rechiseled jej nie ma. Najbezpieczniejszy kierunek:

1. Zwykle dekoracyjne bloki Chisel mapowac bezposrednio na blockstate Rechiseled/Chipped.
2. Auto Chisel przeniesc jako raportowany fallback: odzyskac input/output/target do kontenera lub placeholdera z eventem ratunkowym.
3. Dla blokow dekoracyjnych priorytetem jest podobienstwo wizualne: material, kolor, wzor, a dopiero potem nazwa.

