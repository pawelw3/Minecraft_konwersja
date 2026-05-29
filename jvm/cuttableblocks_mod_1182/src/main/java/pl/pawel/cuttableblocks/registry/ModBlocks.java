package pl.pawel.cuttableblocks.registry;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.Material;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.world.*;

public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(ForgeRegistries.BLOCKS, CuttableBlocksMod.MODID);

    // -- Geometric CB blocks -----------------------------------------------
    public static final RegistryObject<Block> CARPENTER_SLOPE =
        BLOCKS.register("carpenter_slope",
            () -> new CarpenterSlopeBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_STAIRS =
        BLOCKS.register("carpenter_stairs",
            () -> new CarpenterStairsBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_BLOCK =
        BLOCKS.register("carpenter_block",
            () -> new CarpenterBlockBlock(carpenterProperties()));
    public static final RegistryObject<Block> COLLAPSIBLE_BLOCK =
        BLOCKS.register("collapsible_block",
            () -> new CarpenterCollapsibleBlock(carpenterProperties()));

    // -- Functional CB blocks ----------------------------------------------
    public static final RegistryObject<Block> CARPENTER_BARRIER =
        BLOCKS.register("carpenter_barrier",
            () -> new CarpenterBarrierBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_GATE =
        BLOCKS.register("carpenter_gate",
            () -> new CarpenterGateBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_HATCH =
        BLOCKS.register("carpenter_hatch",
            () -> new CarpenterHatchBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_DOOR =
        BLOCKS.register("carpenter_door",
            () -> new CarpenterDoorBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_LADDER =
        BLOCKS.register("carpenter_ladder",
            () -> new CarpenterLadderBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_LEVER =
        BLOCKS.register("carpenter_lever",
            () -> new CarpenterLeverBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_BUTTON =
        BLOCKS.register("carpenter_button",
            () -> new CarpenterButtonBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_PRESSURE_PLATE =
        BLOCKS.register("carpenter_pressure_plate",
            () -> new CarpenterPressurePlateBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_TORCH =
        BLOCKS.register("carpenter_torch",
            () -> new CarpenterTorchBlock(carpenterProperties().noOcclusion().lightLevel(s -> 14)));
    public static final RegistryObject<Block> CARPENTER_DAYLIGHT_SENSOR =
        BLOCKS.register("carpenter_daylight_sensor",
            () -> new CarpenterDaylightSensorBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_SAFE =
        BLOCKS.register("carpenter_safe",
            () -> new CarpenterSafeBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_FLOWER_POT =
        BLOCKS.register("carpenter_flower_pot",
            () -> new CarpenterFlowerPotBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_BED =
        BLOCKS.register("carpenter_bed",
            () -> new CarpenterBedBlock(carpenterProperties()));
    public static final RegistryObject<Block> CARPENTER_GARAGE_DOOR =
        BLOCKS.register("carpenter_garage_door",
            () -> new CarpenterGarageDoorBlock(carpenterProperties()));

    // -- Free-cut block (not from CB) -------------------------------------
    public static final RegistryObject<Block> CUTTABLE_BLOCK = BLOCKS.register(
        "cuttable_block",
        () -> new CuttableBlock(BlockBehaviour.Properties.of(Material.STONE)
            .strength(1.5F, 6.0F)
            .noOcclusion())
    );

    private static BlockBehaviour.Properties carpenterProperties() {
        return BlockBehaviour.Properties.of(Material.WOOD)
            .strength(1.5F, 6.0F)
            .noOcclusion();
    }

    private ModBlocks() {}
}
