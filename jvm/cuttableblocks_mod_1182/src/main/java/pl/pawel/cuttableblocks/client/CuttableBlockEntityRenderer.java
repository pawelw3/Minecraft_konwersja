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
import pl.pawel.cuttableblocks.world.CuttableBlockEntity;

/**
 * Simple fallback BER for CuttableBlockEntity.
 * Renders the original block as a full cube.  Arbitrary-plane cutting is
 * not yet rendered – this preserves the data and shows *something* in-world.
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

        Block block = ForgeRegistries.BLOCKS.getValue(new ResourceLocation(originalId));
        if (block == null || block == Blocks.AIR) {
            block = Blocks.STONE;
        }

        poseStack.pushPose();
        Minecraft.getInstance().getBlockRenderer()
            .renderSingleBlock(block.defaultBlockState(), poseStack, buffer, packedLight, packedOverlay);
        poseStack.popPose();
    }
}
