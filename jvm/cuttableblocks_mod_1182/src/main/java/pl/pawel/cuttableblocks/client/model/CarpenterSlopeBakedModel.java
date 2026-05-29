package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import pl.pawel.cuttableblocks.world.CarpenterSlopeBlock;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * BakedModel for carpenter_slope.
 * Generates true wedge / slope geometry using the cover block's particle texture.
 * Only WEDGE is fully implemented; other slope types fall back to wedge.
 */
public class CarpenterSlopeBakedModel extends CarpenterBakedModel {

    public CarpenterSlopeBakedModel(BakedModel delegate) {
        super(delegate);
    }

    @Override
    protected List<BakedQuad> getQuadsForCover(BlockState carpenterState, BlockState coverState, Direction side, Random rand) {
        BakedModel coverModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(coverState);
        TextureAtlasSprite sprite = coverModel.getParticleIcon();
        if (sprite == null) {
            sprite = delegate.getParticleIcon();
        }

        List<BakedQuad> quads = new ArrayList<>();
        if (carpenterState == null) {
            return quads;
        }

        Direction facing = carpenterState.getValue(CarpenterSlopeBlock.FACING);
        // Half is ignored for now (bottom assumed); can be extended later.

        switch (facing) {
            case NORTH -> buildWedgeNorth(quads, sprite);
            case SOUTH -> buildWedgeSouth(quads, sprite);
            case WEST  -> buildWedgeWest(quads, sprite);
            case EAST  -> buildWedgeEast(quads, sprite);
            default    -> buildWedgeNorth(quads, sprite);
        }
        return quads;
    }

    /* --------------------------------------------------------------------- */
    /*  Wedge builders per facing                                            */
    /* --------------------------------------------------------------------- */

    private void buildWedgeNorth(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        // Back edge (z=0) is high, front edge (z=1) is low.
        Vec3 bsw = v(0, 0, 0), bse = v(1, 0, 0), bne = v(1, 0, 1), bnw = v(0, 0, 1);
        Vec3 tsw = v(0, 1, 0), tse = v(1, 1, 0), tne = v(1, 0, 1), tnw = v(0, 0, 1);
        buildWedgeGeneric(quads, sprite, bsw, bse, bne, bnw, tsw, tse, tne, tnw);
    }

    private void buildWedgeSouth(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        // Front edge (z=1) is high, back edge (z=0) is low.
        Vec3 bsw = v(0, 0, 0), bse = v(1, 0, 0), bne = v(1, 0, 1), bnw = v(0, 0, 1);
        Vec3 tsw = v(0, 0, 0), tse = v(1, 0, 0), tne = v(1, 1, 1), tnw = v(0, 1, 1);
        buildWedgeGeneric(quads, sprite, bsw, bse, bne, bnw, tsw, tse, tne, tnw);
    }

    private void buildWedgeWest(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        // Left edge (x=0) is high, right edge (x=1) is low.
        Vec3 bsw = v(0, 0, 0), bse = v(1, 0, 0), bne = v(1, 0, 1), bnw = v(0, 0, 1);
        Vec3 tsw = v(0, 1, 0), tse = v(1, 0, 0), tne = v(1, 0, 1), tnw = v(0, 1, 1);
        buildWedgeGeneric(quads, sprite, bsw, bse, bne, bnw, tsw, tse, tne, tnw);
    }

    private void buildWedgeEast(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        // Right edge (x=1) is high, left edge (x=0) is low.
        Vec3 bsw = v(0, 0, 0), bse = v(1, 0, 0), bne = v(1, 0, 1), bnw = v(0, 0, 1);
        Vec3 tsw = v(0, 0, 0), tse = v(1, 1, 0), tne = v(1, 1, 1), tnw = v(0, 0, 1);
        buildWedgeGeneric(quads, sprite, bsw, bse, bne, bnw, tsw, tse, tne, tnw);
    }

    /* --------------------------------------------------------------------- */
    /*  Generic wedge generator                                              */
    /* --------------------------------------------------------------------- */

    private void buildWedgeGeneric(List<BakedQuad> quads, TextureAtlasSprite sprite,
                                   Vec3 bsw, Vec3 bse, Vec3 bne, Vec3 bnw,
                                   Vec3 tsw, Vec3 tse, Vec3 tne, Vec3 tnw) {
        // Bottom face
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                bsw, 0, 0, bse, 1, 0, bne, 1, 1, bnw, 0, 1));

        // Slope face (not axis-aligned => face=null so it never gets culled)
        quads.add(QuadBuilder.buildQuad(sprite, null, true, -1,
                bnw, 0, 1, bne, 1, 1, tse, 1, 0, tsw, 0, 0));

        // North face (only if it has area)
        if (!tsw.equals(bsw) || !tse.equals(bse)) {
            quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                    bsw, 0, 0, tsw, 0, 1, tse, 1, 1, bse, 1, 0));
        }

        // South face
        if (!tnw.equals(bnw) || !tne.equals(bne)) {
            quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                    bnw, 0, 1, bne, 1, 1, tne, 1, 0, tnw, 0, 0));
        }

        // West face
        if (!tsw.equals(bsw) || !tnw.equals(bnw)) {
            quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                    bsw, 0, 0, bnw, 1, 0, tnw, 1, 1, tsw, 0, 1));
        }

        // East face
        if (!tse.equals(bse) || !tne.equals(bne)) {
            quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                    bse, 0, 0, tse, 0, 1, tne, 1, 1, bne, 1, 0));
        }
    }

    private static Vec3 v(double x, double y, double z) {
        return new Vec3(x, y, z);
    }
}
