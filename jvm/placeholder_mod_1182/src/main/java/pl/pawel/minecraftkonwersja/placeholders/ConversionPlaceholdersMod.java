package pl.pawel.minecraftkonwersja.placeholders;

import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import pl.pawel.minecraftkonwersja.placeholders.client.ClientSetup;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModBlockEntities;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModBlocks;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModItems;

@Mod(ConversionPlaceholdersMod.MODID)
public class ConversionPlaceholdersMod {
    public static final String MODID = "conversion_placeholders";

    public static final CreativeModeTab TAB = new CreativeModeTab(MODID) {
        @Override
        public ItemStack makeIcon() {
            return new ItemStack(ModItems.BLOCK_ENTITY_PLACEHOLDER.get());
        }
    };

    public ConversionPlaceholdersMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modBus);

        DistExecutor.safeRunWhenOn(Dist.CLIENT, () -> ClientSetup::register);
        MinecraftForge.EVENT_BUS.register(this);
    }
}
