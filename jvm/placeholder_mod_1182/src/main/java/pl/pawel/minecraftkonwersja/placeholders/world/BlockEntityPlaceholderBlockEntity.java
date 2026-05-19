package pl.pawel.minecraftkonwersja.placeholders.world;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModBlockEntities;

public class BlockEntityPlaceholderBlockEntity extends BlockEntity {
    private String sourceMod = "";
    private String sourceBlockId = "";
    private String sourceTeId = "";
    private int sourceMetadata = 0;
    private int sourceX = 0;
    private int sourceY = 0;
    private int sourceZ = 0;
    private String conversionReason = "unsupported_be";
    private String conversionStage = "";
    private CompoundTag originalNbt = new CompoundTag();
    private CompoundTag extra = new CompoundTag();

    public BlockEntityPlaceholderBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.BLOCK_ENTITY_PLACEHOLDER.get(), pos, state);
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putString("source_mod", sourceMod);
        tag.putString("source_block_id", sourceBlockId);
        tag.putString("source_te_id", sourceTeId);
        tag.putInt("source_metadata", sourceMetadata);
        ListTag sourcePos = new ListTag();
        sourcePos.add(net.minecraft.nbt.IntTag.valueOf(sourceX));
        sourcePos.add(net.minecraft.nbt.IntTag.valueOf(sourceY));
        sourcePos.add(net.minecraft.nbt.IntTag.valueOf(sourceZ));
        tag.put("source_pos", sourcePos);
        tag.putString("conversion_reason", conversionReason);
        tag.putString("conversion_stage", conversionStage);
        tag.put("original_nbt", originalNbt.copy());
        tag.put("extra", extra.copy());
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        sourceMod = tag.getString("source_mod");
        sourceBlockId = tag.getString("source_block_id");
        sourceTeId = tag.getString("source_te_id");
        sourceMetadata = tag.contains("source_metadata", Tag.TAG_INT) ? tag.getInt("source_metadata") : 0;
        readSourcePos(tag);
        conversionReason = tag.getString("conversion_reason");
        if (conversionReason.isEmpty()) {
            conversionReason = "unsupported_be";
        }
        conversionStage = tag.getString("conversion_stage");
        originalNbt = tag.contains("original_nbt", Tag.TAG_COMPOUND) ? tag.getCompound("original_nbt").copy() : new CompoundTag();
        extra = tag.contains("extra", Tag.TAG_COMPOUND) ? tag.getCompound("extra").copy() : new CompoundTag();
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = super.getUpdateTag();
        saveAdditional(tag);
        return tag;
    }

    public String getSourceMod() {
        return sourceMod;
    }

    public String getSourceBlockId() {
        return sourceBlockId;
    }

    public String getSourceTeId() {
        return sourceTeId;
    }

    public int getSourceMetadata() {
        return sourceMetadata;
    }

    public String getSourcePosString() {
        return "[" + sourceX + "," + sourceY + "," + sourceZ + "]";
    }

    public String getConversionReason() {
        return conversionReason;
    }

    public String getConversionStage() {
        return conversionStage;
    }

    public CompoundTag getOriginalNbt() {
        return originalNbt.copy();
    }

    public String originalNbtAsString() {
        return originalNbt.toString();
    }

    public String originalNbtPreview(int maxChars) {
        String value = originalNbt.toString();
        if (value.length() <= maxChars) {
            return value;
        }
        return value.substring(0, Math.max(0, maxChars - 3)) + "...";
    }

    private void readSourcePos(CompoundTag tag) {
        if (tag.contains("source_pos", Tag.TAG_LIST)) {
            ListTag sourcePos = tag.getList("source_pos", Tag.TAG_INT);
            if (sourcePos.size() >= 3) {
                sourceX = sourcePos.getInt(0);
                sourceY = sourcePos.getInt(1);
                sourceZ = sourcePos.getInt(2);
                return;
            }
        }
        sourceX = tag.contains("x", Tag.TAG_INT) ? tag.getInt("x") : worldPosition.getX();
        sourceY = tag.contains("y", Tag.TAG_INT) ? tag.getInt("y") : worldPosition.getY();
        sourceZ = tag.contains("z", Tag.TAG_INT) ? tag.getInt("z") : worldPosition.getZ();
    }
}
