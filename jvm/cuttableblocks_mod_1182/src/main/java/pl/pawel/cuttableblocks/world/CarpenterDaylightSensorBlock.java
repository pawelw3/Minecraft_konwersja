package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterDaylightSensorBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final BooleanProperty INVERTED = BooleanProperty.create("inverted");
    public static final IntegerProperty POWER = IntegerProperty.create("power", 0, 15);
    public static final EnumProperty<Sensitivity> SENSITIVITY = EnumProperty.create("sensitivity", Sensitivity.class);

    public enum Sensitivity implements net.minecraft.util.StringRepresentable {
        LOW("low"), NORMAL("normal"), HIGH("high");

        private final String name;
        Sensitivity(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 6, 16);

    public CarpenterDaylightSensorBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.NORTH)
            .setValue(INVERTED, false)
            .setValue(POWER, 0)
            .setValue(SENSITIVITY, Sensitivity.NORMAL));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, INVERTED, POWER, SENSITIVITY);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return SHAPE;
    }
}
