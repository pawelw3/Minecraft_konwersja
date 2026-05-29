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
import net.minecraft.world.level.block.state.properties.DoorHingeSide;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterDoorBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing", Direction.Plane.HORIZONTAL);
    public static final EnumProperty<Half> HALF = EnumProperty.create("half", Half.class);
    public static final EnumProperty<DoorHingeSide> HINGE = EnumProperty.create("hinge", DoorHingeSide.class);
    public static final BooleanProperty OPEN = BooleanProperty.create("open");
    public static final EnumProperty<DoorType> DOOR_TYPE = EnumProperty.create("door_type", DoorType.class);
    public static final BooleanProperty RIGID = BooleanProperty.create("rigid");

    public enum DoorType implements net.minecraft.util.StringRepresentable {
        TYPE_0("type_0"), TYPE_1("type_1"), TYPE_2("type_2"),
        TYPE_3("type_3"), TYPE_4("type_4"), TYPE_5("type_5");

        private final String name;
        DoorType(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape SOUTH_AABB = Block.box(0, 0, 0, 16, 16, 3);
    private static final VoxelShape NORTH_AABB = Block.box(0, 0, 13, 16, 16, 16);
    private static final VoxelShape WEST_AABB  = Block.box(13, 0, 0, 16, 16, 16);
    private static final VoxelShape EAST_AABB  = Block.box(0, 0, 0, 3, 16, 16);

    public CarpenterDoorBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.NORTH)
            .setValue(HALF, Half.BOTTOM)
            .setValue(HINGE, DoorHingeSide.LEFT)
            .setValue(OPEN, false)
            .setValue(DOOR_TYPE, DoorType.TYPE_0)
            .setValue(RIGID, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, HALF, HINGE, OPEN, DOOR_TYPE, RIGID);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return switch (state.getValue(FACING)) {
            case SOUTH -> SOUTH_AABB;
            case NORTH -> NORTH_AABB;
            case WEST -> WEST_AABB;
            case EAST -> EAST_AABB;
            default -> NORTH_AABB;
        };
    }

    @Override
    protected InteractionResult useEmptyHand(BlockState state, Level level, BlockPos pos,
                                             Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        level.setBlock(pos, state.cycle(OPEN), Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
        // TODO: also toggle the other half
        return InteractionResult.CONSUME;
    }
}
