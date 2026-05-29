package pl.pawel.cuttableblocks.world;
import net.minecraft.world.level.block.Block;

import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public class CarpenterSafeBlock extends AbstractCarpenterBlock {

    public CarpenterSafeBlock(BlockBehaviour.Properties properties) {
        super(properties);
    }

    @Override
    protected VoxelShape getCarpenterShape(BlockState state) {
        return Shapes.block();
    }
}
