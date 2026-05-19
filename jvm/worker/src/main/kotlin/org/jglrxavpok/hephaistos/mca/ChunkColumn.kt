package org.jglrxavpok.hephaistos.mca

import org.jglrxavpok.hephaistos.collections.ImmutableByteArray
import org.jglrxavpok.hephaistos.mca.AnvilException.Companion.missing
import org.jglrxavpok.hephaistos.nbt.*
import org.jglrxavpok.hephaistos.nbt.mutable.MutableNBTCompound
import java.util.concurrent.ConcurrentHashMap

/**
 * 16xNx16 chunk column. Extended from Hephaistos 2.2.0 with support for the
 * Minecraft 1.18+ flat chunk format (DataVersion ≥ 2860):
 *   - No "Level" wrapper compound
 *   - Root-level "sections" (lowercase), "block_entities", "xPos", "zPos", "yPos"
 *
 * The pre-1.18 format (with "Level") is fully preserved; the constructor
 * auto-detects which format is present.
 */
class ChunkColumn @JvmOverloads constructor(
    val x: Int,
    val z: Int,
    val minY: Int = 0,
    val maxY: Int = 255,
) {

    companion object {
        const val UnknownBiome = -1
    }

    var version: SupportedVersion = SupportedVersion.Latest
    var dataVersion = version.lowestDataVersion

    var generationStatus: GenerationStatus = GenerationStatus.Empty
    var lastUpdate: Long = 0L
    var inhabitedTime: Long = 0L

    var biomes: IntArray? = null
    var motionBlockingHeightMap = Heightmap()
    var worldSurfaceHeightMap = Heightmap()
    var motionBlockingNoLeavesHeightMap: Heightmap? = null
    var worldSurfaceWorldGenHeightMap: Heightmap? = null
    var oceanFloorHeightMap: Heightmap? = null
    var oceanFloorWorldGenHeightMap: Heightmap? = null

    var entities: NBTList<NBTCompound> = NBT.List(NBTType.TAG_Compound)
    var tileEntities: NBTList<NBTCompound> = NBT.List(NBTType.TAG_Compound)
    var tileTicks: NBTList<NBTCompound> = NBT.List(NBTType.TAG_Compound)
    var liquidTicks: NBTList<NBTCompound> = NBT.List(NBTType.TAG_Compound)
    var structures: NBTCompound? = null
    var lights: NBTList<NBTList<NBTShort>>? = null
    var liquidsToBeTicked: NBTList<NBTList<NBTShort>>? = null
    var toBeTicked: NBTList<NBTList<NBTShort>>? = null
    var postProcessing: NBTList<NBTList<NBTShort>>? = null

    val sections = ConcurrentHashMap<Byte, ChunkSection>()
    var airCarvingMask: ImmutableByteArray? = null
    var liquidCarvingMask: ImmutableByteArray? = null

    val logicalHeight = maxY - minY + 1
    private val biomeArraySize = logicalHeight.blockToSection() * 4 * 4 * 4

    // ── NBT constructor ───────────────────────────────────────────────────────

    @Throws(AnvilException::class)
    constructor(chunkData: NBTCompound, minY: Int = 0, maxY: Int = 255) : this(
        if (chunkData.containsKey("Level"))
            (chunkData.getCompound("Level") ?: missing("Level")).getInt("xPos") ?: missing("xPos")
        else
            chunkData.getInt("xPos") ?: missing("xPos"),
        if (chunkData.containsKey("Level"))
            (chunkData.getCompound("Level") ?: missing("Level")).getInt("zPos") ?: missing("zPos")
        else
            chunkData.getInt("zPos") ?: missing("zPos"),
        minY,
        maxY,
    ) {
        if (minY > maxY) throw AnvilException("minY must be <= maxY")

        dataVersion = chunkData.getInt("DataVersion") ?: missing("DataVersion")
        version = SupportedVersion.closest(dataVersion)

        if (chunkData.containsKey("Level")) {
            readLegacy(chunkData)
        } else {
            readModern(chunkData)
        }
    }

    // ── Legacy (pre-1.18) reader ─────────────────────────────────────────────

    private fun readLegacy(chunkData: NBTCompound) {
        val level = chunkData.getCompound("Level") ?: missing("Level")
        lastUpdate = level.getLong("LastUpdate") ?: missing("LastUpdate")
        inhabitedTime = level.getLong("InhabitedTime") ?: missing("InhabitedTime")
        generationStatus = GenerationStatus.fromID(level.getString("Status") ?: missing("Status"))
        biomes = level.getIntArray("Biomes")?.copyArray()

        if (generationStatus.ordinal >= GenerationStatus.Heightmaps.ordinal) {
            val hm = level.getCompound("Heightmaps") ?: missing("Heightmaps")
            motionBlockingHeightMap = Heightmap(hm.getLongArray("MOTION_BLOCKING") ?: missing("MOTION_BLOCKING"), version)
            worldSurfaceHeightMap = Heightmap(hm.getLongArray("WORLD_SURFACE") ?: missing("WORLD_SURFACE"), version)
            motionBlockingNoLeavesHeightMap = hm.getLongArray("MOTION_BLOCKING_NO_LEAVES")?.let { Heightmap(it, version) }
            worldSurfaceWorldGenHeightMap = hm.getLongArray("WORLD_SURFACE_WG")?.let { Heightmap(it, version) }
            oceanFloorHeightMap = hm.getLongArray("OCEAN_FLOOR")?.let { Heightmap(it, version) }
            oceanFloorWorldGenHeightMap = hm.getLongArray("OCEAN_FLOOR_WG")?.let { Heightmap(it, version) }
        } else {
            motionBlockingHeightMap = Heightmap()
            worldSurfaceHeightMap = Heightmap()
        }

        entities = level.getList("Entities") ?: NBT.List(NBTType.TAG_Compound)
        tileEntities = level.getList("TileEntities") ?: NBT.List(NBTType.TAG_Compound)
        tileTicks = level.getList("TileTicks") ?: NBT.List(NBTType.TAG_Compound)
        liquidTicks = level.getList("LiquidTicks") ?: NBT.List(NBTType.TAG_Compound)
        structures = level.getCompound("Structures")

        val carvingMasks = level.getCompound("CarvingMasks")
        if (carvingMasks != null) {
            airCarvingMask = carvingMasks.getByteArray("AIR")
            liquidCarvingMask = carvingMasks.getByteArray("LIQUID")
        }
        lights = level.getList("Lights")
        liquidsToBeTicked = level.getList("LiquidsToBeTicked")
        toBeTicked = level.getList("ToBeTicked")
        postProcessing = level.getList("PostProcessing")

        val sectionsNBT = level.getList<NBTCompound>("Sections") ?: missing("Sections")
        for (nbt in sectionsNBT) {
            val sectionY = nbt.getByte("Y") ?: missing("Y")
            if (version < SupportedVersion.MC_1_17_0) {
                if (sectionY !in 0..15) continue
            }
            sections[sectionY] = ChunkSection(nbt, version)
        }
    }

    // ── Modern (1.18+) reader ────────────────────────────────────────────────

    private fun readModern(chunkData: NBTCompound) {
        lastUpdate = chunkData.getLong("LastUpdate") ?: 0L
        inhabitedTime = chunkData.getLong("InhabitedTime") ?: 0L

        val rawStatus = chunkData.getString("Status") ?: "full"
        val statusId = if (':' in rawStatus) rawStatus.substringAfter(':') else rawStatus
        generationStatus = try {
            GenerationStatus.fromID(statusId)
        } catch (_: IllegalArgumentException) {
            GenerationStatus.Full
        }

        val hm = chunkData.getCompound("Heightmaps")
        if (hm != null && generationStatus.ordinal >= GenerationStatus.Heightmaps.ordinal) {
            motionBlockingHeightMap = hm.getLongArray("MOTION_BLOCKING")?.let { Heightmap(it, version) } ?: Heightmap()
            worldSurfaceHeightMap = hm.getLongArray("WORLD_SURFACE")?.let { Heightmap(it, version) } ?: Heightmap()
            motionBlockingNoLeavesHeightMap = hm.getLongArray("MOTION_BLOCKING_NO_LEAVES")?.let { Heightmap(it, version) }
            worldSurfaceWorldGenHeightMap = hm.getLongArray("WORLD_SURFACE_WG")?.let { Heightmap(it, version) }
            oceanFloorHeightMap = hm.getLongArray("OCEAN_FLOOR")?.let { Heightmap(it, version) }
            oceanFloorWorldGenHeightMap = hm.getLongArray("OCEAN_FLOOR_WG")?.let { Heightmap(it, version) }
        } else {
            motionBlockingHeightMap = Heightmap()
            worldSurfaceHeightMap = Heightmap()
        }

        tileEntities = chunkData.getList("block_entities") ?: NBT.List(NBTType.TAG_Compound)
        structures = chunkData.getCompound("structures")

        val sectionsNBT = chunkData.getList<NBTCompound>("sections")
            ?: NBT.List(NBTType.TAG_Compound)
        for (nbt in sectionsNBT) {
            val sectionY = nbt.getByte("Y") ?: missing("Y")
            sections[sectionY] = ChunkSection(nbt, version)
        }
    }

    // ── Public API ───────────────────────────────────────────────────────────

    fun getSection(sectionY: Byte): ChunkSection =
        sections.computeIfAbsent(sectionY, ::ChunkSection)

    fun setBlockState(x: Int, y: Int, z: Int, state: BlockState) {
        checkBounds(x, y, z)
        getSection(y.blockToSection())[x, y.blockInsideSection(), z] = state
    }

    fun getBlockState(x: Int, y: Int, z: Int): BlockState {
        checkBounds(x, y, z)
        val section = getSection(y.blockToSection())
        return if (section.empty) BlockState.AIR else section[x, y.blockInsideSection(), z]
    }

    fun setBiome(x: Int, y: Int, z: Int, biomeID: Int) {
        checkBounds(x, y, z)
        if (biomes == null) biomes = IntArray(biomeArraySize) { UnknownBiome }
        biomes!![x / 4 + (z / 4) * 4 + (y / 4) * 16] = biomeID
    }

    fun getBiome(x: Int, y: Int, z: Int): Int {
        checkBounds(x, y, z)
        return biomes?.get(x / 4 + (z / 4) * 4 + (y / 4) * 16) ?: UnknownBiome
    }

    private fun checkBounds(x: Int, y: Int, z: Int) {
        if (x !in 0..15) throw IllegalArgumentException("x ($x) is not in 0..15")
        if (z !in 0..15) throw IllegalArgumentException("z ($z) is not in 0..15")
        if (y !in minY..maxY) throw IllegalArgumentException("y ($y) is not in $minY..$maxY")
    }

    // ── NBT serialisation ─────────────────────────────────────────────────────

    fun toNBT(): NBTCompound = NBT.Kompound {
        this["DataVersion"] = NBT.Int(dataVersion)

        if (version >= SupportedVersion.MC_1_18_2) {
            // ── 1.18+ flat format ─────────────────────────────────────────
            this["xPos"] = NBT.Int(x)
            this["zPos"] = NBT.Int(z)
            this["yPos"] = NBT.Int(minY / 16)
            this["LastUpdate"] = NBT.Long(lastUpdate)
            this["InhabitedTime"] = NBT.Long(inhabitedTime)
            this["Status"] = NBT.String(generationStatus.id)
            this["isLightOn"] = NBT.Byte(1)

            this["Heightmaps"] = NBT.Kompound {
                this["MOTION_BLOCKING"] = NBT.LongArray(motionBlockingHeightMap.compact(version))
                motionBlockingNoLeavesHeightMap?.let { this["MOTION_BLOCKING_NO_LEAVES"] = NBT.LongArray(it.compact(version)) }
                oceanFloorHeightMap?.let { this["OCEAN_FLOOR"] = NBT.LongArray(it.compact(version)) }
                oceanFloorWorldGenHeightMap?.let { this["OCEAN_FLOOR_WG"] = NBT.LongArray(it.compact(version)) }
                this["WORLD_SURFACE"] = NBT.LongArray(worldSurfaceHeightMap.compact(version))
                worldSurfaceWorldGenHeightMap?.let { this["WORLD_SURFACE_WG"] = NBT.LongArray(it.compact(version)) }
            }

            this["sections"] = NBT.List(
                NBTType.TAG_Compound,
                sections.values
                    .filter { !it.empty }
                    .sortedBy { it.y.toInt() }
                    .map { it.toNBT(version) }
            )

            this["block_entities"] = tileEntities
            structures?.let { this["structures"] = it }
        } else {
            // ── Pre-1.18 legacy format ────────────────────────────────────
            this["Level"] = NBT.Kompound {
                this["xPos"] = NBT.Int(x)
                this["zPos"] = NBT.Int(z)
                this["LastUpdate"] = NBT.Long(lastUpdate)
                this["InhabitedTime"] = NBT.Long(inhabitedTime)
                this["Status"] = NBT.String(generationStatus.id)
                biomes?.let { this["Biomes"] = NBT.IntArray(*it) }

                this["Heightmaps"] = NBT.Kompound {
                    this["MOTION_BLOCKING"] = NBT.LongArray(motionBlockingHeightMap.compact(version))
                    motionBlockingNoLeavesHeightMap?.let { this["MOTION_BLOCKING_NO_LEAVES"] = NBT.LongArray(it.compact(version)) }
                    oceanFloorHeightMap?.let { this["OCEAN_FLOOR"] = NBT.LongArray(it.compact(version)) }
                    oceanFloorWorldGenHeightMap?.let { this["OCEAN_FLOOR_WG"] = NBT.LongArray(it.compact(version)) }
                    this["WORLD_SURFACE"] = NBT.LongArray(worldSurfaceHeightMap.compact(version))
                    worldSurfaceWorldGenHeightMap?.let { this["WORLD_SURFACE_WG"] = NBT.LongArray(it.compact(version)) }
                }

                this["Sections"] = NBT.List(
                    NBTType.TAG_Compound,
                    sections.values.filter { !it.empty }.map { it.toNBT(version) }
                )

                this["Entities"] = entities
                this["TileEntities"] = tileEntities
                this["TileTicks"] = tileTicks
                this["LiquidTicks"] = liquidTicks
                structures?.let { this["Structures"] = it }

                if (airCarvingMask != null || liquidCarvingMask != null) {
                    this["CarvingMasks"] = NBT.Kompound {
                        airCarvingMask?.let { this["AIR"] = NBT.ByteArray(it) }
                        liquidCarvingMask?.let { this["LIQUID"] = NBT.ByteArray(it) }
                    }
                }
                lights?.let { this["Lights"] = it }
                liquidsToBeTicked?.let { this["LiquidsToBeTicked"] = it }
                toBeTicked?.let { this["ToBeTicked"] = it }
                postProcessing?.let { this["PostProcessing"] = it }
            }
        }
    }

    // ── GenerationStatus ─────────────────────────────────────────────────────

    enum class GenerationStatus(val id: String) {
        Empty("empty"),
        StructureStarts("structure_starts"),
        StructureReferences("structure_references"),
        Biomes("biomes"),
        Noise("noise"),
        Surface("surface"),
        Carvers("carvers"),
        LiquidCarvers("liquid_carvers"),
        Features("features"),
        Light("light"),
        Spawn("spawn"),
        Heightmaps("heightmaps"),
        Full("full");

        companion object {
            @JvmStatic
            fun fromID(id: String): GenerationStatus =
                values().firstOrNull { it.id == id }
                    ?: throw IllegalArgumentException("Invalid GenerationStatus id: $id")
        }
    }
}
