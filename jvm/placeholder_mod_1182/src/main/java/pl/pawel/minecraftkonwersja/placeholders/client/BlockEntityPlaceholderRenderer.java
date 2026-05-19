package pl.pawel.minecraftkonwersja.placeholders.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Matrix3f;
import com.mojang.math.Matrix4f;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.Material;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.InventoryMenu;
import pl.pawel.minecraftkonwersja.placeholders.world.BlockEntityPlaceholderBlockEntity;

public class BlockEntityPlaceholderRenderer implements BlockEntityRenderer<BlockEntityPlaceholderBlockEntity> {
    private static final float MIN = 6.0F / 16.0F;
    private static final float MAX = 10.0F / 16.0F;
    private static final float HEIGHT = 12.0F / 16.0F;
    private static final Material WHITE_CONCRETE =
        new Material(InventoryMenu.BLOCK_ATLAS, new ResourceLocation("minecraft:block/white_concrete"));

    public BlockEntityPlaceholderRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(
        BlockEntityPlaceholderBlockEntity blockEntity,
        float partialTicks,
        PoseStack poseStack,
        MultiBufferSource buffers,
        int packedLight,
        int packedOverlay
    ) {
        int[] colors = PlaceholderColors.colorsFor(
            blockEntity.getSourceMod(),
            blockEntity.getSourceTeId(),
            blockEntity.getSourceBlockId()
        );
        TextureAtlasSprite sprite = WHITE_CONCRETE.sprite();
        VertexConsumer consumer = buffers.getBuffer(RenderType.solid());
        int light = Math.max(packedLight, LightTexture.FULL_BRIGHT);

        renderColumn(poseStack, consumer, sprite, colors, light, packedOverlay);
    }

    private static void renderColumn(
        PoseStack poseStack,
        VertexConsumer consumer,
        TextureAtlasSprite sprite,
        int[] colors,
        int light,
        int overlay
    ) {
        PoseStack.Pose pose = poseStack.last();
        Matrix4f matrix = pose.pose();
        Matrix3f normal = pose.normal();

        renderSideX(matrix, normal, consumer, sprite, colors, light, overlay, MIN, false);
        renderSideX(matrix, normal, consumer, sprite, colors, light, overlay, MAX, true);
        renderSideZ(matrix, normal, consumer, sprite, colors, light, overlay, MIN, true);
        renderSideZ(matrix, normal, consumer, sprite, colors, light, overlay, MAX, false);
        renderTopOrBottom(matrix, normal, consumer, sprite, colors, light, overlay, 0.0F, false);
        renderTopOrBottom(matrix, normal, consumer, sprite, colors, light, overlay, HEIGHT, true);
    }

    private static void renderSideX(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, TextureAtlasSprite sprite,
                                    int[] colors, int light, int overlay, float x, boolean east) {
        for (int y = 0; y < 12; y++) {
            for (int z = 0; z < 4; z++) {
                float y0 = y / 16.0F;
                float y1 = (y + 1) / 16.0F;
                float z0 = (6 + z) / 16.0F;
                float z1 = (7 + z) / 16.0F;
                int color = patternColor(colors, z, y);
                if (east) {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x, y0, z0, x, y0, z1, x, y1, z1, x, y1, z0, 1, 0, 0);
                } else {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x, y0, z1, x, y0, z0, x, y1, z0, x, y1, z1, -1, 0, 0);
                }
            }
        }
    }

    private static void renderSideZ(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, TextureAtlasSprite sprite,
                                    int[] colors, int light, int overlay, float z, boolean north) {
        for (int y = 0; y < 12; y++) {
            for (int x = 0; x < 4; x++) {
                float x0 = (6 + x) / 16.0F;
                float x1 = (7 + x) / 16.0F;
                float y0 = y / 16.0F;
                float y1 = (y + 1) / 16.0F;
                int color = patternColor(colors, x, y);
                if (north) {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x1, y0, z, x0, y0, z, x0, y1, z, x1, y1, z, 0, 0, -1);
                } else {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x0, y0, z, x1, y0, z, x1, y1, z, x0, y1, z, 0, 0, 1);
                }
            }
        }
    }

    private static void renderTopOrBottom(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, TextureAtlasSprite sprite,
                                          int[] colors, int light, int overlay, float y, boolean top) {
        for (int x = 0; x < 4; x++) {
            for (int z = 0; z < 4; z++) {
                float x0 = (6 + x) / 16.0F;
                float x1 = (7 + x) / 16.0F;
                float z0 = (6 + z) / 16.0F;
                float z1 = (7 + z) / 16.0F;
                int color = patternColor(colors, x, z);
                if (top) {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x0, y, z0, x1, y, z0, x1, y, z1, x0, y, z1, 0, 1, 0);
                } else {
                    quad(matrix, normal, consumer, sprite, color, light, overlay, x0, y, z1, x1, y, z1, x1, y, z0, x0, y, z0, 0, -1, 0);
                }
            }
        }
    }

    private static int patternColor(int[] colors, int u, int v) {
        int index = ((u & 1) == 1 && (v & 1) == 1) ? 3 : ((u & 1) + ((v & 1) * 2));
        return colors[index];
    }

    private static void quad(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, TextureAtlasSprite sprite,
                             int color, int light, int overlay,
                             float x0, float y0, float z0,
                             float x1, float y1, float z1,
                             float x2, float y2, float z2,
                             float x3, float y3, float z3,
                             float nx, float ny, float nz) {
        float u0 = sprite.getU0();
        float u1 = sprite.getU1();
        float v0 = sprite.getV0();
        float v1 = sprite.getV1();
        vertex(matrix, normal, consumer, color, light, overlay, x0, y0, z0, u0, v1, nx, ny, nz);
        vertex(matrix, normal, consumer, color, light, overlay, x1, y1, z1, u1, v1, nx, ny, nz);
        vertex(matrix, normal, consumer, color, light, overlay, x2, y2, z2, u1, v0, nx, ny, nz);
        vertex(matrix, normal, consumer, color, light, overlay, x3, y3, z3, u0, v0, nx, ny, nz);
        vertex(matrix, normal, consumer, color, light, overlay, x3, y3, z3, u0, v0, -nx, -ny, -nz);
        vertex(matrix, normal, consumer, color, light, overlay, x2, y2, z2, u1, v0, -nx, -ny, -nz);
        vertex(matrix, normal, consumer, color, light, overlay, x1, y1, z1, u1, v1, -nx, -ny, -nz);
        vertex(matrix, normal, consumer, color, light, overlay, x0, y0, z0, u0, v1, -nx, -ny, -nz);
    }

    private static void vertex(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, int color, int light, int overlay,
                               float x, float y, float z, float u, float v, float nx, float ny, float nz) {
        float r = ((color >> 16) & 0xFF) / 255.0F;
        float g = ((color >> 8) & 0xFF) / 255.0F;
        float b = (color & 0xFF) / 255.0F;
        consumer.vertex(matrix, x, y, z)
            .color(r, g, b, 1.0F)
            .uv(u, v)
            .overlayCoords(overlay)
            .uv2(light)
            .normal(normal, nx, ny, nz)
            .endVertex();
    }
}
