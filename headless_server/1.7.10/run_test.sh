#!/bin/bash
# Test serwera z CuttableBlocks

echo "=========================================="
echo "TEST SERWERA Z CUTTABLE BLOCKS"
echo "=========================================="
echo ""
echo "Swiat: world_cuttable_test"
echo "27 blokow ukosnych wstawionych"
echo ""

# Sprawdz czy JAR istnieje
if [ ! -f "forge-1.7.10-10.13.4.1614-1.7.10-universal.jar" ]; then
    echo "BLAD: Nie znaleziono JAR serwera"
    exit 1
fi

# Utworz katalog mods
mkdir -p mods

echo "Uruchamianie serwera na 30 sekund..."
echo ""

# Uruchom serwer w tle
timeout 30s java -Xmx1G -jar forge-1.7.10-10.13.4.1614-1.7.10-universal.jar nogui &
SERVER_PID=$!

# Czekaj na inicjalizacje
sleep 25

echo ""
echo "Sprawdzanie logow..."
echo ""

# Sprawdz logi
if [ -f "logs/latest.log" ]; then
    if grep -q "Done" logs/latest.log; then
        echo "OK: Serwer uruchomil sie poprawnie!"
    else
        echo "WARN: Serwer moze miec problemy"
    fi
    
    if grep -q "Error\|Exception" logs/latest.log; then
        echo "ERR: Znaleziono bledy:"
        grep "Error\|Exception" logs/latest.log | tail -5
    fi
fi

# Zatrzymaj serwer
echo ""
echo "Zatrzymywanie serwera..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "=========================================="
echo "TEST ZAKONCZONY"
echo "=========================================="
