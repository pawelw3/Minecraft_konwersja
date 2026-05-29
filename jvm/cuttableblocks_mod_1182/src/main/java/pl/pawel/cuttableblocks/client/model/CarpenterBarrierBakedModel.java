package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import pl.pawel.cuttableblocks.world.CarpenterBarrierBlock;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * BakedModel for carpenter_barrier.
 * Renders a central post plus cross bars (X and Z).  This is a simplified
 * representation; per-side connections (BARRIER_TYPE) can be refined later.
 */
public class CarpenterBarrierBakedModel extends CarpenterBakedModel {

    public CarpenterBarrierBakedModel(BakedModel delegate) {
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
        if (carpenterState == null) return quads;

        boolean post = carpenterState.getValue(CarpenterBarrierBlock.POST);

        // Central post: 6..10 in X and Z
        if (post) {
            addBox(quads, sprite, 6 / 16f, 0f, 6 / 16f, 10 / 16f, 1f, 10 / 16f);
        }

        // Horizontal bars (full width / depth)
        addBox(quads, sprite, 0f, 0f, 6 / 16f, 1f, 1f, 10 / 16f); // X-aligned
        addBox(quads, sprite, 6 / 16f, 0f, 0f, 10 / 16f, 1f, 1f); // Z-aligned

        return quads;
    }

    /** Generates the 6 faces of an axis-aligned box. */
    private static void addBox(List<BakedQuad> quads, TextureAtlasSprite sprite,
                               float x1, float y1, float z1,
                               float x2, float y2, float z2) {
        // Down
        quads.add(QuadBuilder.buildQuad(sprite, Direction.DOWN, true, -1,
                v(x1, y1, z1), 0, 0, v(x1, y1, z2), 0, 1, v(x2, y1, z2), 1, 1, v(x2, y1, z1), 1, 0));
        // Up
        quads.add(QuadBuilder.buildQuad(sprite, Direction.UP, true, -1,
                v(x1, y2, z1), 0, 0, v(x2, y2, z1), 1, 0, v(x2, y2, z2), 1, 1, v(x1, y2, z2), 0, 1));
        // North
        quads.add(QuadBuilder.buildQuad(sprite, Direction.NORTH, true, -1,
                v(x1, y1, z1), 0, 0, v(x2, y1, z1), 1, 0, v(x2, y2, z1), 1, 1, v(x1, y2, z1), 0, 1));
        // South
        quads.add(QuadBuilder.buildQuad(sprite, Direction.SOUTH, true, -1,
                v(x1, y1, z2), 0, 0, v(x1, y2, z2), 0, 1, v(x2, y2, z2), 1, 1, v(x2, y1, z2), 1, 0));
        // West
        quads.add(QuadBuilder.buildQuad(sprite, Direction.WEST, true, -1,
                v(x1, y1, z1), 0, 0, v(x1, y2, z1), 0, 1, v(x1, y2, z2), 1, 1, v(x1, y1, z2), 1, 0));
        // East
        quads.add(QuadBuilder.buildQuad(sprite, Direction.EAST, true, -1,
                v(x2, y1, z1), 0, 0, v(x2, y1, z2), 1, 0, v(x2, y2, z2), 1, 1, v(x2, y2, z1), 0, 1));
    }

    private static Vec3 v(double x, double y, double z) {
        return new Vec3(x, y, z);
    }
}
