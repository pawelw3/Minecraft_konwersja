package pl.pawel.cuttableblocks.items;

import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import pl.pawel.cuttableblocks.registry.ModBlocks;
import pl.pawel.cuttableblocks.world.CarpenterBlockEntity;

/**
 * Carpenter's Hammer: right-click a carpenter block to cycle its facing.
 * Sneak+right-click cycles shape (where applicable).
 * This is a basic implementation – full feature parity with 1.7.10 would
 * require per-block-type logic (slope type cycling, door open/close, etc.).
 */
public class CarpenterHammer extends Item {

    public CarpenterHammer(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();

        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof CarpenterBlockEntity cbe)) {
            return InteractionResult.PASS;
        }

        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        if (context.getPlayer() != null && context.getPlayer().isShiftKeyDown()) {
            // Cycle shape
            int shape = cbe.getShape();
            shape = (shape + 1) % 16;
            cbe.setShape(shape);
        } else {
            // Cycle facing
            int facing = cbe.getFacing();
            facing = (facing + 1) % 6;
            cbe.setFacing(facing);
        }

        return InteractionResult.CONSUME;
    }
}
