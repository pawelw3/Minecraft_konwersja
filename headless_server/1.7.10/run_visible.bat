@echo off
cd /d "%~dp0"
echo Uruchamianie serwera widocznego...
java -Xmx1G -jar forge-1.7.10-10.13.4.1614-1.7.10-universal.jar nogui
pause
