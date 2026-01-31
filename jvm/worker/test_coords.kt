fun testCoords() {
    println(\"Testowanie funkcji koordynatów:\")
    
    // Chunk (0, -1) -> Region (0, -1), Local (0, 31)
    val chunkX1 = 0
    val chunkZ1 = -1
    val regionX1 = java.lang.Math.floorDiv(chunkX1, 32)
    val regionZ1 = java.lang.Math.floorDiv(chunkZ1, 32)
    val localX1 = java.lang.Math.floorMod(chunkX1, 32)
    val localZ1 = java.lang.Math.floorMod(chunkZ1, 32)
    println(\"Chunk (0, -1) -> Region (\, \), Local (\, \)\")
    
    // Chunk (-1, 0) -> Region (-1, 0), Local (31, 0)
    val chunkX2 = -1
    val chunkZ2 = 0
    val regionX2 = java.lang.Math.floorDiv(chunkX2, 32)
    val regionZ2 = java.lang.Math.floorDiv(chunkZ2, 32)
    val localX2 = java.lang.Math.floorMod(chunkX2, 32)
    val localZ2 = java.lang.Math.floorMod(chunkZ2, 32)
    println(\"Chunk (-1, 0) -> Region (\, \), Local (\, \)\")
    
    // Chunk (-1, -1) -> Region (-1, -1), Local (31, 31)
    val chunkX3 = -1
    val chunkZ3 = -1
    val regionX3 = java.lang.Math.floorDiv(chunkX3, 32)
    val regionZ3 = java.lang.Math.floorDiv(chunkZ3, 32)
    val localX3 = java.lang.Math.floorMod(chunkX3, 32)
    val localZ3 = java.lang.Math.floorMod(chunkZ3, 32)
    println(\"Chunk (-1, -1) -> Region (\, \), Local (\, \)\")
}

testCoords()
