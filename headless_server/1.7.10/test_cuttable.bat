@echo off
echo ==========================================
echo TEST SERWERA Z CUTTABLE BLOCKS
echo ==========================================
echo.
echo Swiat: world_cuttable_test
echo 27 blokow ukoœnych wstawionych wokol spawnu
echo.
echo Nacisnij Ctrl+C aby zatrzymac serwer
echo.

REM Utworz katalog mods jesli nie istnieje
if not exist "mods" mkdir "mods"

REM Kopiuj JAR moda jesli istnieje
if exist "..\..\new_mod_trial\build\libs\CuttableBlocks-1.0.0.jar" (
    echo Kopiowanie moda CuttableBlocks...
    copy /Y "..\..\new_mod_trial\build\libs\CuttableBlocks-1.0.0.jar" "mods\" >nul 2>&1
    echo Mod skopiowany.
) else (
    echo UWAGA: Mod nie jest zbudowany!
    echo Bloki ukoœne beda widoczne jako block ID 200 (prawdopodobnie jako blad tekstury)
    echo.
    echo Aby zbudowac mod:
    echo   cd new_mod_trial
    echo   gradlew.bat build
    echo.
)

echo Uruchamianie serwera...
echo ==========================================
echo.

"C:\Program Files\Java\jre1.8.0_481\bin\java.exe" -Xmx1G -jar forge-1.7.10-10.13.4.1614-1.7.10-universal.jar nogui

echo.
echo ==========================================
echo Serwer zatrzymany
echo ==========================================
pause
