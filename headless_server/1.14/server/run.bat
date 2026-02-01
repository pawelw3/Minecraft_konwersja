@echo off
echo Starting Minecraft 1.14.4 Server for map migration...
cd /d "%~dp0"
java -Xmx2G -Xms1G -jar server.jar nogui
