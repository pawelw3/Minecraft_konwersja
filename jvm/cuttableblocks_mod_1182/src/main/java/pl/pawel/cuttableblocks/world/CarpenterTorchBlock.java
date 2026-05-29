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

public class CarpenterTorchBlock extends AbstractCarpenterBlock {

    public static final DirectionProperty FACING = DirectionProperty.create("facing");
    public static final BooleanProperty LIT = BooleanProperty.create("lit");
    public static final BooleanProperty SMOLDERING = BooleanProperty.create("smoldering");
    public static final EnumProperty<TorchType> TORCH_TYPE = EnumProperty.create("torch_type", TorchType.class);

    public enum TorchType implements net.minecraft.util.StringRepresentable {
        VANILLA("vanilla"), LANTERN("lantern");

        private final String name;
        TorchType(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape AABB     = Block.box(6, 0, 6, 10, 16, 10);
    private static final VoxelShape NORTH_AABB = Block.box(5.5, 3, 11, 10.5, 13, 16);
    private static final VoxelShape SOUTH_AABB = Block.box(5.5, 3, 0, 10.5, 13, 5);
    private static final VoxelShape WEST_AABB  = Block.box(11, 3, 5.5, 16, 13, 10.5);
    private static final VoxelShape EAST_AABB  = Block.box(0, 3, 5.5, 5, 13, 10.5);

    public CarpenterTorchBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(FACING, Direction.UP)
            .setValue(LIT, true)
            .setValue(SMOLDERING, false)
            .setValue(TORCH_TYPE, TorchType.VANILLA));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, LIT, SMOLDERING, TORCH_TYPE);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return switch (state.getValue(FACING)) {
            case UP -> AABB;
            case NORTH -> NORTH_AABB;
            case SOUTH -> SOUTH_AABB;
            case WEST -> WEST_AABB;
            case EAST -> EAST_AABB;
            default -> AABB;
        };
    }
}
