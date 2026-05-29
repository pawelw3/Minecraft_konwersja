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
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterButtonBlock extends AbstractCarpenterBlock {

    public static final EnumProperty<AttachFace> FACE = EnumProperty.create("face", AttachFace.class);
    public static final DirectionProperty FACING = DirectionProperty.create("facing");
    public static final BooleanProperty POWERED = BooleanProperty.create("powered");
    public static final BooleanProperty POLARITY = BooleanProperty.create("polarity");

    private static final VoxelShape CEILING_AABB_X = Block.box(6, 14, 5, 10, 16, 11);
    private static final VoxelShape CEILING_AABB_Z = Block.box(5, 14, 6, 11, 16, 10);
    private static final VoxelShape FLOOR_AABB_X   = Block.box(6, 0, 5, 10, 2, 11);
    private static final VoxelShape FLOOR_AABB_Z   = Block.box(5, 0, 6, 11, 2, 10);
    private static final VoxelShape NORTH_AABB     = Block.box(5, 6, 14, 11, 10, 16);
    private static final VoxelShape SOUTH_AABB     = Block.box(5, 6, 0, 11, 10, 2);
    private static final VoxelShape WEST_AABB      = Block.box(14, 6, 5, 16, 10, 11);
    private static final VoxelShape EAST_AABB      = Block.box(0, 6, 5, 2, 10, 11);

    public CarpenterButtonBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACE, AttachFace.WALL)
            .setValue(FACING, Direction.NORTH)
            .setValue(POWERED, false)
            .setValue(POLARITY, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACE, FACING, POWERED, POLARITY);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return switch (state.getValue(FACE)) {
            case FLOOR -> {
                Direction dir = state.getValue(FACING);
                yield (dir.getAxis() == Direction.Axis.X) ? FLOOR_AABB_X : FLOOR_AABB_Z;
            }
            case CEILING -> {
                Direction dir = state.getValue(FACING);
                yield (dir.getAxis() == Direction.Axis.X) ? CEILING_AABB_X : CEILING_AABB_Z;
            }
            case WALL -> switch (state.getValue(FACING)) {
                case NORTH -> NORTH_AABB;
                case SOUTH -> SOUTH_AABB;
                case WEST -> WEST_AABB;
                case EAST -> EAST_AABB;
                default -> NORTH_AABB;
            };
        };
    }

    @Override
    protected InteractionResult useEmptyHand(BlockState state, Level level, BlockPos pos,
                                             Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        level.setBlock(pos, state.cycle(POWERED), Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
        // TODO: schedule tick to turn off after 1s (like vanilla button)
        return InteractionResult.CONSUME;
    }
}
