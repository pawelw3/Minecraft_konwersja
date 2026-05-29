package pl.pawel.cuttableblocks.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Matrix3f;
import com.mojang.math.Matrix4f;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.registries.ForgeRegistries;
import pl.pawel.cuttableblocks.client.render.CuttableGeometry;
import pl.pawel.cuttableblocks.world.CuttableBlockEntity;

import java.util.List;

/**
 * Renders a cuttable_block with arbitrary-plane geometry clipping.
 *
 * Uses the original block's particle texture for all faces.
 */
public class CuttableBlockEntityRenderer implements BlockEntityRenderer<CuttableBlockEntity> {

    public CuttableBlockEntityRenderer(BlockEntityRendererProvider.Context ctx) {
    }

    @Override
    public void render(CuttableBlockEntity be, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffer, int packedLight, int packedOverlay) {
        String originalId = be.getOriginalBlock();
        if (originalId.isEmpty()) {
            originalId = "minecraft:stone";
        }

        ResourceLocation originalLocation = ResourceLocation.tryParse(originalId);
        Block block = originalLocation != null ? ForgeRegistries.BLOCKS.getValue(originalLocation) : null;
        if (block == null || block == Blocks.AIR) {
            block = Blocks.STONE;
        }

        // Get particle texture (main texture for simple blocks)
        TextureAtlasSprite sprite = Minecraft.getInstance().getBlockRenderer()
                .getBlockModel(block.defaultBlockState()).getParticleIcon();

        List<CuttableGeometry.Vertex[]> triangles = CuttableGeometry.generateTriangles(
                be.getDirId(), be.getRotId(), be.keepPositiveSide()
        );

        if (triangles.isEmpty()) return;

        poseStack.pushPose();
        Matrix4f matrix = poseStack.last().pose();
        Matrix3f normalMatrix = poseStack.last().normal();

        VertexConsumer vc = buffer.getBuffer(RenderType.cutoutMipped());

        for (CuttableGeometry.Vertex[] tri : triangles) {
            for (CuttableGeometry.Vertex v : tri) {
                float u = sprite.getU(v.u * 16f);
                float vAt = sprite.getV(v.v * 16f);

                vc.vertex(matrix, v.x, v.y, v.z)
                        .color(255, 255, 255, 255)
                        .uv(u, vAt)
                        .overlayCoords(packedOverlay)
                        .uv2(packedLight)
                        .normal(normalMatrix, v.nx, v.ny, v.nz)
                        .endVertex();
            }
        }

        poseStack.popPose();
    }
}
