package pl.pawel.minecraftkonwersja.placeholders1710;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.tileentity.TileEntity;

public class TileEntityPlaceholder extends TileEntity {
    private String sourceMod = "";
    private String sourceBlockId = "";
    private String sourceTeId = "";
    private int sourceNumericId = -1;
    private int sourceMetadata = 0;
    private int sourceX = 0;
    private int sourceY = 0;
    private int sourceZ = 0;
    private String conversionReason = "unsupported_mod_block";
    private NBTTagCompound originalNbt = new NBTTagCompound();
    private NBTTagCompound extra = new NBTTagCompound();

    @Override
    public void readFromNBT(NBTTagCompound tag) {
        super.readFromNBT(tag);
        sourceMod = tag.getString("source_mod");
        sourceBlockId = tag.getString("source_block_id");
        sourceTeId = tag.getString("source_te_id");
        sourceNumericId = tag.hasKey("source_numeric_id") ? tag.getInteger("source_numeric_id") : -1;
        sourceMetadata = tag.getInteger("source_metadata");
        conversionReason = tag.getString("conversion_reason");
        int[] pos = tag.getIntArray("source_pos");
        if (pos.length >= 3) {
            sourceX = pos[0];
            sourceY = pos[1];
            sourceZ = pos[2];
        }
        if (tag.hasKey("original_nbt")) {
            originalNbt = tag.getCompoundTag("original_nbt");
        }
        if (tag.hasKey("extra")) {
            extra = tag.getCompoundTag("extra");
        }
    }

    @Override
    public void writeToNBT(NBTTagCompound tag) {
        super.writeToNBT(tag);
        tag.setString("id", ConversionPlaceholders1710Mod.PLACEHOLDER_TE_ID);
        tag.setString("source_mod", sourceMod == null ? "" : sourceMod);
        tag.setString("source_block_id", sourceBlockId == null ? "" : sourceBlockId);
        tag.setString("source_te_id", sourceTeId == null ? "" : sourceTeId);
        tag.setInteger("source_numeric_id", sourceNumericId);
        tag.setInteger("source_metadata", sourceMetadata);
        tag.setIntArray("source_pos", new int[] { sourceX, sourceY, sourceZ });
        tag.setString("conversion_reason", conversionReason == null ? "" : conversionReason);
        tag.setTag("original_nbt", originalNbt == null ? new NBTTagCompound() : originalNbt);
        tag.setTag("extra", extra == null ? new NBTTagCompound() : extra);
    }

    public List<String> describe(boolean verbose) {
        List<String> lines = new ArrayList<String>();
        lines.add("Placeholder: " + safe(sourceMod) + " " + safe(sourceBlockId));
        lines.add("ID: " + sourceNumericId + ":" + sourceMetadata + " TE: " + safe(sourceTeId));
        lines.add("Source pos: " + sourceX + " " + sourceY + " " + sourceZ + " Reason: " + safe(conversionReason));
        if (verbose) {
            String nbt = originalNbt == null ? "{}" : originalNbt.toString();
            int limit = Math.min(900, nbt.length());
            lines.add("NBT: " + nbt.substring(0, limit) + (nbt.length() > limit ? "..." : ""));
        }
        return lines;
    }

    private String safe(String value) {
        return value == null || value.length() == 0 ? "unknown" : value;
    }
}
