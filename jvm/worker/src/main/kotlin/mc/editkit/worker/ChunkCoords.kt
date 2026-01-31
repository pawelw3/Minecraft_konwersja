package mc.editkit.worker

import java.lang.Math

/**
 * Typy koordynatów chunków dla bezpieczeństwa typów
 * Rozróżniają globalne koordynaty (świat) od lokalnych (w regionie)
 */

/**
 * Globalne koordynaty chunka w świecie Minecraft
 * Zakres: (-∞, +∞)
 * Przykład: chunk (-1, -1) to chunk na północny-zachód od (0,0)
 */
data class GlobalChunkCoord(val x: Int, val z: Int) {
    fun toRegionCoord(): RegionCoord = RegionCoord(
        Math.floorDiv(x, 32),
        Math.floorDiv(z, 32)
    )
    
    fun toLocalCoord(): LocalChunkCoord = LocalChunkCoord(
        Math.floorMod(x, 32),
        Math.floorMod(z, 32)
    )
    
    fun toBlockCoord(): BlockCoord = BlockCoord(x * 16, z * 16)
    
    override fun toString(): String = "GlobalChunk($x, $z)"
}

/**
 * Lokalne koordynaty chunka wewnątrz regionu (0-31)
 * Używane do indeksowania w tablicach i do debug printów
 */
data class LocalChunkCoord(val x: Int, val z: Int) {
    init {
        require(x in 0..31) { "LocalChunkCoord.x must be in 0..31, got $x" }
        require(z in 0..31) { "LocalChunkCoord.z must be in 0..31, got $z" }
    }
    
    override fun toString(): String = "LocalChunk($x, $z)"
}

/**
 * Koordynaty regionu
 * Zakres: (-∞, +∞)
 * Plik regionu: r.{regionX}.{regionZ}.mca
 */
data class RegionCoord(val x: Int, val z: Int) {
    fun toGlobalChunk(local: LocalChunkCoord): GlobalChunkCoord = GlobalChunkCoord(
        x * 32 + local.x,
        z * 32 + local.z
    )
    
    fun fileName(): String = "r.${x}.${z}.mca"
    
    override fun toString(): String = "Region($x, $z)"
}

/**
 * Koordynaty bloka w świecie
 */
data class BlockCoord(val x: Int, val z: Int) {
    fun toGlobalChunk(): GlobalChunkCoord = GlobalChunkCoord(
        Math.floorDiv(x, 16),
        Math.floorDiv(z, 16)
    )
    
    fun toLocalBlock(): LocalBlockCoord = LocalBlockCoord(
        Math.floorMod(x, 16),
        Math.floorMod(z, 16)
    )
    
    override fun toString(): String = "Block($x, $z)"
}

/**
 * Lokalne koordynaty bloka w chunku (0-15)
 */
data class LocalBlockCoord(val x: Int, val z: Int) {
    init {
        require(x in 0..15) { "LocalBlockCoord.x must be in 0..15, got $x" }
        require(z in 0..15) { "LocalBlockCoord.z must be in 0..15, got $z" }
    }
    
    override fun toString(): String = "LocalBlock($x, $z)"
}

// Funkcje pomocnicze dla Hephaistos API

/**
 * Konwertuje globalne koordynaty chunka na format używany przez Hephaistos API.
 * Hephaistos RegionFile.getChunk/getChunkData oczekuje GLOBALNYCH koordynatów!
 */
fun GlobalChunkCoord.toHephaistosParams(): Pair<Int, Int> = Pair(x, z)

/**
 * Logowanie mapowania dla debugowania
 */
fun logChunkMapping(global: GlobalChunkCoord): String {
    val region = global.toRegionCoord()
    val local = global.toLocalCoord()
    return "${global} -> ${region} + ${local}"
}

/**
 * Przykłady mapowania:
 * Global(0, 0) -> Region(0, 0) + Local(0, 0)
 * Global(31, 31) -> Region(0, 0) + Local(31, 31)
 * Global(32, 0) -> Region(1, 0) + Local(0, 0)
 * Global(-1, -1) -> Region(-1, -1) + Local(31, 31)
 * Global(-32, 0) -> Region(-1, 0) + Local(0, 0)
 */
