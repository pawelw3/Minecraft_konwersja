# 03. Plan rozbudowy JVM Worker (Kotlin)

## Stan obecny

Istniejący worker (`jvm/worker/`) zawiera:

```
jvm/worker/src/main/kotlin/mc/editkit/worker/
├── WorldEditor.kt      ✓ setBlock(), setTileEntity() dla 1.7.10
├── Main.kt             ✓ CLI z --patch dla Patch JSON
├── EditMetadata.kt     ✓ Metadane edycji
├── Utils.kt            ✓ Funkcje pomocnicze
└── [inne pliki testowe]
```

**Ograniczenia obecnego workera:**
- Obsługuje tylko format 1.7.10
- Brak batch processing (każda operacja osobno)
- Prosty format Patch JSON (tylko `set_block`, `set_te`)
- Brak obsługi entities
- Brak walidacji eventów

## Docelowa struktura

```
jvm/worker/src/main/kotlin/mc/editkit/
├── Main.kt                           # Rozbudowany CLI
├── events/
│   ├── EventProcessor.kt             # Główny procesor eventów
│   ├── EventParser.kt                # Parser Event JSON
│   ├── EventValidator.kt             # Walidacja eventów
│   ├── EventTypes.kt                 # Typy eventów (sealed classes)
│   └── EventReport.kt                # Generowanie raportów
├── handlers/
│   ├── HandlerRegistry.kt            # Rejestr handlerów
│   ├── BlockHandler.kt               # Operacje na blokach
│   ├── BlockEntityHandler.kt         # Operacje na BlockEntity
│   ├── EntityHandler.kt              # Operacje na Entity
│   └── NbtModifyHandler.kt           # Modyfikacje NBT
├── world/
│   ├── WorldEditor1710.kt            # Edytor 1.7.10 (z obecnego WorldEditor.kt)
│   ├── WorldEditor1182.kt            # NOWY: Edytor 1.18.2
│   ├── WorldEditorInterface.kt       # Wspólny interfejs
│   ├── ChunkCache.kt                 # Cache chunków dla batch processing
│   └── RegionManager.kt              # Zarządzanie plikami .mca
├── nbt/
│   ├── NbtJsonConverter.kt           # JSON ↔ NBT konwersja
│   ├── NbtTransformer.kt             # Transformacje NBT
│   └── NbtTypeAdapter.kt             # Adaptery dla specjalnych typów
├── blockstate/
│   ├── BlockStateRegistry.kt         # Rejestr blockstate dla 1.18.2
│   ├── BlockStatePalette.kt          # Obsługa palet blockstate
│   └── BlockStateValidator.kt        # Walidacja blockstate
└── util/
    ├── Coords.kt                     # Istniejące (koordynaty)
    └── Logging.kt                    # Logowanie
```

## Szczegóły implementacji

### 1. EventTypes.kt - Definicje eventów

```kotlin
package mc.editkit.events

import org.jglrxavpok.hephaistos.nbt.NBTCompound

/**
 * Pozycja w świecie (blok)
 */
data class BlockPos(val x: Int, val y: Int, val z: Int) {
    fun toChunkPos() = ChunkPos(x shr 4, z shr 4)
    fun toRegionPos() = RegionPos(x shr 9, z shr 9)
    fun toLocalInChunk() = BlockPos(x and 15, y, z and 15)
}

/**
 * Pozycja entity (floating point)
 */
data class EntityPos(val x: Double, val y: Double, val z: Double)

data class ChunkPos(val x: Int, val z: Int)
data class RegionPos(val x: Int, val z: Int)

/**
 * Blockstate properties
 */
typealias BlockState = Map<String, String>

/**
 * Źródło eventu (do debugowania)
 */
data class EventSource(
    val mod: String,
    val blockId: String? = null,
    val teId: String? = null,
    val metadata: Int? = null,
    val reason: String? = null
)

/**
 * Sealed class dla wszystkich typów eventów
 */
sealed class ConversionEvent {
    abstract val source: EventSource?

    data class SetBlock(
        val pos: BlockPos,
        val block: String,
        val blockstate: BlockState = emptyMap(),
        override val source: EventSource? = null
    ) : ConversionEvent()

    data class SetBlockEntity(
        val pos: BlockPos,
        val block: String,
        val blockstate: BlockState = emptyMap(),
        val nbt: NBTCompound,
        override val source: EventSource? = null
    ) : ConversionEvent()

    data class RemoveBlock(
        val pos: BlockPos,
        override val source: EventSource? = null
    ) : ConversionEvent()

    data class SetEntity(
        val pos: EntityPos,
        val nbt: NBTCompound,
        override val source: EventSource? = null
    ) : ConversionEvent()

    data class RemoveEntity(
        val uuid: IntArray,
        override val source: EventSource? = null
    ) : ConversionEvent()

    data class ModifyNbt(
        val pos: BlockPos,
        val target: NbtTarget,
        val operations: List<NbtOperation>,
        override val source: EventSource? = null
    ) : ConversionEvent()
}

enum class NbtTarget { BLOCK_ENTITY, ENTITY }

data class NbtOperation(
    val path: String,
    val op: NbtOp,
    val value: Any? = null
)

enum class NbtOp { SET, REMOVE, APPEND }
```

### 2. EventProcessor.kt - Główny procesor

```kotlin
package mc.editkit.events

import mc.editkit.handlers.*
import mc.editkit.world.*
import java.nio.file.Path

/**
 * Główny procesor eventów
 */
class EventProcessor(
    private val targetWorld: WorldEditorInterface,
    private val config: ProcessorConfig = ProcessorConfig()
) {
    private val handlers = HandlerRegistry()
    private val validator = EventValidator()
    private val report = EventReport()

    data class ProcessorConfig(
        val batchSize: Int = 1000,           // Eventy na batch
        val validateEvents: Boolean = true,   // Czy walidować eventy
        val continueOnError: Boolean = true,  // Czy kontynuować po błędzie
        val dryRun: Boolean = false          // Tylko walidacja, bez zapisu
    )

    /**
     * Przetwarza plik z eventami
     */
    fun processEventFile(eventFilePath: Path): ProcessingResult {
        println("Processing events from: $eventFilePath")

        // 1. Parsuj eventy
        val eventFile = EventParser.parse(eventFilePath)
        report.setMetadata(eventFile.metadata)

        println("Loaded ${eventFile.events.size} events")

        // 2. Waliduj (opcjonalnie)
        if (config.validateEvents) {
            val validationErrors = validator.validate(eventFile.events)
            if (validationErrors.isNotEmpty()) {
                report.addValidationErrors(validationErrors)
                if (!config.continueOnError) {
                    return report.toResult(success = false)
                }
            }
        }

        // 3. Grupuj po regionach
        val byRegion = eventFile.events.groupBy { it.toRegionPos() }
        println("Events span ${byRegion.size} regions")

        // 4. Przetwarzaj region po regionie
        for ((region, regionEvents) in byRegion) {
            processRegion(region, regionEvents)
        }

        // 5. Commit (jeśli nie dry-run)
        if (!config.dryRun) {
            targetWorld.commit()
        }

        return report.toResult(success = true)
    }

    private fun processRegion(region: RegionPos, events: List<ConversionEvent>) {
        println("Processing region r.${region.x}.${region.z} (${events.size} events)")

        // Grupuj po chunkach dla lepszego cache
        val byChunk = events.groupBy { it.toChunkPos() }

        for ((chunk, chunkEvents) in byChunk) {
            for (event in chunkEvents) {
                try {
                    processEvent(event)
                    report.recordSuccess(event)
                } catch (e: Exception) {
                    report.recordFailure(event, e.message ?: "Unknown error")
                    if (!config.continueOnError) {
                        throw e
                    }
                }
            }
        }
    }

    private fun processEvent(event: ConversionEvent) {
        when (event) {
            is ConversionEvent.SetBlock ->
                handlers.blockHandler.setBlock(targetWorld, event)
            is ConversionEvent.SetBlockEntity ->
                handlers.blockEntityHandler.setBlockEntity(targetWorld, event)
            is ConversionEvent.RemoveBlock ->
                handlers.blockHandler.removeBlock(targetWorld, event)
            is ConversionEvent.SetEntity ->
                handlers.entityHandler.setEntity(targetWorld, event)
            is ConversionEvent.RemoveEntity ->
                handlers.entityHandler.removeEntity(targetWorld, event)
            is ConversionEvent.ModifyNbt ->
                handlers.nbtHandler.modifyNbt(targetWorld, event)
        }
    }

    // Extension functions
    private fun ConversionEvent.toRegionPos(): RegionPos = when (this) {
        is ConversionEvent.SetBlock -> pos.toRegionPos()
        is ConversionEvent.SetBlockEntity -> pos.toRegionPos()
        is ConversionEvent.RemoveBlock -> pos.toRegionPos()
        is ConversionEvent.SetEntity -> RegionPos(
            (pos.x.toInt()) shr 9,
            (pos.z.toInt()) shr 9
        )
        is ConversionEvent.RemoveEntity -> RegionPos(0, 0) // TODO: track entity positions
        is ConversionEvent.ModifyNbt -> pos.toRegionPos()
    }

    private fun ConversionEvent.toChunkPos(): ChunkPos = when (this) {
        is ConversionEvent.SetBlock -> pos.toChunkPos()
        is ConversionEvent.SetBlockEntity -> pos.toChunkPos()
        is ConversionEvent.RemoveBlock -> pos.toChunkPos()
        is ConversionEvent.SetEntity -> ChunkPos(
            (pos.x.toInt()) shr 4,
            (pos.z.toInt()) shr 4
        )
        is ConversionEvent.RemoveEntity -> ChunkPos(0, 0)
        is ConversionEvent.ModifyNbt -> pos.toChunkPos()
    }
}

data class ProcessingResult(
    val success: Boolean,
    val totalEvents: Int,
    val successfulEvents: Int,
    val failedEvents: Int,
    val failures: List<EventFailure>,
    val warnings: List<EventWarning>
)

data class EventFailure(
    val eventIndex: Int,
    val pos: BlockPos?,
    val error: String
)

data class EventWarning(
    val code: String,
    val message: String,
    val pos: BlockPos?
)
```

### 3. WorldEditor1182.kt - Edytor dla 1.18.2

```kotlin
package mc.editkit.world

import mc.editkit.blockstate.BlockStatePalette
import mc.editkit.events.BlockPos
import mc.editkit.events.BlockState
import org.jglrxavpok.hephaistos.mca.RegionFile
import org.jglrxavpok.hephaistos.nbt.*
import java.nio.file.Path

/**
 * Edytor świata dla formatu Minecraft 1.18.2
 *
 * Kluczowe różnice względem 1.7.10:
 * - BlockState palette zamiast numerycznych ID
 * - Sekcje od Y=-64 do Y=319 (zamiast 0-255)
 * - Nowa struktura NBT chunków
 * - BlockEntity zamiast TileEntity
 */
class WorldEditor1182(private val worldPath: Path) : WorldEditorInterface {

    private val regionPath = worldPath.resolve("region")
    private val chunkCache = ChunkCache()
    private val modifiedChunks = mutableSetOf<ChunkPos>()

    companion object {
        const val MIN_Y = -64
        const val MAX_Y = 319
        const val SECTION_HEIGHT = 16
        const val MIN_SECTION = MIN_Y / SECTION_HEIGHT  // -4
        const val MAX_SECTION = MAX_Y / SECTION_HEIGHT  // 19
    }

    override fun setBlock(pos: BlockPos, blockId: String, blockstate: BlockState) {
        validatePos(pos)

        val chunk = getOrLoadChunk(pos.toChunkPos())
        val section = getOrCreateSection(chunk, pos.y / SECTION_HEIGHT)

        // Blockstate jako string (np. "minecraft:chest[facing=north,type=single]")
        val fullBlockState = buildBlockStateString(blockId, blockstate)

        // Dodaj do palety i ustaw w section
        val paletteIndex = section.palette.getOrAdd(fullBlockState)
        section.setBlock(pos.toLocalInChunk(), paletteIndex)

        markModified(pos.toChunkPos())
    }

    override fun setBlockEntity(pos: BlockPos, blockId: String, blockstate: BlockState, nbt: NBTCompound) {
        // Najpierw ustaw blok
        setBlock(pos, blockId, blockstate)

        // Potem dodaj BlockEntity
        val chunk = getOrLoadChunk(pos.toChunkPos())

        // Usuń istniejące BE na tej pozycji
        chunk.removeBlockEntity(pos)

        // Dodaj nowe BE z prawidłowymi koordynatami
        val beNbt = NBT.Compound { be ->
            // Skopiuj wszystkie pola z nbt
            for (key in nbt.keys) {
                be[key] = nbt[key]!!
            }
            // Nadpisz koordynaty
            be.setInt("x", pos.x)
            be.setInt("y", pos.y)
            be.setInt("z", pos.z)
            // Upewnij się że jest "keepPacked" = false (dla 1.18+)
            be.setByte("keepPacked", 0)
        }

        chunk.addBlockEntity(beNbt)
        markModified(pos.toChunkPos())
    }

    override fun removeBlock(pos: BlockPos) {
        setBlock(pos, "minecraft:air", emptyMap())
    }

    override fun setEntity(pos: EntityPos, nbt: NBTCompound) {
        val chunkPos = ChunkPos((pos.x.toInt()) shr 4, (pos.z.toInt()) shr 4)
        val chunk = getOrLoadChunk(chunkPos)

        // W 1.18.2 entities są w osobnych plikach (entities/*.mca)
        // ale dla kompatybilności obsługujemy też stary format
        val entityNbt = NBT.Compound { entity ->
            for (key in nbt.keys) {
                entity[key] = nbt[key]!!
            }
            // Upewnij się że Pos jest prawidłowe
            entity["Pos"] = NBT.List(NBTType.TAG_Double, listOf(
                NBTDouble(pos.x),
                NBTDouble(pos.y),
                NBTDouble(pos.z)
            ))
        }

        chunk.addEntity(entityNbt)
        markModified(chunkPos)
    }

    override fun commit() {
        println("Committing ${modifiedChunks.size} modified chunks...")

        // Grupuj chunki po regionach
        val byRegion = modifiedChunks.groupBy { it.toRegionPos() }

        for ((region, chunks) in byRegion) {
            commitRegion(region, chunks)
        }

        chunkCache.clear()
        modifiedChunks.clear()
        println("Commit complete.")
    }

    private fun commitRegion(region: RegionPos, chunks: List<ChunkPos>) {
        val regionFile = regionPath.resolve("r.${region.x}.${region.z}.mca")

        // Otwórz/utwórz region file
        val raf = java.io.RandomAccessFile(regionFile.toFile().apply {
            parentFile?.mkdirs()
            if (!exists()) createNewFile()
        }, "rw")

        try {
            for (chunkPos in chunks) {
                val chunk = chunkCache.get(chunkPos) ?: continue
                writeChunk(raf, chunkPos, chunk)
            }
        } finally {
            raf.close()
        }

        println("Saved region r.${region.x}.${region.z} (${chunks.size} chunks)")
    }

    private fun buildBlockStateString(blockId: String, blockstate: BlockState): String {
        return if (blockstate.isEmpty()) {
            blockId
        } else {
            val props = blockstate.entries.joinToString(",") { "${it.key}=${it.value}" }
            "$blockId[$props]"
        }
    }

    private fun validatePos(pos: BlockPos) {
        require(pos.y in MIN_Y..MAX_Y) {
            "Y coordinate ${pos.y} out of range [$MIN_Y, $MAX_Y]"
        }
    }

    private fun markModified(chunk: ChunkPos) {
        modifiedChunks.add(chunk)
    }

    // ... pozostałe metody pomocnicze
}

/**
 * Wspólny interfejs dla edytorów różnych wersji
 */
interface WorldEditorInterface {
    fun setBlock(pos: BlockPos, blockId: String, blockstate: BlockState)
    fun setBlockEntity(pos: BlockPos, blockId: String, blockstate: BlockState, nbt: NBTCompound)
    fun removeBlock(pos: BlockPos)
    fun setEntity(pos: EntityPos, nbt: NBTCompound)
    fun commit()
}
```

### 4. Rozbudowany Main.kt

```kotlin
package mc.editkit

import mc.editkit.events.*
import mc.editkit.world.*
import java.nio.file.Paths

fun main(args: Array<String>) {
    println("MC EditKit Worker v2.0 (Event Handler)")

    val command = parseArgs(args)

    when (command) {
        is Command.ApplyEvents -> applyEvents(command)
        is Command.ValidateEvents -> validateEvents(command)
        is Command.LegacyPatch -> legacyPatch(command)
        is Command.Help -> printHelp()
    }
}

sealed class Command {
    data class ApplyEvents(
        val eventFiles: List<String>,
        val targetWorld: String,
        val dryRun: Boolean = false,
        val continueOnError: Boolean = true
    ) : Command()

    data class ValidateEvents(
        val eventFiles: List<String>
    ) : Command()

    data class LegacyPatch(
        val worldPath: String,
        val patchPath: String
    ) : Command()

    object Help : Command()
}

fun applyEvents(cmd: Command.ApplyEvents) {
    println("Target world: ${cmd.targetWorld}")
    println("Event files: ${cmd.eventFiles.size}")
    if (cmd.dryRun) println("DRY RUN - no changes will be saved")

    val editor = WorldEditor1182(Paths.get(cmd.targetWorld))
    val processor = EventProcessor(editor, EventProcessor.ProcessorConfig(
        dryRun = cmd.dryRun,
        continueOnError = cmd.continueOnError
    ))

    var totalSuccess = 0
    var totalFailed = 0

    for (eventFile in cmd.eventFiles) {
        println("\n--- Processing: $eventFile ---")
        val result = processor.processEventFile(Paths.get(eventFile))

        totalSuccess += result.successfulEvents
        totalFailed += result.failedEvents

        println("Result: ${result.successfulEvents} success, ${result.failedEvents} failed")

        if (result.failures.isNotEmpty()) {
            println("Failures:")
            for (failure in result.failures.take(10)) {
                println("  - ${failure.pos}: ${failure.error}")
            }
            if (result.failures.size > 10) {
                println("  ... and ${result.failures.size - 10} more")
            }
        }
    }

    println("\n=== SUMMARY ===")
    println("Total successful: $totalSuccess")
    println("Total failed: $totalFailed")

    if (totalFailed > 0) {
        System.exit(1)
    }
}

fun printHelp() {
    println("""
        MC EditKit Worker v2.0 - Event Handler

        USAGE:
          # Apply events to target world
          java -jar worker.jar --apply-events <event-files...> --target <world-path>

          # Validate event files without applying
          java -jar worker.jar --validate-events <event-files...>

          # Legacy: Apply patch JSON (backward compatibility)
          java -jar worker.jar --world <path> --patch <path>

        OPTIONS:
          --apply-events <files>   Event JSON files to process
          --target <path>          Target world path (1.18.2 format)
          --dry-run                Validate and process but don't save
          --continue-on-error      Continue processing after errors (default: true)
          --validate-events        Only validate, don't apply

        EXAMPLES:
          # Apply single converter events
          java -jar worker.jar --apply-events events/betterstorage.json --target worlds/1.18.2

          # Apply multiple converters
          java -jar worker.jar --apply-events events/*.json --target worlds/1.18.2

          # Dry run to check for errors
          java -jar worker.jar --apply-events events/betterstorage.json --target worlds/1.18.2 --dry-run
    """.trimIndent())
}
```

## Plan implementacji

### Faza 1: Podstawy (2-3 dni)

1. **EventTypes.kt** - definicje typów
2. **EventParser.kt** - parser JSON → obiekty Kotlin
3. **NbtJsonConverter.kt** - konwersja JSON ↔ NBT

### Faza 2: Handlery (2-3 dni)

1. **BlockHandler.kt** - operacje na blokach
2. **BlockEntityHandler.kt** - operacje na BE
3. **HandlerRegistry.kt** - rejestr handlerów

### Faza 3: WorldEditor1182 (3-4 dni)

1. **WorldEditor1182.kt** - główna implementacja
2. **BlockStatePalette.kt** - obsługa palet
3. **ChunkCache.kt** - cache chunków

### Faza 4: Integracja (2 dni)

1. **EventProcessor.kt** - procesor eventów
2. **Rozbudowa Main.kt** - nowe CLI
3. **Testy integracyjne**

## Testy

```kotlin
// test/kotlin/mc/editkit/events/EventProcessorTest.kt
class EventProcessorTest {
    @Test
    fun `should process set_block event`() {
        val tempWorld = createTempWorld()
        val editor = WorldEditor1182(tempWorld)
        val processor = EventProcessor(editor)

        val eventJson = """
        {
          "version": "2.0",
          "events": [
            {"op": "set_block", "pos": [0, 64, 0], "block": "minecraft:stone"}
          ]
        }
        """.trimIndent()

        val result = processor.processEventFile(createTempFile(eventJson))

        assertEquals(1, result.successfulEvents)
        assertEquals(0, result.failedEvents)

        // Verify block was set
        val block = editor.getBlock(BlockPos(0, 64, 0))
        assertEquals("minecraft:stone", block)
    }
}
```
