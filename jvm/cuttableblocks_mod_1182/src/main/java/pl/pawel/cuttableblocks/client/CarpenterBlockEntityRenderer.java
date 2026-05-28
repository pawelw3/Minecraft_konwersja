package pl.pawel.cuttableblocks.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.registries.ForgeRegistries;
import pl.pawel.cuttableblocks.world.CarpenterBlockEntity;

/**
 * Simple fallback BER for CarpenterBlockEntity.
 * Renders the cover block as a full cube.  Geometry (slope, stairs, etc.) is
 * not yet rendered – this is a visual placeholder that guarantees the block
 * is visible in-world after conversion.
 */
public class CarpenterBlockEntityRenderer implements BlockEntityRenderer<CarpenterBlockEntity> {

    public CarpenterBlockEntityRenderer(BlockEntityRendererProvider.Context ctx) {
    }

    @Override
    public void render(CarpenterBlockEntity be, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffer, int packedLight, int packedOverlay) {
        String coverId = be.getCoverBlock();
        if (coverId.isEmpty()) {
            coverId = "minecraft:oak_planks";
        }

        Block block = ForgeRegistries.BLOCKS.getValue(new ResourceLocation(coverId));
        if (block == null || block == Blocks.AIR) {
            block = Blocks.OAK_PLANKS;
        }

        poseStack.pushPose();
        Minecraft.getInstance().getBlockRenderer()
            .renderSingleBlock(block.defaultBlockState(), poseStack, buffer, packedLight, packedOverlay);
        poseStack.popPose();
    }
}
