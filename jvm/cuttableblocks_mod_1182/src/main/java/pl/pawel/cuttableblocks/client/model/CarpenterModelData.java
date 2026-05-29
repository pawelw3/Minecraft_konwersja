package pl.pawel.cuttableblocks.client.model;

import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelDataMap;
import net.minecraftforge.client.model.data.ModelProperty;

public final class CarpenterModelData {
    public static final ModelProperty<BlockState> COVER_STATE = new ModelProperty<>();
    public static final ModelProperty<int[]> QUAD_DEPTHS = new ModelProperty<>();

    private CarpenterModelData() {}

    public static ModelDataMap create(BlockState coverState) {
        return new ModelDataMap.Builder()
                .withInitial(COVER_STATE, coverState)
                .build();
    }

    public static ModelDataMap create(BlockState coverState, int[] quadDepths) {
        return new ModelDataMap.Builder()
                .withInitial(COVER_STATE, coverState)
                .withInitial(QUAD_DEPTHS, quadDepths)
                .build();
    }
}
