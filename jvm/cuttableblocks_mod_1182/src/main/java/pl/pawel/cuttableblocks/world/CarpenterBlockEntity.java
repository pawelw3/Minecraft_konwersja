package pl.pawel.cuttableblocks.world;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntArrayTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import pl.pawel.cuttableblocks.registry.ModBlockEntities;

/**
 * BlockEntity for all 18 carpenter_* cuttableblocks block types.
 *
 * Mirrors TileEntityCoverable from new_mod_trial 1.7.10, extended with full
 * CarpentersBlocks feature parity (side covers, dyes, design, illuminator,
 * collapsible quad depths, flower pot, multiblock).
 *
 * NBT schema:
 *
 *   -- From TileEntityCoverable (1.7.10 compatible field names) --
 *   coverBlock         STRING   ""     Base cover material (1.18.2 resource location).
 *                                      1.7.10 equivalent: coverBlock + coverMeta (merged here).
 *   facing             INT      0      ForgeDirection ordinal: 0=DOWN,1=UP,2=N,3=S,4=W,5=E.
 *   shape              INT      0      Block-type specific shape index:
 *                                        slope=slopeID(0..64), stairs=stairsID(0..27),
 *                                        block=slabID(0..6), barrier=barrierType,
 *                                        hatch/door=type, gate=gateType,
 *                                        ladder=ladderType, torch=torchType,
 *                                        daylight_sensor=sensitivity(0..2), others=0.
 *   flags              INT      0      Bitmask (FLAG_* constants below).
 *   sourceCarpentersTeId STRING ""    Original CB block ID for traceability.
 *
 *   -- 1.18.2 extensions for full CB parity --
 *   sideCovers         COMPOUND {}    Per-side cover overrides, keys "0".."5".
 *   sideDyes           COMPOUND {}    Per-side dye materials.
 *   cbDesign           STRING   ""    Chisel pattern name.
 *   illuminator        BYTE     0     1 if illuminator attribute is set.
 *   quadDepths         INT[]    {0,0,0,0}  Collapsible quad depths [XZNN,XZNP,XZPN,XZPP] 0..16.
 *   lightLevel         INT      0     Daylight sensor current light level (0..15).
 *   plantBlock         STRING   ""    Flower pot plant resource location.
 *   soilBlock          STRING   ""    Flower pot soil resource location.
 *   cbMetadataRaw      INT      -1    Multiblock preserved raw cbMetadata (-1 = not set).
 */
public class CarpenterBlockEntity extends BlockEntity {

    // flags bitmask constants (compatible with 1.7.10 TileEntityCoverable flags)
    public static final int FLAG_STATE        = 0x01; // open/powered/lit/inverted
    public static final int FLAG_UPPER_HALF   = 0x02; // door upper half; hatch high position
    public static final int FLAG_RIGHT_HINGE  = 0x04; // door right hinge
    public static final int FLAG_RIGID        = 0x08; // hatch/door rigid
    public static final int FLAG_POLARITY_NEG = 0x10; // lever/button polarity negative
    public static final int FLAG_SMOLDERING   = 0x20; // torch smoldering
    public static final int FLAG_HAS_POST     = 0x40; // barrier has post

    // --- 1.7.10-compatible base fields ---
    private String coverBlock = "";
    private int facing = 0;
    private int shape = 0;
    private int flags = 0;
    private String sourceCarpentersTeId = "";

    // --- 1.18.2 CB-parity extensions ---
    private CompoundTag sideCovers = new CompoundTag();
    private CompoundTag sideDyes = new CompoundTag();
    private String cbDesign = "";
    private boolean illuminator = false;

    // collapsible_block
    private int[] quadDepths = {0, 0, 0, 0};

    // carpenter_daylight_sensor
    private int lightLevel = 0;

    // carpenter_flower_pot
    private String plantBlock = "";
    private String soilBlock = "";

    // carpenter_bed / carpenter_garage_door
    private int cbMetadataRaw = -1;

    // -----------------------------------------------------------------------

    public CarpenterBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.CARPENTER.get(), pos, state);
    }

    // --- Serialization -----------------------------------------------------

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);

        tag.putString("coverBlock", coverBlock);
        tag.putInt("facing", facing);
        tag.putInt("shape", shape);
        tag.putInt("flags", flags);
        tag.putString("sourceCarpentersTeId", sourceCarpentersTeId);

        if (!sideCovers.isEmpty()) {
            tag.put("sideCovers", sideCovers.copy());
        }
        if (!sideDyes.isEmpty()) {
            tag.put("sideDyes", sideDyes.copy());
        }
        if (!cbDesign.isEmpty()) {
            tag.putString("cbDesign", cbDesign);
        }
        if (illuminator) {
            tag.putBoolean("illuminator", true);
        }
        if (quadDepths[0] != 0 || quadDepths[1] != 0 || quadDepths[2] != 0 || quadDepths[3] != 0) {
            tag.put("quadDepths", new IntArrayTag(quadDepths));
        }
        if (lightLevel != 0) {
            tag.putInt("lightLevel", lightLevel);
        }
        if (!plantBlock.isEmpty()) {
            tag.putString("plantBlock", plantBlock);
        }
        if (!soilBlock.isEmpty()) {
            tag.putString("soilBlock", soilBlock);
        }
        if (cbMetadataRaw >= 0) {
            tag.putInt("cbMetadataRaw", cbMetadataRaw);
        }
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);

        coverBlock = tag.getString("coverBlock");
        facing = tag.contains("facing", Tag.TAG_INT) ? tag.getInt("facing") : 0;
        shape = tag.contains("shape", Tag.TAG_INT) ? tag.getInt("shape") : 0;
        flags = tag.contains("flags", Tag.TAG_INT) ? tag.getInt("flags") : 0;
        sourceCarpentersTeId = tag.getString("sourceCarpentersTeId");

        sideCovers = tag.contains("sideCovers", Tag.TAG_COMPOUND)
            ? tag.getCompound("sideCovers").copy() : new CompoundTag();
        sideDyes = tag.contains("sideDyes", Tag.TAG_COMPOUND)
            ? tag.getCompound("sideDyes").copy() : new CompoundTag();
        cbDesign = tag.getString("cbDesign");
        illuminator = tag.getBoolean("illuminator");

        if (tag.contains("quadDepths", Tag.TAG_INT_ARRAY)) {
            int[] raw = tag.getIntArray("quadDepths");
            if (raw.length >= 4) {
                quadDepths = new int[]{raw[0], raw[1], raw[2], raw[3]};
            }
        }
        lightLevel = tag.contains("lightLevel", Tag.TAG_INT) ? tag.getInt("lightLevel") : 0;
        plantBlock = tag.getString("plantBlock");
        soilBlock = tag.getString("soilBlock");
        cbMetadataRaw = tag.contains("cbMetadataRaw", Tag.TAG_INT) ? tag.getInt("cbMetadataRaw") : -1;
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = super.getUpdateTag();
        saveAdditional(tag);
        return tag;
    }

    // --- Accessors ---------------------------------------------------------

    public String getCoverBlock() { return coverBlock; }
    public int getFacing() { return facing; }
    public int getShape() { return shape; }
    public int getFlags() { return flags; }
    public boolean hasFlag(int mask) { return (flags & mask) != 0; }
    public String getSourceCarpentersTeId() { return sourceCarpentersTeId; }
    public CompoundTag getSideCovers() { return sideCovers.copy(); }
    public CompoundTag getSideDyes() { return sideDyes.copy(); }
    public String getCbDesign() { return cbDesign; }
    public boolean isIlluminator() { return illuminator; }
    public int[] getQuadDepths() { return quadDepths.clone(); }
    public int getLightLevel() { return lightLevel; }
    public String getPlantBlock() { return plantBlock; }
    public String getSoilBlock() { return soilBlock; }
    public int getCbMetadataRaw() { return cbMetadataRaw; }

    // --- Setters (for in-game tools) ---------------------------------------

    public void setCoverBlock(String coverBlock) {
        this.coverBlock = coverBlock;
        setChanged();
    }

    public void setFacing(int facing) {
        this.facing = facing;
        setChanged();
    }

    public void setShape(int shape) {
        this.shape = shape;
        setChanged();
    }

    public void setFlags(int flags) {
        this.flags = flags;
        setChanged();
    }

    public void setFlag(int mask, boolean value) {
        if (value) {
            this.flags |= mask;
        } else {
            this.flags &= ~mask;
        }
        setChanged();
    }
}
