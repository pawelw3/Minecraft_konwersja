package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterBedBlock extends AbstractCarpenterBlock {

    public static final EnumProperty<net.minecraft.world.level.block.state.properties.BedPart> PART = EnumProperty.create("part", net.minecraft.world.level.block.state.properties.BedPart.class);
    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final BooleanProperty OCCUPIED = BooleanProperty.create("occupied");

    private static final VoxelShape BED_AABB = Block.box(0, 0, 0, 16, 9, 16);

    public CarpenterBedBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(PART, net.minecraft.world.level.block.state.properties.BedPart.FOOT)
            .setValue(FACING, Direction.NORTH)
            .setValue(OCCUPIED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(PART, FACING, OCCUPIED);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return BED_AABB;
    }
}
