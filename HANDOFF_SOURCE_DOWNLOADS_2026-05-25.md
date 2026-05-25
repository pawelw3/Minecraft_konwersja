# Handoff: pobranie brakujacych kodow modow

## Podsumowanie sesji
Pobrano brakujace publiczne repozytoria kodu zrodlowego modow docelowych 1.18.x do `mod_src/118/actual_src/1.18.2`. Dla Macaw's Furniture, gdzie nie znaleziono publicznego repozytorium z kodem moda, zdekompilowano lokalny JAR 1.18.2 do `mod_src/118/code_from_jar/1.18.2`.

## Ukonczono
- [x] `EnchantingInfuser` pobrany i przelaczony na branch `1.18.2`.
- [x] `SophisticatedStorage` pobrany i przelaczony na branch `1.18.x`.
- [x] `CBMultipart` pobrany i przelaczony na branch `1.18.x`.
- [x] `IntegratedDynamics` pobrany i przelaczony na branch `release-1.18`.
- [x] `MrCrayfishFurniture` pobrany i przelaczony na branch `1.18.X`.
- [x] `Handcrafted` pobrany, ale publiczne repo nie ma widocznego brancha/tagu `1.18.x`; obecnie jest to zrodlo referencyjne z brancha `1.21.x`.
- [x] `MacawsFurniture` zdekompilowany z lokalnego JAR-a `macawsfurniture-1.18.2-3.4.1.jar`.

## Nowe lokalizacje
- `mod_src/118/actual_src/1.18.2/EnchantingInfuser/repo`
- `mod_src/118/actual_src/1.18.2/Handcrafted/repo`
- `mod_src/118/actual_src/1.18.2/SophisticatedStorage/repo`
- `mod_src/118/actual_src/1.18.2/CBMultipart/repo`
- `mod_src/118/actual_src/1.18.2/IntegratedDynamics/repo`
- `mod_src/118/actual_src/1.18.2/MrCrayfishFurniture/repo`
- `mod_src/118/code_from_jar/1.18.2/MacawsFurniture/decompiled`
- `tools/cfr-0.152.jar`

## Weryfikacja
- `EnchantingInfuser`: 54 pliki zrodlowe, HEAD `8ee4293`.
- `SophisticatedStorage`: 1118 plikow zrodlowych, HEAD `891b0d9e`.
- `CBMultipart`: 211 plikow zrodlowych, HEAD `ee4de53`.
- `IntegratedDynamics`: 2333 pliki zrodlowe, HEAD `f683b8faafd`.
- `MrCrayfishFurniture`: 4190 plikow zrodlowych, HEAD `3970f18f`.
- `MacawsFurniture`: 40 zdekompilowanych plikow `.java`.

## Uwagi
- `Handcrafted` nie jest potwierdzonym kodem 1.18.2. Modrinth pokazuje kompatybilnosc od 1.19.2 wzwyz, a FTB Wiki wskazuje starsze wsparcie 1.17.2/1.18.1, nie 1.18.2.
- Repozytoria zostaly pobrane jako zagniezdzone repozytoria Git; nie modyfikowano istniejacych zmian uzytkownika w glownym repo.
