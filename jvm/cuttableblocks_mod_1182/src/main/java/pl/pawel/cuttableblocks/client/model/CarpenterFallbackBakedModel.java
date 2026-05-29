package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

import java.util.List;
import java.util.Random;

/**
 * Fallback BakedModel that simply renders the cover block as a full cube.
 * Used for block types whose true geometry is not yet implemented
 * (barrier, gate, door, torch, etc.).
 */
public class CarpenterFallbackBakedModel extends CarpenterBakedModel {

    public CarpenterFallbackBakedModel(BakedModel delegate) {
        super(delegate);
    }

    @Override
    protected List<BakedQuad> getQuadsForCover(BlockState carpenterState, BlockState coverState, Direction side, Random rand) {
        BakedModel coverModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(coverState);
        return coverModel.getQuads(coverState, side, rand);
    }
}
