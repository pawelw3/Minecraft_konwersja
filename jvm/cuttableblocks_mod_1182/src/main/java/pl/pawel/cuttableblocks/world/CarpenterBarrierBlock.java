package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterBarrierBlock extends AbstractCarpenterBlock {

    public static final EnumProperty<BarrierType> BARRIER_TYPE = EnumProperty.create("barrier_type", BarrierType.class);
    public static final BooleanProperty POST = BooleanProperty.create("post");

    public enum BarrierType implements net.minecraft.util.StringRepresentable {
        TYPE_0("type_0"), TYPE_1("type_1"), TYPE_2("type_2"),
        TYPE_3("type_3"), TYPE_4("type_4"), TYPE_5("type_5"), TYPE_6("type_6");

        private final String name;
        BarrierType(String name) { this.name = name; }
        @Override public String getSerializedName() { return name; }
    }

    private static final VoxelShape POST_SHAPE = Block.box(6, 0, 6, 10, 16, 10);
    private static final VoxelShape X_SHAPE = Block.box(0, 0, 6, 16, 16, 10);
    private static final VoxelShape Z_SHAPE = Block.box(6, 0, 0, 10, 16, 16);

    public CarpenterBarrierBlock(BlockBehaviour.Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
            .setValue(BARRIER_TYPE, BarrierType.TYPE_0)
            .setValue(POST, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(BARRIER_TYPE, POST);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        // Simple fallback: cross shape when post is true, post only otherwise
        if (state.getValue(POST)) {
            return Shapes.or(POST_SHAPE, X_SHAPE, Z_SHAPE);
        }
        return POST_SHAPE;
    }
}
