package pl.pawel.minecraftkonwersja.placeholders.client;

import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModBlockEntities;

public final class ClientSetup {
    private ClientSetup() {
    }

    public static void register() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        modBus.addListener(ClientSetup::onClientSetup);
    }

    private static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> net.minecraft.client.renderer.blockentity.BlockEntityRenderers.register(
            ModBlockEntities.BLOCK_ENTITY_PLACEHOLDER.get(),
            BlockEntityPlaceholderRenderer::new
        ));
        event.enqueueWork(() -> net.minecraft.client.renderer.blockentity.BlockEntityRenderers.register(
            ModBlockEntities.INVENTORY_PLACEHOLDER.get(),
            BlockEntityPlaceholderRenderer::new
        ));
    }
}
