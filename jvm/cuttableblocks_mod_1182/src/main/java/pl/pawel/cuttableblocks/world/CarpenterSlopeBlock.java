package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterSlopeBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final EnumProperty<SlopeType> SLOPE_TYPE = EnumProperty.create("slope_type", SlopeType.class);
    public static final EnumProperty<Half> HALF = EnumProperty.create("half", Half.class);

    public enum SlopeType implements net.minecraft.util.StringRepresentable {
        WEDGE("wedge"),
        OBLIQUE_INT("oblique_int"),
        OBLIQUE_EXT("oblique_ext"),
        PRISM("prism"),
        PRISM_WEDGE("prism_wedge"),
        PRISM_EXT("prism_ext");

        private final String name;

        SlopeType(String name) { this.name = name; }

        @Override public String getSerializedName() { return name; }
    }

    // WEDGE approximations
    private static final VoxelShape WEDGE_BOTTOM_NORTH = Shapes.or(Block.box(0,0,0,16,8,16), Block.box(0,8,0,16,16,8));
    private static final VoxelShape WEDGE_BOTTOM_SOUTH = Shapes.or(Block.box(0,0,0,16,8,16), Block.box(0,8,8,16,16,16));
    private static final VoxelShape WEDGE_BOTTOM_WEST  = Shapes.or(Block.box(0,0,0,16,8,16), Block.box(0,8,0,8,16,16));
    private static final VoxelShape WEDGE_BOTTOM_EAST  = Shapes.or(Block.box(0,0,0,16,8,16), Block.box(8,8,0,16,16,16));
    private static final VoxelShape WEDGE_TOP_NORTH    = Shapes.or(Block.box(0,8,0,16,16,16), Block.box(0,0,0,16,8,8));
    private static final VoxelShape WEDGE_TOP_SOUTH    = Shapes.or(Block.box(0,8,0,16,16,16), Block.box(0,0,8,16,8,16));
    private static final VoxelShape WEDGE_TOP_WEST     = Shapes.or(Block.box(0,8,0,16,16,16), Block.box(0,0,0,8,8,16));
    private static final VoxelShape WEDGE_TOP_EAST     = Shapes.or(Block.box(0,8,0,16,16,16), Block.box(8,0,0,16,8,16));

    public CarpenterSlopeBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.NORTH)
            .setValue(SLOPE_TYPE, SlopeType.WEDGE)
            .setValue(HALF, Half.BOTTOM));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, SLOPE_TYPE, HALF);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        if (state.getValue(SLOPE_TYPE) != SlopeType.WEDGE) {
            return Shapes.block();
        }
        boolean top = state.getValue(HALF) == Half.TOP;
        return switch (state.getValue(FACING)) {
            case NORTH -> top ? WEDGE_TOP_NORTH : WEDGE_BOTTOM_NORTH;
            case SOUTH -> top ? WEDGE_TOP_SOUTH : WEDGE_BOTTOM_SOUTH;
            case WEST  -> top ? WEDGE_TOP_WEST  : WEDGE_BOTTOM_WEST;
            case EAST  -> top ? WEDGE_TOP_EAST  : WEDGE_BOTTOM_EAST;
            default -> Shapes.block();
        };
    }
}
