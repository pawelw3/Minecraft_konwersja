package pl.pawel.cuttableblocks.client.model;

import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.Vec3;

/**
 * Helper for constructing BakedQuad instances from explicit vertex positions.
 * Inspired by FramedBlocks' quad generation, but written from scratch for
 * CuttableBlocks (keeps licensing simple).
 */
public final class QuadBuilder {

    private QuadBuilder() {}

    public static BakedQuad buildQuad(
            TextureAtlasSprite sprite,
            Direction face,
            boolean shade,
            int tintIndex,
            Vec3 p1, float u1, float v1,
            Vec3 p2, float u2, float v2,
            Vec3 p3, float u3, float v3,
            Vec3 p4, float u4, float v4
    ) {
        int[] data = new int[32];
        putVertex(data, 0, p1.x, p1.y, p1.z, u1, v1, sprite);
        putVertex(data, 1, p2.x, p2.y, p2.z, u2, v2, sprite);
        putVertex(data, 2, p3.x, p3.y, p3.z, u3, v3, sprite);
        putVertex(data, 3, p4.x, p4.y, p4.z, u4, v4, sprite);

        Vec3 e1 = p2.subtract(p1);
        Vec3 e2 = p3.subtract(p1);
        Vec3 n = e1.cross(e2).normalize();
        int normalPacked = packNormal((float) n.x, (float) n.y, (float) n.z);
        for (int i = 0; i < 4; i++) {
            data[i * 8 + 7] = normalPacked;
        }

        return new BakedQuad(data, tintIndex, face, sprite, shade);
    }

    private static void putVertex(int[] data, int idx,
                                  double x, double y, double z,
                                  float u, float v,
                                  TextureAtlasSprite sprite) {
        int i = idx * 8;
        data[i + 0] = Float.floatToRawIntBits((float) x);
        data[i + 1] = Float.floatToRawIntBits((float) y);
        data[i + 2] = Float.floatToRawIntBits((float) z);
        data[i + 3] = 0xFFFFFFFF;
        data[i + 4] = Float.floatToRawIntBits(sprite.getU(u * 16.0F));
        data[i + 5] = Float.floatToRawIntBits(sprite.getV(v * 16.0F));
        data[i + 6] = 0;
        data[i + 7] = 0;
    }

    private static int packNormal(float x, float y, float z) {
        int nx = ((byte) (x * 127.0F)) & 0xFF;
        int ny = ((byte) (y * 127.0F)) & 0xFF;
        int nz = ((byte) (z * 127.0F)) & 0xFF;
        return nx | (ny << 8) | (nz << 16);
    }
}
