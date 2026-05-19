package pl.pawel.minecraftkonwersja.placeholders.registry;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.Material;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.minecraftkonwersja.placeholders.ConversionPlaceholdersMod;
import pl.pawel.minecraftkonwersja.placeholders.world.BlockEntityPlaceholderBlock;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(ForgeRegistries.BLOCKS, ConversionPlaceholdersMod.MODID);

    public static final RegistryObject<Block> BLOCK_ENTITY_PLACEHOLDER = BLOCKS.register(
        "block_entity_placeholder",
        () -> new BlockEntityPlaceholderBlock(BlockBehaviour.Properties.of(Material.METAL)
            .strength(0.5F, 6.0F)
            .noOcclusion())
    );

    private ModBlocks() {
    }
}
