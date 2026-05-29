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
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.util.StringRepresentable;
import pl.pawel.cuttableblocks.world.*;

import java.util.ArrayList;
import java.util.List;

/**
 * Carpenter's Hammer: right-click a carpenter block to cycle its facing/direction.
 * Sneak+right-click cycles the block's type/shape/polarity where applicable.
 *
 * Operates on BlockState properties (1.18.2) rather than the legacy int facing/shape
 * stored in CarpenterBlockEntity.
 */
public class CarpenterHammer extends Item {

    public CarpenterHammer(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        BlockState state = level.getBlockState(pos);
        Block block = state.getBlock();

        if (!(block instanceof AbstractCarpenterBlock)) {
            return InteractionResult.PASS;
        }

        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        boolean shift = context.getPlayer() != null && context.getPlayer().isShiftKeyDown();
        BlockState newState = state;

        if (shift) {
            newState = cycleShiftProperty(state, block);
        } else {
            newState = cycleMainProperty(state, block);
        }

        if (newState != state) {
            level.setBlock(pos, newState, Block.UPDATE_ALL);
            BlockEntity be = level.getBlockEntity(pos);
            if (be != null) {
                be.setChanged();
            }
        }

        return InteractionResult.CONSUME;
    }

    /** Cycle the primary direction property (FACING) or equivalent. */
    private static BlockState cycleMainProperty(BlockState state, Block block) {
        // Generic DirectionProperty cycle
        for (Property<?> prop : state.getProperties()) {
            if (prop instanceof DirectionProperty dp) {
                return cycleDirection(state, dp);
            }
        }
        // No direction property - try cycling other meaningful properties
        if (block instanceof CarpenterBlockBlock && state.hasProperty(CarpenterBlockBlock.TYPE)) {
            return cycleEnum(state, CarpenterBlockBlock.TYPE);
        }
        if (block instanceof CarpenterPressurePlateBlock && state.hasProperty(CarpenterPressurePlateBlock.POWERED)) {
            return state.setValue(CarpenterPressurePlateBlock.POWERED, !state.getValue(CarpenterPressurePlateBlock.POWERED));
        }
        return state;
    }

    /** Cycle the secondary "shape/type" property when sneaking. */
    private static BlockState cycleShiftProperty(BlockState state, Block block) {
        if (block instanceof CarpenterSlopeBlock && state.hasProperty(CarpenterSlopeBlock.SLOPE_TYPE)) {
            return cycleEnum(state, CarpenterSlopeBlock.SLOPE_TYPE);
        }
        if (block instanceof CarpenterSlopeBlock && state.hasProperty(CarpenterSlopeBlock.HALF)) {
            return cycleEnum(state, CarpenterSlopeBlock.HALF);
        }
        if (block instanceof CarpenterStairsBlock && state.hasProperty(CarpenterStairsBlock.SHAPE)) {
            return cycleEnum(state, CarpenterStairsBlock.SHAPE);
        }
        if (block instanceof CarpenterStairsBlock && state.hasProperty(CarpenterStairsBlock.HALF)) {
            return cycleEnum(state, CarpenterStairsBlock.HALF);
        }
        if (block instanceof CarpenterBlockBlock && state.hasProperty(CarpenterBlockBlock.TYPE)) {
            return cycleEnum(state, CarpenterBlockBlock.TYPE);
        }
        if (block instanceof CarpenterBarrierBlock && state.hasProperty(CarpenterBarrierBlock.BARRIER_TYPE)) {
            return cycleEnum(state, CarpenterBarrierBlock.BARRIER_TYPE);
        }
        if (block instanceof CarpenterBarrierBlock && state.hasProperty(CarpenterBarrierBlock.POST)) {
            return state.setValue(CarpenterBarrierBlock.POST, !state.getValue(CarpenterBarrierBlock.POST));
        }
        if (block instanceof CarpenterButtonBlock && state.hasProperty(CarpenterButtonBlock.POLARITY)) {
            return state.setValue(CarpenterButtonBlock.POLARITY, !state.getValue(CarpenterButtonBlock.POLARITY));
        }
        if (block instanceof CarpenterDaylightSensorBlock && state.hasProperty(CarpenterDaylightSensorBlock.SENSITIVITY)) {
            return cycleEnum(state, CarpenterDaylightSensorBlock.SENSITIVITY);
        }
        if (block instanceof CarpenterDaylightSensorBlock && state.hasProperty(CarpenterDaylightSensorBlock.INVERTED)) {
            return state.setValue(CarpenterDaylightSensorBlock.INVERTED, !state.getValue(CarpenterDaylightSensorBlock.INVERTED));
        }
        if (block instanceof CarpenterDoorBlock && state.hasProperty(CarpenterDoorBlock.DOOR_TYPE)) {
            return cycleEnum(state, CarpenterDoorBlock.DOOR_TYPE);
        }
        if (block instanceof CarpenterDoorBlock && state.hasProperty(CarpenterDoorBlock.HALF)) {
            return cycleEnum(state, CarpenterDoorBlock.HALF);
        }
        if (block instanceof CarpenterDoorBlock && state.hasProperty(CarpenterDoorBlock.HINGE)) {
            return cycleEnum(state, CarpenterDoorBlock.HINGE);
        }
        if (block instanceof CarpenterDoorBlock && state.hasProperty(CarpenterDoorBlock.RIGID)) {
            return state.setValue(CarpenterDoorBlock.RIGID, !state.getValue(CarpenterDoorBlock.RIGID));
        }
        if (block instanceof CarpenterGateBlock && state.hasProperty(CarpenterGateBlock.GATE_TYPE)) {
            return cycleEnum(state, CarpenterGateBlock.GATE_TYPE);
        }
        if (block instanceof CarpenterGateBlock && state.hasProperty(CarpenterGateBlock.OPEN)) {
            return state.setValue(CarpenterGateBlock.OPEN, !state.getValue(CarpenterGateBlock.OPEN));
        }
        if (block instanceof CarpenterHatchBlock && state.hasProperty(CarpenterHatchBlock.HATCH_TYPE)) {
            return cycleEnum(state, CarpenterHatchBlock.HATCH_TYPE);
        }
        if (block instanceof CarpenterHatchBlock && state.hasProperty(CarpenterHatchBlock.HALF)) {
            return cycleEnum(state, CarpenterHatchBlock.HALF);
        }
        if (block instanceof CarpenterHatchBlock && state.hasProperty(CarpenterHatchBlock.RIGID)) {
            return state.setValue(CarpenterHatchBlock.RIGID, !state.getValue(CarpenterHatchBlock.RIGID));
        }
        if (block instanceof CarpenterLadderBlock && state.hasProperty(CarpenterLadderBlock.LADDER_TYPE)) {
            return cycleEnum(state, CarpenterLadderBlock.LADDER_TYPE);
        }
        if (block instanceof CarpenterLeverBlock && state.hasProperty(CarpenterLeverBlock.POLARITY)) {
            return state.setValue(CarpenterLeverBlock.POLARITY, !state.getValue(CarpenterLeverBlock.POLARITY));
        }
        if (block instanceof CarpenterTorchBlock && state.hasProperty(CarpenterTorchBlock.TORCH_TYPE)) {
            return cycleEnum(state, CarpenterTorchBlock.TORCH_TYPE);
        }
        if (block instanceof CarpenterTorchBlock && state.hasProperty(CarpenterTorchBlock.SMOLDERING)) {
            return state.setValue(CarpenterTorchBlock.SMOLDERING, !state.getValue(CarpenterTorchBlock.SMOLDERING));
        }
        if (block instanceof CarpenterTorchBlock && state.hasProperty(CarpenterTorchBlock.LIT)) {
            return state.setValue(CarpenterTorchBlock.LIT, !state.getValue(CarpenterTorchBlock.LIT));
        }
        // Fallback: cycle any enum property we find
        for (Property<?> prop : state.getProperties()) {
            if (prop instanceof EnumProperty && !(prop instanceof DirectionProperty)) {
                return cycleEnumRaw(state, (EnumProperty<?>) prop);
            }
        }
        // Fallback: toggle first boolean property
        for (Property<?> prop : state.getProperties()) {
            if (prop instanceof BooleanProperty) {
                BooleanProperty bp = (BooleanProperty) prop;
                return state.setValue(bp, !state.getValue(bp));
            }
        }
        return state;
    }

    private static BlockState cycleDirection(BlockState state, DirectionProperty property) {
        Direction current = state.getValue(property);
        List<Direction> allowed = new ArrayList<>(property.getPossibleValues());
        int idx = allowed.indexOf(current);
        Direction next = allowed.get((idx + 1) % allowed.size());
        return state.setValue(property, next);
    }

    private static <T extends Enum<T> & StringRepresentable> BlockState cycleEnum(BlockState state, EnumProperty<T> property) {
        T current = state.getValue(property);
        List<T> allowed = new ArrayList<>(property.getPossibleValues());
        int idx = allowed.indexOf(current);
        T next = allowed.get((idx + 1) % allowed.size());
        return state.setValue(property, next);
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static BlockState cycleEnumRaw(BlockState state, EnumProperty property) {
        Comparable current = state.getValue(property);
        List<Comparable> allowed = new ArrayList<>(property.getPossibleValues());
        int idx = allowed.indexOf(current);
        Comparable next = allowed.get((idx + 1) % allowed.size());
        return state.setValue(property, next);
    }
}
