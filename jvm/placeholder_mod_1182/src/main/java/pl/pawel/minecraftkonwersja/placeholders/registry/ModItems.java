package pl.pawel.minecraftkonwersja.placeholders.registry;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.minecraftkonwersja.placeholders.ConversionPlaceholdersMod;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, ConversionPlaceholdersMod.MODID);

    public static final RegistryObject<Item> BLOCK_ENTITY_PLACEHOLDER = ITEMS.register(
        "block_entity_placeholder",
        () -> new BlockItem(ModBlocks.BLOCK_ENTITY_PLACEHOLDER.get(),
            new Item.Properties().tab(ConversionPlaceholdersMod.TAB))
    );

    private ModItems() {
    }
}
