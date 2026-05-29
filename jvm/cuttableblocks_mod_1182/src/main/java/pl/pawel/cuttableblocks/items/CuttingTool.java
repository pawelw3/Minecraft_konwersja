package pl.pawel.cuttableblocks.items;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.registries.ForgeRegistries;
import pl.pawel.cuttableblocks.registry.ModBlocks;
import pl.pawel.cuttableblocks.world.CuttableBlockEntity;

/**
 * Cutting tool: right-click any block to convert it into a cuttable_block.
 * Right-click an existing cuttable_block to cycle its cut direction (dirId).
 * Sneak+right-click cycles rotation (rotId).
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

        // Existing cuttable block: cycle dirId / rotId
        if (block == ModBlocks.CUTTABLE_BLOCK.get()) {
            BlockEntity be = level.getBlockEntity(pos);
            if (be instanceof CuttableBlockEntity cbe) {
                if (!level.isClientSide) {
                    if (context.getPlayer() != null && context.getPlayer().isShiftKeyDown()) {
                        cbe.setRotId((cbe.getRotId() + 1) % 24);
                    } else {
                        cbe.setDirId((cbe.getDirId() + 1) % 6);
                    }
                    level.sendBlockUpdated(pos, state, state, Block.UPDATE_ALL);
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        String originalId = ForgeRegistries.BLOCKS.getKey(block).toString();
        level.setBlock(pos, ModBlocks.CUTTABLE_BLOCK.get().defaultBlockState(), 3);

        BlockState newState = level.getBlockState(pos);
        BlockEntity be = level.getBlockEntity(pos);
        if (be instanceof CuttableBlockEntity cbe) {
            cbe.setOriginalBlock(originalId);
            Direction clickedFace = context.getClickedFace();
            cbe.setDirId(clickedFace != null ? clickedFace.get3DDataValue() : 0);
            cbe.setRotId(0);
            cbe.setKeepPositive(true);
            level.sendBlockUpdated(pos, newState, newState, Block.UPDATE_ALL);
        }

        return InteractionResult.CONSUME;
    }
}
