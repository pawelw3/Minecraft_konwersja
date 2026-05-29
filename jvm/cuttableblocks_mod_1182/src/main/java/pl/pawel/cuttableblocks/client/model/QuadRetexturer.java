package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;

import java.util.ArrayList;
import java.util.List;

/**
 * Utility that remaps the texture atlas coordinates of existing BakedQuads
 * from one sprite onto another.  This lets us reuse vanilla block geometry
 * (stairs, doors, trapdoors, etc.) while drawing it with the Carpenter cover
 * block's texture.
 */
public final class QuadRetexturer {

    private QuadRetexturer() {}

    public static List<BakedQuad> retexture(List<BakedQuad> quads, TextureAtlasSprite newSprite) {
        List<BakedQuad> result = new ArrayList<>(quads.size());
        for (BakedQuad quad : quads) {
            TextureAtlasSprite oldSprite = quad.getSprite();
            int[] oldData = quad.getVertices();
            int[] newData = oldData.clone();

            if (oldSprite != null && oldSprite != newSprite) {
                float oldU0 = oldSprite.getU0();
                float oldU1 = oldSprite.getU1();
                float oldV0 = oldSprite.getV0();
                float oldV1 = oldSprite.getV1();
                float oldWidth = oldU1 - oldU0;
                float oldHeight = oldV1 - oldV0;

                float newU0 = newSprite.getU0();
                float newU1 = newSprite.getU1();
                float newV0 = newSprite.getV0();
                float newV1 = newSprite.getV1();
                float newWidth = newU1 - newU0;
                float newHeight = newV1 - newV0;

                for (int i = 0; i < 4; i++) {
                    int off = i * 8;
                    float oldU = Float.intBitsToFloat(oldData[off + 4]);
                    float oldV = Float.intBitsToFloat(oldData[off + 5]);

                    float uRel = (oldU - oldU0) / oldWidth;
                    float vRel = (oldV - oldV0) / oldHeight;

                    float newU = newU0 + uRel * newWidth;
                    float newV = newV0 + vRel * newHeight;

                    newData[off + 4] = Float.floatToRawIntBits(newU);
                    newData[off + 5] = Float.floatToRawIntBits(newV);
                }
            }

            result.add(new BakedQuad(newData, quad.getTintIndex(), quad.getDirection(), newSprite, quad.isShade()));
        }
        return result;
    }
}
