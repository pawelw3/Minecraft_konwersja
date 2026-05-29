package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.block.model.ItemOverrides;
import net.minecraft.client.renderer.block.model.ItemTransforms;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.EmptyModelData;
import net.minecraftforge.client.model.data.IModelData;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Base BakedModel for all Carpenter blocks.
 * Delegates to the original JSON model when no cover is present,
 * otherwise generates geometry from the cover block's texture.
 */
public abstract class CarpenterBakedModel implements BakedModel {

    protected final BakedModel delegate;
    private final Map<QuadCacheKey, List<BakedQuad>> quadCache = new HashMap<>();

    protected CarpenterBakedModel(BakedModel delegate) {
        this.delegate = delegate;
    }

    @Nonnull
    @Override
    public List<BakedQuad> getQuads(@Nullable BlockState state, @Nullable Direction side, @Nonnull Random rand, @Nonnull IModelData extraData) {
        BlockState coverState = extraData.getData(CarpenterModelData.COVER_STATE);
        if (coverState == null) {
            return delegate.getQuads(state, side, rand, extraData);
        }
        QuadCacheKey key = new QuadCacheKey(state, coverState, side);
        return quadCache.computeIfAbsent(key, k -> getQuadsForCover(k.carpenterState(), k.coverState(), k.side(), rand));
    }

    private record QuadCacheKey(@Nullable BlockState carpenterState, BlockState coverState, @Nullable Direction side) {}

    @Nonnull
    @Override
    public List<BakedQuad> getQuads(@Nullable BlockState state, @Nullable Direction side, @Nonnull Random rand) {
        return getQuads(state, side, rand, EmptyModelData.INSTANCE);
    }

    protected abstract List<BakedQuad> getQuadsForCover(@Nullable BlockState carpenterState, BlockState coverState, @Nullable Direction side, Random rand);

    @Override
    public boolean useAmbientOcclusion() {
        return delegate.useAmbientOcclusion();
    }

    @Override
    public boolean isGui3d() {
        return delegate.isGui3d();
    }

    @Override
    public boolean usesBlockLight() {
        return delegate.usesBlockLight();
    }

    @Override
    public boolean isCustomRenderer() {
        return delegate.isCustomRenderer();
    }

    @Override
    public TextureAtlasSprite getParticleIcon() {
        return delegate.getParticleIcon();
    }

    @Override
    public ItemOverrides getOverrides() {
        return delegate.getOverrides();
    }

    @Override
    public ItemTransforms getTransforms() {
        return delegate.getTransforms();
    }
}
