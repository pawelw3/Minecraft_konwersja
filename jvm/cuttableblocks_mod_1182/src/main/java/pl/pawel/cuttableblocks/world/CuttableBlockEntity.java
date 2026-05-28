package pl.pawel.cuttableblocks.world;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import pl.pawel.cuttableblocks.registry.ModBlockEntities;

/**
 * BlockEntity for cuttable_block (free arbitrary-cut concept).
 *
 * Mirrors TileEntityCuttable from new_mod_trial 1.7.10.
 *
 * NBT schema:
 *   originalBlock  STRING  ""    Resource location of the original block material.
 *                                1.7.10: stored as block registry name + originalMeta.
 *   rotId          BYTE    0     Rotation ID (0..23) — discrete block rotation.
 *   dirId          BYTE    0     Direction ID (0..17) — cut plane normal direction.
 *   keepPositive   BYTE    0     1 = keep the positive-side half after cut.
 */
public class CuttableBlockEntity extends BlockEntity {

    private String originalBlock = "";
    private byte rotId = 0;
    private byte dirId = 0;
    private boolean keepPositive = true;

    public CuttableBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.CUTTABLE.get(), pos, state);
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putString("originalBlock", originalBlock);
        tag.putByte("rotId", rotId);
        tag.putByte("dirId", dirId);
        tag.putBoolean("keepPositive", keepPositive);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        originalBlock = tag.getString("originalBlock");
        rotId = tag.contains("rotId", Tag.TAG_BYTE) ? tag.getByte("rotId") : 0;
        dirId = tag.contains("dirId", Tag.TAG_BYTE) ? tag.getByte("dirId") : 0;
        keepPositive = !tag.contains("keepPositive", Tag.TAG_BYTE) || tag.getBoolean("keepPositive");
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = super.getUpdateTag();
        saveAdditional(tag);
        return tag;
    }

    public String getOriginalBlock() { return originalBlock; }
    public int getRotId() { return rotId & 0xFF; }
    public int getDirId() { return dirId & 0xFF; }
    public boolean keepPositiveSide() { return keepPositive; }

    // --- Setters (for in-game tools) ---------------------------------------

    public void setOriginalBlock(String originalBlock) {
        this.originalBlock = originalBlock;
        setChanged();
    }

    public void setRotId(int rotId) {
        this.rotId = (byte) rotId;
        setChanged();
    }

    public void setDirId(int dirId) {
        this.dirId = (byte) dirId;
        setChanged();
    }

    public void setKeepPositive(boolean keepPositive) {
        this.keepPositive = keepPositive;
        setChanged();
    }
}
