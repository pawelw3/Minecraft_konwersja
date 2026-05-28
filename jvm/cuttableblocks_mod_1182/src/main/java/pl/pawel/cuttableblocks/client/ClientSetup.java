package pl.pawel.cuttableblocks.client;

import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.registry.ModBlockEntities;

/**
 * Client-side setup: registers BERs, creative tabs, and keybindings.
 */
@Mod.EventBusSubscriber(modid = CuttableBlocksMod.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ClientSetup {

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            BlockEntityRenderers.register(
                ModBlockEntities.CARPENTER.get(),
                CarpenterBlockEntityRenderer::new
            );
            BlockEntityRenderers.register(
                ModBlockEntities.CUTTABLE.get(),
                CuttableBlockEntityRenderer::new
            );
        });
    }
}
