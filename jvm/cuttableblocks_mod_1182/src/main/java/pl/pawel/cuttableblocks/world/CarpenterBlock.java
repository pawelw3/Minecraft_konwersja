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
 * Shared block class for all 18 carpenter_* cuttableblocks types.
 *
 * Matches the role of BlockCoverable / BlockCoverableDoor from new_mod_trial 1.7.10.
 * Geometry and cover data live entirely in CarpenterBlockEntity NBT.
 */
public class CarpenterBlock extends BaseEntityBlock {

    public CarpenterBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new CarpenterBlockEntity(pos, state);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.ENTITYBLOCK_ANIMATED;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos,
                                 Player player, InteractionHand hand, BlockHitResult hit) {
        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof CarpenterBlockEntity cbe)) {
            return InteractionResult.PASS;
        }

        // Simple toggle for functional blocks (door, hatch, gate, lever, button, torch, daylight_sensor)
        if (!level.isClientSide) {
            cbe.setFlag(CarpenterBlockEntity.FLAG_STATE, !cbe.hasFlag(CarpenterBlockEntity.FLAG_STATE));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
