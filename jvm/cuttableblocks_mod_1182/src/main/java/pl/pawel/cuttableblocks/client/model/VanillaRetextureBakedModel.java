package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

import java.util.List;
import java.util.Random;
import java.util.function.Function;

/**
 * Generic BakedModel that copies geometry from a vanilla block and retextures it
 * with the cover block's particle sprite.  Used for stairs, doors, trapdoors,
 * levers, buttons, beds, ladders, etc.
 */
public class VanillaRetextureBakedModel extends CarpenterBakedModel {

    private final Function<BlockState, BlockState> stateMapper;

    public VanillaRetextureBakedModel(BakedModel delegate, Function<BlockState, BlockState> stateMapper) {
        super(delegate);
        this.stateMapper = stateMapper;
    }

    @Override
    protected List<BakedQuad> getQuadsForCover(BlockState carpenterState, BlockState coverState, Direction side, Random rand) {
        if (carpenterState == null) {
            return delegate.getQuads(carpenterState, side, rand);
        }
        BlockState vanillaState = stateMapper.apply(carpenterState);
        BakedModel vanillaModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(vanillaState);
        List<BakedQuad> vanillaQuads = vanillaModel.getQuads(vanillaState, side, rand);

        BakedModel coverModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(coverState);
        TextureAtlasSprite coverSprite = coverModel.getParticleIcon();
        if (coverSprite == null) {
            coverSprite = delegate.getParticleIcon();
        }

        return QuadRetexturer.retexture(vanillaQuads, coverSprite);
    }
}
