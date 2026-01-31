package mc.editkit.worker

import java.lang.Math

/**
 * Poprawne funkcje konwersji koordynatów dla Minecraft 1.7.10
 * Używa Math.floorDiv i Math.floorMod - odporne na wartości ujemne
 * 
 * Problem: Ręczne wzory typu (chunkX + 1) shr 5 - 1 nie działają poprawnie dla chunków ujemnych
 * Rozwiązanie: Użycie floorDiv/floorMod zamiast bitowych operacji przesunięcia
 */

/**
 * Konwertuje koordynat chunka (globalny) na koordynat regionu
 * Dla chunkX = -1 zwraca regionX = -1 (a nie 0!)
 * Dla chunkX = 0 zwraca regionX = 0
 * Dla chunkX = 31 zwraca regionX = 0
 * Dla chunkX = 32 zwraca regionX = 1
 */
fun regionCoordFromChunk(c: Int): Int = Math.floorDiv(c, 32)

/**
 * Konwertuje koordynat chunka (globalny) na lokalny koordynat w regionie (0-31)
 * Dla chunkX = -1 zwraca localChunkX = 31
 * Dla chunkX = 0 zwraca localChunkX = 0
 * Dla chunkX = 31 zwraca localChunkX = 31
 * Dla chunkX = 32 zwraca localChunkX = 0
 */
fun localChunkFromChunk(c: Int): Int = Math.floorMod(c, 32)

/**
 * Konwertuje koordynat bloka (światowy) na koordynat chunka
 */
fun chunkCoordFromBlock(b: Int): Int = Math.floorDiv(b, 16)

/**
 * Konwertuje koordynat bloka (światowy) na lokalny koordynat w chunku (0-15)
 */
fun localBlockFromWorld(b: Int): Int = Math.floorMod(b, 16)

/**
 * Kompletne mapowanie: blok → chunk → region
 * Zwraca: Triple(regionX, regionZ, localChunkX, localChunkZ)
 */
fun mapBlockToRegionAndLocalChunk(worldX: Int, worldZ: Int): RegionMapping {
    val chunkX = chunkCoordFromBlock(worldX)
    val chunkZ = chunkCoordFromBlock(worldZ)
    
    return RegionMapping(
        regionX = regionCoordFromChunk(chunkX),
        regionZ = regionCoordFromChunk(chunkZ),
        localChunkX = localChunkFromChunk(chunkX),
        localChunkZ = localChunkFromChunk(chunkZ),
        chunkX = chunkX,
        chunkZ = chunkZ,
        localBlockX = localBlockFromWorld(worldX),
        localBlockZ = localBlockFromWorld(worldZ)
    )
}

/**
 * Dane mapowania koordynatów
 */
data class RegionMapping(
    val regionX: Int,
    val regionZ: Int,
    val localChunkX: Int,
    val localChunkZ: Int,
    val chunkX: Int,
    val chunkZ: Int,
    val localBlockX: Int,
    val localBlockZ: Int
) {
    fun regionFileName(): String = "r.${regionX}.${regionZ}.mca"
    
    override fun toString(): String = 
        "Block($chunkX*16+$localBlockX, $chunkZ*16+$localBlockZ) → " +
        "Chunk($chunkX, $chunkZ) → " +
        "Region(${regionFileName()}) local($localChunkX, $localChunkZ)"
}

/**
 * Kompletne mapowanie: chunk → region
 */
fun mapChunkToRegionAndLocalChunk(chunkX: Int, chunkZ: Int): RegionMapping {
    return RegionMapping(
        regionX = regionCoordFromChunk(chunkX),
        regionZ = regionCoordFromChunk(chunkZ),
        localChunkX = localChunkFromChunk(chunkX),
        localChunkZ = localChunkFromChunk(chunkZ),
        chunkX = chunkX,
        chunkZ = chunkZ,
        localBlockX = 0,
        localBlockZ = 0
    )
}
