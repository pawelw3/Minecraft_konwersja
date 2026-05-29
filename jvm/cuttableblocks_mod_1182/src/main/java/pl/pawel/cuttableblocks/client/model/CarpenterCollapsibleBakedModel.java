package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.model.data.IModelData;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * BakedModel for collapsible_block.
 * Generates a surface whose 4 corner heights are driven by quadDepths from the
 * BlockEntity (packed into IModelData).  The top is tessellated as 4 triangles
 * meeting at the centre so it renders correctly even when the corners are at
 * different heights.
 */
public class CarpenterCollapsibleBakedModel extends CarpenterBakedModel {

    public CarpenterCollapsibleBakedModel(BakedModel delegate) {
        super(delegate);
    }

    @Override
    protected List<BakedQuad> getQuadsForCover(@Nullable BlockState carpenterState, BlockState coverState, @Nullable Direction side, Random rand) {
        return delegate.getQuads(carpenterState, side, rand);
    }

    @Override
    @Nonnull
    public List<BakedQuad> getQuads(@Nullable BlockState state, @Nullable Direction side, @Nonnull Random rand, @Nonnull IModelData extraData) {
        BlockState coverState = extraData.getData(CarpenterModelData.COVER_STATE);
        int[] depths = extraData.getData(CarpenterModelData.QUAD_DEPTHS);
        if (coverState == null || depths == null) {
            return delegate.getQuads(state, side, rand, extraData);
        }

        BakedModel coverModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(coverState);
        TextureAtlasSprite sprite = coverModel.getParticleIcon();
        if (sprite == null) {
            sprite = delegate.getParticleIcon();
        }

        float h00 = depths[0] / 16.0f; // XZNN = north-west  (x=0, z=0)
        float h01 = depths[1] / 16.0f; // XZNP = south-west  (x=0, z=1)
        float h10 = depths[2] / 16.0f; // XZPN = north-east  (x=1, z=0)
        float h11 = depths[3] / 16.0f; // XZPP = south-east  (x=1, z=1)

        List<BakedQuad> quads = new ArrayList<>();

        // Bottom face (full)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                v(0, 0, 0), 0, 0, v(0, 0, 1), 0, 1, v(1, 0, 1), 1, 1, v(1, 0, 0), 1, 0));

        // Top face: 4 triangles radiating from centre (copes with non-planar corners)
        Vec3 nw = v(0, h00, 0);
        Vec3 sw = v(0, h01, 1);
        Vec3 se = v(1, h11, 1);
        Vec3 ne = v(1, h10, 0);
        Vec3 centre = v(0.5, (h00 + h01 + h10 + h11) * 0.25f, 0.5);

        quads.add(triangle(sprite, nw, sw, centre));
        quads.add(triangle(sprite, sw, se, centre));
        quads.add(triangle(sprite, se, ne, centre));
        quads.add(triangle(sprite, ne, nw, centre));

        // North face (trapezoid)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                v(0, 0, 0), 0, 0, v(1, 0, 0), 1, 0, v(1, h10, 0), 1, 1, v(0, h00, 0), 0, 1));

        // South face
        quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                v(0, 0, 1), 0, 0, v(0, h01, 1), 0, 1, v(1, h11, 1), 1, 1, v(1, 0, 1), 1, 0));

        // West face
        quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                v(0, 0, 0), 0, 0, v(0, h00, 0), 0, 1, v(0, h01, 1), 1, 1, v(0, 0, 1), 1, 0));

        // East face
        quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                v(1, 0, 0), 0, 0, v(1, 0, 1), 1, 0, v(1, h11, 1), 1, 1, v(1, h10, 0), 0, 1));

        return quads;
    }

    private static BakedQuad triangle(TextureAtlasSprite sprite, Vec3 a, Vec3 b, Vec3 c) {
        // Degenerate quad (a, b, c, c) – Minecraft renders triangles fine this way
        return QuadBuilder.buildQuad(sprite, null, true, -1,
                a, 0, 0,
                b, 1, 0,
                c, 0.5f, 1,
                c, 0.5f, 1);
    }

    private static Vec3 v(double x, double y, double z) {
        return new Vec3(x, y, z);
    }
}
