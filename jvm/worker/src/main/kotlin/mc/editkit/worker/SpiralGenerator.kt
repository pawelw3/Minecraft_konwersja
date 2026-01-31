package mc.editkit.worker

import org.json.JSONArray
import org.json.JSONObject

/**
 * Generator spiral redstone dla testów
 */

/**
 * Generuje prostą spiralę redstone z command blockami
 * @param centerX Środek spirali X
 * @param centerY Poziom Y (wysokość na której budujemy)
 * @param centerZ Środek spirali Z
 * @param radius Promień spirali (w chunkach)
 * @param stepDistance Odległość między command blockami
 */
fun generateSpiral(
    centerX: Int,
    centerY: Int,
    centerZ: Int,
    radius: Int,
    stepDistance: Int = 16
): List<SpiralPoint> {
    val points = mutableListOf<SpiralPoint>()
    
    // Kierunki: +X, +Z, -X, -Z (prawo, dół, lewo, góra)
    val directions = listOf(
        Pair(1, 0),   // +X (E)
        Pair(0, 1),   // +Z (S)
        Pair(-1, 0),  // -X (W)
        Pair(0, -1)   // -Z (N)
    )
    
    var currentX = centerX
    var currentZ = centerZ
    var dirIndex = 0
    var stepCount = 1
    var stepsInCurrentLeg = 0
    var legCount = 0
    var stepNumber = 0
    
    // Punkt startowy (środek)
    points.add(SpiralPoint(currentX, centerY, currentZ, stepNumber, true))
    
    // Generuj spiralę
    while (kotlin.math.max(kotlin.math.abs(currentX - centerX), kotlin.math.abs(currentZ - centerZ)) < radius * 16) {
        val dir = directions[dirIndex % 4]
        
        // Przesuń się o 1 blok
        currentX += dir.first
        currentZ += dir.second
        stepsInCurrentLeg++
        
        // Sprawdź czy to punkt na spirali (co stepDistance bloków)
        val isCheckpoint = (points.size % stepDistance == 0)
        
        stepNumber++
        points.add(SpiralPoint(currentX, centerY, currentZ, stepNumber, isCheckpoint))
        
        // Zmień kierunek po zakończeniu nogi
        if (stepsInCurrentLeg >= stepCount) {
            stepsInCurrentLeg = 0
            dirIndex++
            legCount++
            
            // Co druga noga zwiększamy długość
            if (legCount % 2 == 0) {
                stepCount++
            }
        }
    }
    
    return points
}

/**
 * Konwertuje spiralę na patch JSON
 */
fun spiralToPatch(points: List<SpiralPoint>): JSONObject {
    val edits = JSONArray()
    
    for (i in points.indices) {
        val point = points[i]
        
        // Ustaw blok pod redstone (stone)
        edits.put(JSONObject().apply {
            put("op", "set_block")
            put("x", point.x)
            put("y", point.y)
            put("z", point.z)
            put("id", 1) // stone
            put("meta", 0)
        })
        
        // Ustaw redstone wire na górze
        edits.put(JSONObject().apply {
            put("op", "set_block")
            put("x", point.x)
            put("y", point.y + 1)
            put("z", point.z)
            put("id", 55) // redstone wire
            put("meta", 15) // pełna moc
        })
        
        // Jeśli to checkpoint - ustaw command block
        if (point.isCheckpoint) {
            // Blok pod command blockiem
            edits.put(JSONObject().apply {
                put("op", "set_block")
                put("x", point.x)
                put("y", point.y + 2)
                put("z", point.z)
                put("id", 1) // stone
                put("meta", 0)
            })
            
            // Command block (impulse, facing up)
            edits.put(JSONObject().apply {
                put("op", "set_block")
                put("x", point.x)
                put("y", point.y + 3)
                put("z", point.z)
                put("id", 137) // command block
                put("meta", 1) // facing up
            })
            
            // Tile Entity dla command blocka
            val chunkX = point.x shr 4
            val chunkZ = point.z shr 4
            edits.put(JSONObject().apply {
                put("op", "set_te")
                put("x", point.x)
                put("y", point.y + 3)
                put("z", point.z)
                put("nbt", JSONObject().apply {
                    put("id", "Control")
                    put("Command", "/say [PROBE] REACHED cx=${chunkX} cz=${chunkZ} step=${point.step}")
                })
            })
            
            // Dodaj redstone block obok command blocka aby go aktywować (zasilanie)
            // Umieśćmy go na pozycji x+1, y+3, z (obok command blocka)
            edits.put(JSONObject().apply {
                put("op", "set_block")
                put("x", point.x + 1)
                put("y", point.y + 3)
                put("z", point.z)
                put("id", 152) // redstone block
                put("meta", 0)
            })
        }
    }
    
    // Dodaj startowy redstone block przy pierwszym segmencie (aby aktywować spiralę)
    if (points.isNotEmpty()) {
        val first = points.first()
        edits.put(JSONObject().apply {
            put("op", "set_block")
            put("x", first.x)
            put("y", first.y + 2)
            put("z", first.z)
            put("id", 152) // redstone block (zasilanie)
            put("meta", 0)
        })
    }
    
    return JSONObject().put("edits", edits)
}

/**
 * Generuje prosty multi-chunk test (4 bloki w różnych chunkach)
 */
fun generateMultiChunkTest(centerX: Int, y: Int, centerZ: Int): JSONObject {
    val edits = JSONArray()
    
    // 4 bloki w czterech chunkach wokół spawna
    val positions = listOf(
        Triple(centerX, y, centerZ),           // chunk (0,0)
        Triple(centerX + 16, y, centerZ),      // chunk (1,0)
        Triple(centerX, y, centerZ + 16),      // chunk (0,1)
        Triple(centerX + 16, y, centerZ + 16)  // chunk (1,1)
    )
    
    for ((x, py, z) in positions) {
        // Stone pod
        edits.put(JSONObject().apply {
            put("op", "set_block")
            put("x", x)
            put("y", py)
            put("z", z)
            put("id", 1)
            put("meta", 0)
        })
        
        // Command block na górze
        edits.put(JSONObject().apply {
            put("op", "set_block")
            put("x", x)
            put("y", py + 1)
            put("z", z)
            put("id", 137)
            put("meta", 0)
        })
        
        val chunkX = x shr 4
        val chunkZ = z shr 4
        edits.put(JSONObject().apply {
            put("op", "set_te")
            put("x", x)
            put("y", py + 1)
            put("z", z)
            put("nbt", JSONObject().apply {
                put("id", "Control")
                put("Command", "/say [MULTI] cx=${chunkX} cz=${chunkZ}")
            })
        })
    }
    
    return JSONObject().put("edits", edits)
}

data class SpiralPoint(
    val x: Int,
    val y: Int,
    val z: Int,
    val step: Int,
    val isCheckpoint: Boolean
)

fun main(args: Array<String>) {
    when (args.getOrNull(0)) {
        "multichunk" -> {
            val patch = generateMultiChunkTest(0, 64, 0)
            println(patch.toString(2))
        }
        "spiral-r1" -> {
            val spiral = generateSpiral(0, 64, 0, radius = 1)
            val patch = spiralToPatch(spiral)
            println(patch.toString(2))
            println("\n// Generated ${spiral.size} points, ${spiral.count { it.isCheckpoint }} checkpoints")
        }
        "spiral-r3" -> {
            val spiral = generateSpiral(0, 64, 0, radius = 3)
            val patch = spiralToPatch(spiral)
            println(patch.toString(2))
            println("\n// Generated ${spiral.size} points, ${spiral.count { it.isCheckpoint }} checkpoints")
        }
        else -> {
            println("Usage: SpiralGenerator <multichunk|spiral-r1|spiral-r3>")
        }
    }
}
