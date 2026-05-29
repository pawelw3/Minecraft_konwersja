package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import pl.pawel.cuttableblocks.world.CarpenterBlockBlock;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * BakedModel for carpenter_block (full / slab variants).
 * Full block delegates directly to the cover model.
 * Slabs generate simple half-block geometry.
 */
public class CarpenterBlockBakedModel extends CarpenterBakedModel {

    public CarpenterBlockBakedModel(BakedModel delegate) {
        super(delegate);
    }

    @Override
    protected List<BakedQuad> getQuadsForCover(BlockState carpenterState, BlockState coverState, Direction side, Random rand) {
        BakedModel coverModel = Minecraft.getInstance().getBlockRenderer().getBlockModel(coverState);

        if (carpenterState == null) {
            return coverModel.getQuads(coverState, side, rand);
        }

        CarpenterBlockBlock.SlabType type = carpenterState.getValue(CarpenterBlockBlock.TYPE);
        if (type == CarpenterBlockBlock.SlabType.FULL) {
            return coverModel.getQuads(coverState, side, rand);
        }

        TextureAtlasSprite sprite = coverModel.getParticleIcon();
        if (sprite == null) {
            sprite = delegate.getParticleIcon();
        }

        List<BakedQuad> quads = new ArrayList<>();
        switch (type) {
            case SLAB_Y -> buildSlabY(quads, sprite);
            case SLAB_X -> buildSlabX(quads, sprite);
            case SLAB_Z -> buildSlabZ(quads, sprite);
        }
        return quads;
    }

    private void buildSlabY(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        float y = 0.5f;
        // bottom
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                v(0,0,0), 0, 0, v(0,0,1), 0, 1, v(1,0,1), 1, 1, v(1,0,0), 1, 0));
        // top
        quads.add(QuadBuilder.buildQuad(sprite, Direction.UP, true, -1,
                v(0,y,0), 0, 0, v(1,y,0), 1, 0, v(1,y,1), 1, 1, v(0,y,1), 0, 1));
        // north
        quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                v(0,0,0), 0, 0, v(1,0,0), 1, 0, v(1,y,0), 1, 1, v(0,y,0), 0, 1));
        // south
        quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                v(0,0,1), 0, 0, v(0,y,1), 0, 1, v(1,y,1), 1, 1, v(1,0,1), 1, 0));
        // west
        quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                v(0,0,0), 0, 0, v(0,y,0), 0, 1, v(0,y,1), 1, 1, v(0,0,1), 1, 0));
        // east
        quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                v(1,0,0), 0, 0, v(1,0,1), 1, 0, v(1,y,1), 1, 1, v(1,y,0), 0, 1));
    }

    private void buildSlabX(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        float x = 0.5f;
        // bottom
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                v(0,0,0), 0, 0, v(0,0,1), 0, 1, v(x,0,1), 1, 1, v(x,0,0), 1, 0));
        // top
        quads.add(QuadBuilder.buildQuad(sprite, Direction.UP, true, -1,
                v(0,1,0), 0, 0, v(x,1,0), 1, 0, v(x,1,1), 1, 1, v(0,1,1), 0, 1));
        // north
        quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                v(0,0,0), 0, 0, v(x,0,0), 1, 0, v(x,1,0), 1, 1, v(0,1,0), 0, 1));
        // south
        quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                v(0,0,1), 0, 0, v(0,1,1), 0, 1, v(x,1,1), 1, 1, v(x,0,1), 1, 0));
        // west (full)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                v(0,0,0), 0, 0, v(0,1,0), 0, 1, v(0,1,1), 1, 1, v(0,0,1), 1, 0));
        // east (half)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                v(x,0,0), 0, 0, v(x,0,1), 1, 0, v(x,1,1), 1, 1, v(x,1,0), 0, 1));
    }

    private void buildSlabZ(List<BakedQuad> quads, TextureAtlasSprite sprite) {
        float z = 0.5f;
        // bottom
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                v(0,0,0), 0, 0, v(0,0,z), 0, 1, v(1,0,z), 1, 1, v(1,0,0), 1, 0));
        // top
        quads.add(QuadBuilder.buildQuad(sprite, Direction.UP, true, -1,
                v(0,1,0), 0, 0, v(1,1,0), 1, 0, v(1,1,z), 1, 1, v(0,1,z), 0, 1));
        // north (half)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                v(0,0,0), 0, 0, v(1,0,0), 1, 0, v(1,1,0), 1, 1, v(0,1,0), 0, 1));
        // south (half)
        quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                v(0,0,z), 0, 0, v(0,1,z), 0, 1, v(1,1,z), 1, 1, v(1,0,z), 1, 0));
        // west
        quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                v(0,0,0), 0, 0, v(0,1,0), 0, 1, v(0,1,z), 1, 1, v(0,0,z), 1, 0));
        // east
        quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                v(1,0,0), 0, 0, v(1,0,z), 1, 0, v(1,1,z), 1, 1, v(1,1,0), 0, 1));
    }

    private static Vec3 v(double x, double y, double z) {
        return new Vec3(x, y, z);
    }
}
