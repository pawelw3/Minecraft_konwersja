@echo off
setlocal

set JDK=C:\Program Files\Java\jdk-21
set JAVAC="%JDK%\bin\javac"
set JAR="%JDK%\bin\jar"

set SRC=src\main\java
set RES=src\main\resources
set BUILD=build\simple
set SERVER=..\headless_server\1.7.10

echo === Kompilacja CuttableBlocks ===
echo.

:: Przygotuj katalogi
if not exist "%BUILD%\classes" mkdir "%BUILD%\classes"
if not exist "%BUILD%\classes\META-INF" mkdir "%BUILD%\classes\META-INF"
if not exist "%BUILD%\libs" mkdir "%BUILD%\libs"

:: Przygotuj classpath
set CP=%SERVER%\forge-1.7.10-10.13.4.1614-1.7.10-universal.jar;%SERVER%\minecraft_server.1.7.10.jar

echo Classpath: %CP%
echo.

:: Znajdz wszystkie pliki Java
echo Szukanie plikow Java...
dir /s /b %SRC%\*.java > %BUILD%\sources.txt
set /p COUNT= < %BUILD%\sources.txt
for /f %%a in ('type %BUILD%\sources.txt ^| find /c /v ""') do set COUNT=%%a
echo Znaleziono %COUNT% plikow
echo.

:: Kompiluj
echo Kompilowanie...
%JAVAC% -cp %CP% -d %BUILD%\classes -source 8 -target 8 -encoding UTF8 @%BUILD%\sources.txt
if errorlevel 1 (
    echo Blad kompilacji!
    exit /b 1
)
echo Kompilacja OK
echo.

:: Skopiuj zasoby
echo Kopiowanie zasobow...
if exist %RES% xcopy /s /y %RES%\* %BUILD%\classes\ >nul 2>&1

:: Utworz mcmod.info
echo Tworzenie mcmod.info...
(
echo [{
echo   "modid": "cuttableblocks",
echo   "name": "Cuttable Blocks",
echo   "description": "Cut blocks at any angle",
echo   "version": "1.0.0",
echo   "mcversion": "1.7.10"
echo }]
) > %BUILD%\classes\mcmod.info

:: Utworz manifest
echo Manifest-Version: 1.0 > %BUILD%\classes\META-INF\MANIFEST.MF
echo FMLCorePlugin: com.cuttableblocks.asm.CuttableBlocksLoadingPlugin >> %BUILD%\classes\META-INF\MANIFEST.MF
echo FMLCorePluginContainsFMLMod: true >> %BUILD%\classes\META-INF\MANIFEST.MF

:: Spakuj JAR
echo Tworzenie JAR...
cd %BUILD%\classes
%JAR% cvfm ..\libs\CuttableBlocks-1.0.0.jar META-INF\MANIFEST.MF . >nul
cd ..\..

:: Sprawdz
echo.
if exist %BUILD%\libs\CuttableBlocks-1.0.0.jar (
    echo === SUKCES ===
    echo JAR: %BUILD%\libs\CuttableBlocks-1.0.0.jar
    for %%F in (%BUILD%\libs\CuttableBlocks-1.0.0.jar) do echo Rozmiar: %%~zF bajtow
    
    :: Kopiuj do serwera
    if not exist %SERVER%\mods mkdir %SERVER%\mods
    copy /y %BUILD%\libs\CuttableBlocks-1.0.0.jar %SERVER%\mods\
    echo Skopiowano do %SERVER%\mods\
) else (
    echo BLAD: JAR nie powstal!
)

:: Cleanup
del %BUILD%\sources.txt 2>nul

echo.
pause
