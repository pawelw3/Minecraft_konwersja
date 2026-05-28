package pl.pawel.cuttableblocks.registry;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.Material;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.world.CarpenterBlock;
import pl.pawel.cuttableblocks.world.CuttableBlock;

/**
 * Block registrations for cuttableblocks mod.
 *
 * Registry ID → CB 1.7.10 counterpart:
 *   carpenter_slope          blockCarpentersSlope
 *   carpenter_stairs         blockCarpentersStairs
 *   carpenter_block          blockCarpentersBlock (slab/full)
 *   collapsible_block        blockCarpentersCollapsibleBlock
 *   carpenter_barrier        blockCarpentersBarrier
 *   carpenter_gate           blockCarpentersGate
 *   carpenter_hatch          blockCarpentersHatch
 *   carpenter_door           blockCarpentersDoor
 *   carpenter_ladder         blockCarpentersLadder
 *   carpenter_lever          blockCarpentersLever
 *   carpenter_button         blockCarpentersButton
 *   carpenter_pressure_plate blockCarpentersPressurePlate
 *   carpenter_torch          blockCarpentersTorch
 *   carpenter_daylight_sensor blockCarpentersDaylightSensor
 *   carpenter_safe           blockCarpentersSafe
 *   carpenter_flower_pot     blockCarpentersFlowerPot
 *   carpenter_bed            blockCarpentersBed
 *   carpenter_garage_door    blockCarpentersGarageDoor
 *
 *   cuttable_block           (free-cut concept, not from CB)
 */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(ForgeRegistries.BLOCKS, CuttableBlocksMod.MODID);

    // -- Geometric CB blocks -----------------------------------------------
    public static final RegistryObject<Block> CARPENTER_SLOPE =
        registerCarpenter("carpenter_slope");
    public static final RegistryObject<Block> CARPENTER_STAIRS =
        registerCarpenter("carpenter_stairs");
    public static final RegistryObject<Block> CARPENTER_BLOCK =
        registerCarpenter("carpenter_block");
    public static final RegistryObject<Block> COLLAPSIBLE_BLOCK =
        registerCarpenter("collapsible_block");

    // -- Functional CB blocks ----------------------------------------------
    public static final RegistryObject<Block> CARPENTER_BARRIER =
        registerCarpenter("carpenter_barrier");
    public static final RegistryObject<Block> CARPENTER_GATE =
        registerCarpenter("carpenter_gate");
    public static final RegistryObject<Block> CARPENTER_HATCH =
        registerCarpenter("carpenter_hatch");
    public static final RegistryObject<Block> CARPENTER_DOOR =
        registerCarpenter("carpenter_door");
    public static final RegistryObject<Block> CARPENTER_LADDER =
        registerCarpenter("carpenter_ladder");
    public static final RegistryObject<Block> CARPENTER_LEVER =
        registerCarpenter("carpenter_lever");
    public static final RegistryObject<Block> CARPENTER_BUTTON =
        registerCarpenter("carpenter_button");
    public static final RegistryObject<Block> CARPENTER_PRESSURE_PLATE =
        registerCarpenter("carpenter_pressure_plate");
    public static final RegistryObject<Block> CARPENTER_TORCH =
        registerCarpenter("carpenter_torch");
    public static final RegistryObject<Block> CARPENTER_DAYLIGHT_SENSOR =
        registerCarpenter("carpenter_daylight_sensor");
    public static final RegistryObject<Block> CARPENTER_SAFE =
        registerCarpenter("carpenter_safe");
    public static final RegistryObject<Block> CARPENTER_FLOWER_POT =
        registerCarpenter("carpenter_flower_pot");
    public static final RegistryObject<Block> CARPENTER_BED =
        registerCarpenter("carpenter_bed");
    public static final RegistryObject<Block> CARPENTER_GARAGE_DOOR =
        registerCarpenter("carpenter_garage_door");

    // -- Free-cut block (not from CB) -------------------------------------
    public static final RegistryObject<Block> CUTTABLE_BLOCK = BLOCKS.register(
        "cuttable_block",
        () -> new CuttableBlock(BlockBehaviour.Properties.of(Material.STONE)
            .strength(1.5F, 6.0F)
            .noOcclusion())
    );

    private static RegistryObject<Block> registerCarpenter(String name) {
        return BLOCKS.register(name,
            () -> new CarpenterBlock(BlockBehaviour.Properties.of(Material.WOOD)
                .strength(1.5F, 6.0F)
                .noOcclusion()));
    }

    private ModBlocks() {}
}
