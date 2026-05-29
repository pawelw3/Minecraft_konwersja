package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.world.level.block.state.StateDefinition;

public class CarpenterBlockBlock extends AbstractCarpenterBlock {

    public static final EnumProperty<SlabType> TYPE = EnumProperty.create("type", SlabType.class);

    public enum SlabType implements net.minecraft.util.StringRepresentable {
        FULL("full"),
        SLAB_X("slab_x"),
        SLAB_Y("slab_y"),
        SLAB_Z("slab_z");

        private final String name;
        SlabType(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape SHAPE_FULL = Shapes.block();
    private static final VoxelShape SHAPE_X = Block.box(0, 0, 0, 8, 16, 16);
    private static final VoxelShape SHAPE_Y = Block.box(0, 0, 0, 16, 8, 16);
    private static final VoxelShape SHAPE_Z = Block.box(0, 0, 0, 16, 16, 8);

    public CarpenterBlockBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(TYPE, SlabType.FULL));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(TYPE);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return switch (state.getValue(TYPE)) {
            case SLAB_X -> SHAPE_X;
            case SLAB_Y -> SHAPE_Y;
            case SLAB_Z -> SHAPE_Z;
            default -> SHAPE_FULL;
        };
    }
}
