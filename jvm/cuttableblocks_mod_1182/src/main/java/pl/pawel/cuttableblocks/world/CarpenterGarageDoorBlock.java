package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterGarageDoorBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final IntegerProperty PART = IntegerProperty.create("part", 0, 7);

    private static final VoxelShape NORTH_AABB = Block.box(0, 0, 13, 16, 16, 16);
    private static final VoxelShape SOUTH_AABB = Block.box(0, 0, 0, 16, 16, 3);
    private static final VoxelShape WEST_AABB  = Block.box(13, 0, 0, 16, 16, 16);
    private static final VoxelShape EAST_AABB  = Block.box(0, 0, 0, 3, 16, 16);

    public CarpenterGarageDoorBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.NORTH)
            .setValue(PART, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, PART);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return switch (state.getValue(FACING)) {
            case NORTH -> NORTH_AABB;
            case SOUTH -> SOUTH_AABB;
            case WEST -> WEST_AABB;
            case EAST -> EAST_AABB;
            default -> NORTH_AABB;
        };
    }
}
