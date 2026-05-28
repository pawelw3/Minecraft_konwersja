package pl.pawel.cuttableblocks.items;

import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import pl.pawel.cuttableblocks.registry.ModBlocks;
import pl.pawel.cuttableblocks.world.CuttableBlockEntity;

/**
 * Cutting tool: right-click any block to convert it into a cuttable_block.
 * The original block type is stored in CuttableBlockEntity.originalBlock so
 * that the renderer can display it (and in future, true arbitrary-plane
 * cutting can be implemented).
 */
public class CuttingTool extends Item {

    public CuttingTool(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        BlockState state = level.getBlockState(pos);
        Block block = state.getBlock();

        // Don't re-cut our own blocks
        if (block == ModBlocks.CUTTABLE_BLOCK.get()) {
            // Toggle keepPositive side as a simple interaction
            BlockEntity be = level.getBlockEntity(pos);
            if (be instanceof CuttableBlockEntity cbe) {
                if (!level.isClientSide) {
                    cbe.setKeepPositive(!cbe.keepPositiveSide());
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        String originalId = block.getRegistryName().toString();
        level.setBlock(pos, ModBlocks.CUTTABLE_BLOCK.get().defaultBlockState(), 3);

        BlockEntity be = level.getBlockEntity(pos);
        if (be instanceof CuttableBlockEntity cbe) {
            cbe.setOriginalBlock(originalId);
            cbe.setDirId(0);
            cbe.setRotId(0);
            cbe.setKeepPositive(true);
        }

        return InteractionResult.CONSUME;
    }
}
