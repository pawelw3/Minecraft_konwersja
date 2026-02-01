@echo off
echo Starting Minecraft Forge 1.14.4 Server for map migration...
cd /d "%~dp0\server"
java -Xmx4G -Xms2G -jar ..\forge-1.14.4-28.2.23.jar nogui
