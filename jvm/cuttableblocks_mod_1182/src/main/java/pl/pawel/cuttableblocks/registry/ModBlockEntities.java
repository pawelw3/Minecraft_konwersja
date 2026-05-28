package pl.pawel.cuttableblocks.registry;

import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.world.CarpenterBlockEntity;
import pl.pawel.cuttableblocks.world.CuttableBlockEntity;

/**
 * Two BlockEntity types mirroring the 1.7.10 new_mod_trial structure:
 *
 *   CARPENTER (CarpenterBlockEntity) — all 18 carpenter_* + collapsible_block
 *             Matches TileEntityCoverable / TileEntityCollapsible from 1.7.10.
 *
 *   CUTTABLE  (CuttableBlockEntity)  — cuttable_block (free-cut)
 *             Matches TileEntityCuttable from 1.7.10.
 */
public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
        DeferredRegister.create(ForgeRegistries.BLOCK_ENTITIES, CuttableBlocksMod.MODID);

    public static final RegistryObject<BlockEntityType<CarpenterBlockEntity>> CARPENTER =
        BLOCK_ENTITIES.register(
            "carpenter",
            () -> BlockEntityType.Builder.of(
                CarpenterBlockEntity::new,
                ModBlocks.CARPENTER_SLOPE.get(),
                ModBlocks.CARPENTER_STAIRS.get(),
                ModBlocks.CARPENTER_BLOCK.get(),
                ModBlocks.COLLAPSIBLE_BLOCK.get(),
                ModBlocks.CARPENTER_BARRIER.get(),
                ModBlocks.CARPENTER_GATE.get(),
                ModBlocks.CARPENTER_HATCH.get(),
                ModBlocks.CARPENTER_DOOR.get(),
                ModBlocks.CARPENTER_LADDER.get(),
                ModBlocks.CARPENTER_LEVER.get(),
                ModBlocks.CARPENTER_BUTTON.get(),
                ModBlocks.CARPENTER_PRESSURE_PLATE.get(),
                ModBlocks.CARPENTER_TORCH.get(),
                ModBlocks.CARPENTER_DAYLIGHT_SENSOR.get(),
                ModBlocks.CARPENTER_SAFE.get(),
                ModBlocks.CARPENTER_FLOWER_POT.get(),
                ModBlocks.CARPENTER_BED.get(),
                ModBlocks.CARPENTER_GARAGE_DOOR.get()
            ).build(null)
        );

    public static final RegistryObject<BlockEntityType<CuttableBlockEntity>> CUTTABLE =
        BLOCK_ENTITIES.register(
            "cuttable",
            () -> BlockEntityType.Builder.of(
                CuttableBlockEntity::new,
                ModBlocks.CUTTABLE_BLOCK.get()
            ).build(null)
        );

    private ModBlockEntities() {}
}
