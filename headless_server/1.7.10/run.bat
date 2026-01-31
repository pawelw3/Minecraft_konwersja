@echo off
REM Minecraft 1.7.10 Forge Server - Windows
REM Wymaga Java 8! (NIE Java 17 ani 21)

set JAVA_HOME=C:\Program Files (x86)\Common Files\Oracle\Java\java8path
set JAVA_OPTS=-Xms2G -Xmx4G -XX:+UseG1GC -XX:MaxGCPauseMillis=200
set SERVER_JAR=forge-1.7.10-10.13.4.1614-1.7.10-universal.jar

echo Starting Minecraft 1.7.10 Server...
echo Java: %JAVA_HOME%\java.exe
echo Java Options: %JAVA_OPTS%
echo Server Jar: %SERVER_JAR%
echo.

"%JAVA_HOME%\java.exe" %JAVA_OPTS% -jar %SERVER_JAR% nogui

pause
