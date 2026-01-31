package mc.editkit.worker

import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.NBTCompound
import java.io.RandomAccessFile
import java.nio.file.Paths

/**
 * Weryfikator spirali - sprawdza czy command blocki zostały poprawnie zapisane
 */
fun verifySpiral(worldPath: String, expectedCheckpoints: Int) {
    println("\nWeryfikacja spirali")
    println("=" * 50)
    
    val regionPath = Paths.get(worldPath, "region")
    if (!regionPath.toFile().exists()) {
        println("❌ FAIL: Brak katalogu region")
        return
    }
    
    val regionFiles = regionPath.toFile().listFiles { f -> f.name.endsWith(".mca") }
    if (regionFiles.isNullOrEmpty()) {
        println("❌ FAIL: Brak plików region")
        return
    }
    
    var totalCommandBlocks = 0
    var totalRedstone = 0
    var foundProbeCommands = 0
    
    for (regionFile in regionFiles.sortedBy { it.name }) {
        var raf: RandomAccessFile? = null
        try {
            raf = RandomAccessFile(regionFile, "r")
            val parts = regionFile.name.removePrefix("r.").removeSuffix(".mca").split(".")
            val regionX = parts[0].toInt()
            val regionZ = parts[1].toInt()
            
            val region = RegionFile(raf, regionX, regionZ, 0, 255)
            
            // Przeszukaj wszystkie chunki w regionie
            val chunkStartX = regionX * 32
            val chunkStartZ = regionZ * 32
            
            for (lz in 0..31) {
                for (lx in 0..31) {
                    val globalCx = chunkStartX + lx
                    val globalCz = chunkStartZ + lz
                    
                    if (!region.hasChunk(globalCx, globalCz)) continue
                    
                    val chunkData = region.getChunkData(globalCx, globalCz) ?: continue
                    val level = chunkData.getCompound("Level") ?: continue
                    
                    // Sprawdź Tile Entities (command blocki)
                    val tileEntities = level.getList<NBTCompound>("TileEntities") ?: continue
                    
                    for (i in 0 until tileEntities.size) {
                        val te = tileEntities[i]
                        val id = te.getString("id") ?: continue
                        
                        if (id == "Control") {
                            totalCommandBlocks++
                            val command = te.getString("Command") ?: ""
                            if ("[PROBE]" in command) {
                                foundProbeCommands++
                            }
                        }
                    }
                }
            }
            
            raf.close()
        } catch (e: Exception) {
            println("Błąd w regionie ${regionFile.name}: ${e.message}")
        } finally {
            try { raf?.close() } catch (_: Exception) {}
        }
    }
    
    println("Znaleziono:")
    println("  - Command blocks: $totalCommandBlocks")
    println("  - [PROBE] commands: $foundProbeCommands")
    println("  - Oczekiwano checkpointów: $expectedCheckpoints")
    
    if (foundProbeCommands == expectedCheckpoints) {
        println("✅ Weryfikacja PASS: Wszystkie command blocki znalezione")
    } else if (foundProbeCommands > 0) {
        println("⚠️  Weryfikacja PARTIAL: Znaleziono $foundProbeCommands/$expectedCheckpoints checkpointów")
    } else {
        println("❌ Weryfikacja FAIL: Nie znaleziono checkpointów")
    }
}
