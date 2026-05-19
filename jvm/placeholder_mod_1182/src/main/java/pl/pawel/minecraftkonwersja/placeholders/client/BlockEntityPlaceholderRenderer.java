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
        boolean inventory = blockEntity instanceof pl.pawel.minecraftkonwersja.placeholders.world.InventoryPlaceholderBlockEntity;

        renderBox(poseStack, consumer, sprite, colors, light, packedOverlay,
            inventory ? 2 : 6,
            inventory ? 14 : 10,
            inventory ? 14 : 12);
    }

    private static void renderBox(
        PoseStack poseStack,
        VertexConsumer consumer,
        TextureAtlasSprite sprite,
        int[] colors,
        int light,
        int overlay,
        int minPixel,
        int maxPixel,
        int heightPixel
    ) {
        PoseStack.Pose pose = poseStack.last();
        Matrix4f matrix = pose.pose();
        Matrix3f normal = pose.normal();
        float min = minPixel / 16.0F;
        float max = maxPixel / 16.0F;
        float height = heightPixel / 16.0F;

        renderSideX(matrix, normal, consumer, sprite, colors, light, overlay, min, false, minPixel, maxPixel, heightPixel);
        renderSideX(matrix, normal, consumer, sprite, colors, light, overlay, max, true, minPixel, maxPixel, heightPixel);
        renderSideZ(matrix, normal, consumer, sprite, colors, light, overlay, min, true, minPixel, maxPixel, heightPixel);
        renderSideZ(matrix, normal, consumer, sprite, colors, light, overlay, max, false, minPixel, maxPixel, heightPixel);
        renderTopOrBottom(matrix, normal, consumer, sprite, colors, light, overlay, 0.0F, false, minPixel, maxPixel);
        renderTopOrBottom(matrix, normal, consumer, sprite, colors, light, overlay, height, true, minPixel, maxPixel);
    }

    private static void renderSideX(Matrix4f matrix, Matrix3f normal, VertexConsumer consumer, TextureAtlasSprite sprite,
                                    int[] colors, int light, int overlay, float x, boolean east,
                                    int minPixel, int maxPixel, int heightPixel) {
        for (int y = 0; y < heightPixel; y++) {
            for (int z = minPixel; z < maxPixel; z++) {
                float y0 = y / 16.0F;
                float y1 = (y + 1) / 16.0F;
                float z0 = z / 16.0F;
                float z1 = (z + 1) / 16.0F;
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
                                    int[] colors, int light, int overlay, float z, boolean north,
                                    int minPixel, int maxPixel, int heightPixel) {
        for (int y = 0; y < heightPixel; y++) {
            for (int x = minPixel; x < maxPixel; x++) {
                float x0 = x / 16.0F;
                float x1 = (x + 1) / 16.0F;
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
                                          int[] colors, int light, int overlay, float y, boolean top,
                                          int minPixel, int maxPixel) {
        for (int x = minPixel; x < maxPixel; x++) {
            for (int z = minPixel; z < maxPixel; z++) {
                float x0 = x / 16.0F;
                float x1 = (x + 1) / 16.0F;
                float z0 = z / 16.0F;
                float z1 = (z + 1) / 16.0F;
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
