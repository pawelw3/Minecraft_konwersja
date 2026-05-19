package pl.pawel.minecraftkonwersja.placeholders.registry;

import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.minecraftkonwersja.placeholders.ConversionPlaceholdersMod;
import pl.pawel.minecraftkonwersja.placeholders.world.BlockEntityPlaceholderBlockEntity;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
        DeferredRegister.create(ForgeRegistries.BLOCK_ENTITIES, ConversionPlaceholdersMod.MODID);

    public static final RegistryObject<BlockEntityType<BlockEntityPlaceholderBlockEntity>> BLOCK_ENTITY_PLACEHOLDER =
        BLOCK_ENTITIES.register(
            "block_entity_placeholder",
            () -> BlockEntityType.Builder.of(
                BlockEntityPlaceholderBlockEntity::new,
                ModBlocks.BLOCK_ENTITY_PLACEHOLDER.get()
            ).build(null)
        );

    private ModBlockEntities() {
    }
}
