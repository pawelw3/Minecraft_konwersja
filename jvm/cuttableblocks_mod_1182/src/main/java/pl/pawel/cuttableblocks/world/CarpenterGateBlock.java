package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterGateBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final BooleanProperty OPEN = BooleanProperty.create("open");
    public static final EnumProperty<GateType> GATE_TYPE = EnumProperty.create("gate_type", GateType.class);

    public enum GateType implements net.minecraft.util.StringRepresentable {
        TYPE_0("type_0"), TYPE_1("type_1"), TYPE_2("type_2"),
        TYPE_3("type_3"), TYPE_4("type_4"), TYPE_5("type_5"), TYPE_6("type_6");

        private final String name;
        GateType(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape Z_SHAPE = Block.box(0, 0, 6, 16, 16, 10);
    private static final VoxelShape X_SHAPE = Block.box(6, 0, 0, 10, 16, 16);
    private static final VoxelShape Z_SHAPE_LOW = Block.box(0, 0, 6, 16, 13, 10);
    private static final VoxelShape X_SHAPE_LOW = Block.box(6, 0, 0, 10, 13, 16);

    public CarpenterGateBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.NORTH)
            .setValue(OPEN, false)
            .setValue(GATE_TYPE, GateType.TYPE_0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, OPEN, GATE_TYPE);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        if (state.getValue(OPEN)) {
            return switch (state.getValue(FACING)) {
                case NORTH, SOUTH -> X_SHAPE_LOW;
                case EAST, WEST -> Z_SHAPE_LOW;
                default -> Z_SHAPE_LOW;
            };
        }
        return switch (state.getValue(FACING)) {
            case NORTH, SOUTH -> Z_SHAPE;
            case EAST, WEST -> X_SHAPE;
            default -> Z_SHAPE;
        };
    }

    @Override
    protected InteractionResult useEmptyHand(BlockState state, Level level, BlockPos pos,
                                             Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        level.setBlock(pos, state.cycle(OPEN), Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
        return InteractionResult.CONSUME;
    }
}
