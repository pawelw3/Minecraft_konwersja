package mc.editkit.worker

import java.nio.file.Paths

/**
 * Wykrywa czy wzór bloków tworzy kwadratową spiralę
 */
fun detectSpiralPattern(worldPath: String) {
    val path = Paths.get(worldPath)
    val analyzer = RedstoneAnalyzer(path)
    
    println("=".repeat(70))
    println("ANALIZA WZORCA SPIRALI")
    println("=".repeat(70))
    
    // Pobierz wszystkie elementy redstone
    val allElements = mutableListOf<RedstoneAnalyzer.RedstoneElement>()
    for (cx in -1..1) {
        for (cz in -1..1) {
            allElements.addAll(analyzer.analyzeChunk(cx, cz))
        }
    }
    
    if (allElements.isEmpty()) {
        println("Brak elementów redstone!")
        return
    }
    
    // Grupuj po poziomach Y
    val byY = allElements.groupBy { it.y }.toSortedMap()
    
    byY.forEach { (y, elements) ->
        println("\n--- Poziom Y=$y ---")
        println("Liczba elementów: ${elements.size}")
        
        // Znajdź zakres
        val minX = elements.minOf { it.x }
        val maxX = elements.maxOf { it.x }
        val minZ = elements.minOf { it.z }
        val maxZ = elements.maxOf { it.z }
        
        println("Zakres X: $minX do $maxX (${maxX - minX + 1} bloków)")
        println("Zakres Z: $minZ do $maxZ (${maxZ - minZ + 1} bloków)")
        
        // Sprawdź czy to kwadrat
        val width = maxX - minX + 1
        val depth = maxZ - minZ + 1
        println("Wymiary: ${width}x$depth ${if (width == depth) "(KWADRAT)" else "(prostokąt)"}")
        
        // Stwórz mapę 2D
        val grid = mutableMapOf<Pair<Int, Int>, RedstoneAnalyzer.RedstoneElement>()
        elements.forEach { grid[Pair(it.x, it.z)] = it }
        
        // Sprawdź wzorzec spirali - kolejne warstwy
        println("\nMapa (X→, Z↓):")
        println("     " + (minX..maxX).joinToString("") { String.format("%2d", it % 100) })
        
        for (z in minZ..maxZ) {
            val row = StringBuilder()
            row.append(String.format("Z%2d: ", z % 100))
            for (x in minX..maxX) {
                val el = grid[Pair(x, z)]
                val c = when {
                    el == null -> " ."
                    el.blockId == 55 -> " R"  // Redstone wire
                    el.blockId == 76 -> " T"  // Torch on
                    el.blockId == 75 -> " t"  // Torch off
                    el.blockId == 93 -> " >"  // Repeater
                    el.blockId == 94 -> " >>" // Repeater on
                    else -> " ?"
                }
                row.append(c)
            }
            println(row)
        }
        
        // Sprawdź czy to spiralny wzorzec
        analyzeSpiralPattern(elements, minX, maxX, minZ, maxZ)
    }
}

private fun analyzeSpiralPattern(
    elements: List<RedstoneAnalyzer.RedstoneElement>,
    minX: Int, maxX: Int, minZ: Int, maxZ: Int
) {
    val grid = elements.associateBy { Pair(it.x, it.z) }
    val wirePositions = elements.filter { it.blockId == 55 }.map { Pair(it.x, it.z) }.toSet()
    
    println("\n--- Analiza wzorca spirali ---")
    
    // Sprawdź warstwy od zewnątrz do środka
    var layer = 0
    var foundSpiral = true
    
    while (minX + layer < maxX - layer && minZ + layer < maxZ - layer) {
        val layerMinX = minX + layer
        val layerMaxX = maxX - layer
        val layerMinZ = minZ + layer
        val layerMaxZ = maxZ - layer
        
        println("\nWarstwa $layer (X: $layerMinX-$layerMaxX, Z: $layerMinZ-$layerMaxZ):")
        
        // Sprawdź krawędzie warstwy
        val edges = mutableListOf<String>()
        
        // Górna krawędź (Z=min, X=min do max)
        val topEdge = (layerMinX..layerMaxX).map { wirePositions.contains(Pair(it, layerMinZ)) }
        val topCount = topEdge.count { it }
        edges.add("Górna: $topCount/${topEdge.size}")
        
        // Prawa krawędź (X=max, Z=min+1 do max)
        val rightEdge = ((layerMinZ+1)..layerMaxZ).map { wirePositions.contains(Pair(layerMaxX, it)) }
        val rightCount = rightEdge.count { it }
        edges.add("Prawa: $rightCount/${rightEdge.size}")
        
        // Dolna krawędź (Z=max, X=max-1 downTo min)
        val bottomEdge = ((layerMaxX-1) downTo layerMinX).map { wirePositions.contains(Pair(it, layerMaxZ)) }
        val bottomCount = bottomEdge.count { it }
        edges.add("Dolna: $bottomCount/${bottomEdge.size}")
        
        // Lewa krawędź (X=min, Z=max-1 downTo min+1)
        val leftEdge = ((layerMaxZ-1) downTo (layerMinZ+1)).map { wirePositions.contains(Pair(layerMinX, it)) }
        val leftCount = leftEdge.count { it }
        edges.add("Lewa: $leftCount/${leftEdge.size}")
        
        println("  " + edges.joinToString(" | "))
        
        // Sprawdź czy warstwa jest zamknięta (czyli ma postać kwadratu)
        val allEdges = topEdge + rightEdge + bottomEdge + leftEdge
        val filledPercent = allEdges.count { it } * 100 / allEdges.size
        println("  Wypełnienie warstwy: $filledPercent%")
        
        if (filledPercent < 50) {
            foundSpiral = false
        }
        
        layer++
        if (layer > 5) break  // Bezpieczeństwo
    }
    
    println("\n" + "=".repeat(70))
    if (foundSpiral && layer > 1) {
        println("✅ WYKRYTO WZORZEC SPIRALI KWADRATOWEJ ($layer warstw)")
    } else if (layer == 1) {
        println("⚠️  Tylko jedna warstwa - to może być prosty kwadrat/linia")
    } else {
        println("❌ Brak regularnej struktury spirali")
        println("   Elementy są rozłączne lub tworzą nieregularny wzorzec")
    }
    println("=".repeat(70))
}
