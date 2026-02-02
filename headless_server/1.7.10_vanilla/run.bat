@echo off
REM Minecraft 1.7.10 Vanilla Server
REM Wymaga Java 8!

set JAVA_HOME=C:\Program Files (x86)\Common Files\Oracle\Java\java8path
set JAVA_OPTS=-Xms2G -Xmx4G -XX:+UseG1GC -XX:MaxGCPauseMillis=200
set SERVER_JAR=minecraft_server.1.7.10.jar

echo Starting Minecraft 1.7.10 Vanilla Server...
echo Java: %JAVA_HOME%\java.exe
echo Java Options: %JAVA_OPTS%
echo Server Jar: %SERVER_JAR%
echo.

"%JAVA_HOME%\java.exe" %JAVA_OPTS% -jar %SERVER_JAR% nogui

pause
