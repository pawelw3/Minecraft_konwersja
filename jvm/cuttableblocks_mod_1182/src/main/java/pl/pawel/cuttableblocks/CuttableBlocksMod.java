package pl.pawel.cuttableblocks;

import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import pl.pawel.cuttableblocks.registry.ModBlockEntities;
import pl.pawel.cuttableblocks.registry.ModBlocks;
import pl.pawel.cuttableblocks.registry.ModItems;

@Mod(CuttableBlocksMod.MODID)
public class CuttableBlocksMod {
    public static final String MODID = "cuttableblocks";

    public static final CreativeModeTab TAB = new CreativeModeTab(MODID) {
        @Override
        public ItemStack makeIcon() {
            return new ItemStack(ModItems.CARPENTER_SLOPE.get());
        }
    };

    public CuttableBlocksMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modBus);
        MinecraftForge.EVENT_BUS.register(this);
    }
}
