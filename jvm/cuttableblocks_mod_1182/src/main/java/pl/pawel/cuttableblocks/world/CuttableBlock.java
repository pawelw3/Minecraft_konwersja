package pl.pawel.cuttableblocks.world;

import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * Block class for cuttable_block (free arbitrary-cut concept).
 *
 * Matches BlockCuttable from new_mod_trial 1.7.10.
 * Cut geometry (rotId, dirId, keepPositive, originalBlock) lives in CuttableBlockEntity.
 */
public class CuttableBlock extends BaseEntityBlock {

    public CuttableBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new CuttableBlockEntity(pos, state);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos,
                                 Player player, InteractionHand hand, BlockHitResult hit) {
        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof CuttableBlockEntity cbe)) {
            return InteractionResult.PASS;
        }

        if (!level.isClientSide) {
            cbe.setKeepPositive(!cbe.keepPositiveSide());
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
