#!/bin/bash
# Minecraft 1.7.10 Forge Server - Linux/Mac
# Wymaga Java 8! (NIE Java 11, 17 ani 21)

JAVA_OPTS="-Xms2G -Xmx4G -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
SERVER_JAR="forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"

# Sprawdź czy mamy Java 8
if command -v java8 &> /dev/null; then
    JAVA_CMD="java8"
elif [ -n "$JAVA8_HOME" ]; then
    JAVA_CMD="$JAVA8_HOME/bin/java"
else
    JAVA_CMD="java"
fi

echo "Starting Minecraft 1.7.10 Server..."
echo "Java: $JAVA_CMD"
echo "Java Options: $JAVA_OPTS"
echo "Server Jar: $SERVER_JAR"
echo

$JAVA_CMD $JAVA_OPTS -jar $SERVER_JAR nogui
