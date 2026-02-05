@echo off
setlocal enabledelayedexpansion

REM Użyj JRE 8 i JDK 17 (kompilator z 17, runtime z 8)
set JRE8=C:\Program Files\Java\jre1.8.0_481
set JDK17=C:\Program Files\Java\jdk-21

set JAVA_HOME=%JDK17%
set PATH=%JAVA_HOME%\bin;%PATH%

cd /d "%~dp0"

echo === Kompilacja CuttableBlocks ===
echo JDK 17 (kompilator) + JRE 8 (runtime)
echo.

REM Przygotuj katalogi
if not exist "build\classes" mkdir "build\classes"
if not exist "build\libs" mkdir "build\libs"

REM Classpath z Forge
set CP=..\headless_server\1.7.10\forge-1.7.10-10.13.4.1614-1.7.10-universal.jar
set CP=!CP!;..\headless_server\1.7.10\minecraft_server.1.7.10.jar
set CP=!CP!;..\headless_server\1.7.10\libraries\net\minecraft\launchwrapper\1.12\launchwrapper-1.12.jar
set CP=!CP!;..\headless_server\1.7.10\libraries\org\ow2\asm\asm-all\5.0.3\asm-all-5.0.3.jar

echo Kompilowanie...

REM Znajdź wszystkie pliki Java
dir /s /b src\main\java\*.java > build\sources.txt 2>nul

REM Kompiluj z target 1.8
javac -cp "!CP!" -d build\classes -source 8 -target 8 -encoding UTF8 @build\sources.txt
if errorlevel 1 (
    echo Blad kompilacji!
    exit /b 1
)

echo Kompilacja OK!
echo.

REM Skopiuj zasoby
echo Kopiowanie zasobow...
xcopy /s /y src\main\resources\* build\classes\ >nul 2>&1

REM Utworz mcmod.info
echo Tworzenie mcmod.info...
(
echo [{
echo   "modid": "cuttableblocks",
echo   "name": "Cuttable Blocks",
echo   "description": "Cut blocks at any angle",
echo   "version": "1.0.0",
echo   "mcversion": "1.7.10"
echo }]
) > build\classes\mcmod.info

REM Utworz manifest
if not exist "build\classes\META-INF" mkdir "build\classes\META-INF"
(
echo Manifest-Version: 1.0
echo FMLCorePlugin: com.cuttableblocks.asm.CuttableBlocksLoadingPlugin
echo FMLCorePluginContainsFMLMod: true
echo.
) > build\classes\META-INF\MANIFEST.MF

REM Spakuj JAR
echo Tworzenie JAR...
cd build\classes
jar cvfm ..\libs\CuttableBlocks-1.0.0.jar META-INF\MANIFEST.MF . >nul
cd ..\..

if exist "build\libs\CuttableBlocks-1.0.0.jar" (
    echo.
    echo === SUKCES ===
    echo JAR: build\libs\CuttableBlocks-1.0.0.jar
    for %%F in (build\libs\CuttableBlocks-1.0.0.jar) do echo Rozmiar: %%~zF bajtow
    
    REM Kopiuj do serwera
    if not exist "..\headless_server\1.7.10\mods" mkdir "..\headless_server\1.7.10\mods"
    copy /y "build\libs\CuttableBlocks-1.0.0.jar" "..\headless_server\1.7.10\mods\" >nul
    echo Skopiowano do serwera!
) else (
    echo BLAD: JAR nie powstal!
)

pause
