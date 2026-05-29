package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterFlowerPotBlock extends AbstractCarpenterBlock {

    private static final VoxelShape SHAPE = Block.box(5, 0, 5, 11, 6, 11);

    public CarpenterFlowerPotBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return SHAPE;
    }
}
