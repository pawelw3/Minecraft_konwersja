package pl.pawel.cuttableblocks.registry;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.items.CarpenterHammer;
import pl.pawel.cuttableblocks.items.CuttingTool;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, CuttableBlocksMod.MODID);

    // Carpenter blocks (18 CB counterparts)
    public static final RegistryObject<Item> CARPENTER_SLOPE =
        fromBlock(ModBlocks.CARPENTER_SLOPE, "carpenter_slope");
    public static final RegistryObject<Item> CARPENTER_STAIRS =
        fromBlock(ModBlocks.CARPENTER_STAIRS, "carpenter_stairs");
    public static final RegistryObject<Item> CARPENTER_BLOCK =
        fromBlock(ModBlocks.CARPENTER_BLOCK, "carpenter_block");
    public static final RegistryObject<Item> COLLAPSIBLE_BLOCK =
        fromBlock(ModBlocks.COLLAPSIBLE_BLOCK, "collapsible_block");
    public static final RegistryObject<Item> CARPENTER_BARRIER =
        fromBlock(ModBlocks.CARPENTER_BARRIER, "carpenter_barrier");
    public static final RegistryObject<Item> CARPENTER_GATE =
        fromBlock(ModBlocks.CARPENTER_GATE, "carpenter_gate");
    public static final RegistryObject<Item> CARPENTER_HATCH =
        fromBlock(ModBlocks.CARPENTER_HATCH, "carpenter_hatch");
    public static final RegistryObject<Item> CARPENTER_DOOR =
        fromBlock(ModBlocks.CARPENTER_DOOR, "carpenter_door");
    public static final RegistryObject<Item> CARPENTER_LADDER =
        fromBlock(ModBlocks.CARPENTER_LADDER, "carpenter_ladder");
    public static final RegistryObject<Item> CARPENTER_LEVER =
        fromBlock(ModBlocks.CARPENTER_LEVER, "carpenter_lever");
    public static final RegistryObject<Item> CARPENTER_BUTTON =
        fromBlock(ModBlocks.CARPENTER_BUTTON, "carpenter_button");
    public static final RegistryObject<Item> CARPENTER_PRESSURE_PLATE =
        fromBlock(ModBlocks.CARPENTER_PRESSURE_PLATE, "carpenter_pressure_plate");
    public static final RegistryObject<Item> CARPENTER_TORCH =
        fromBlock(ModBlocks.CARPENTER_TORCH, "carpenter_torch");
    public static final RegistryObject<Item> CARPENTER_DAYLIGHT_SENSOR =
        fromBlock(ModBlocks.CARPENTER_DAYLIGHT_SENSOR, "carpenter_daylight_sensor");
    public static final RegistryObject<Item> CARPENTER_SAFE =
        fromBlock(ModBlocks.CARPENTER_SAFE, "carpenter_safe");
    public static final RegistryObject<Item> CARPENTER_FLOWER_POT =
        fromBlock(ModBlocks.CARPENTER_FLOWER_POT, "carpenter_flower_pot");
    public static final RegistryObject<Item> CARPENTER_BED =
        fromBlock(ModBlocks.CARPENTER_BED, "carpenter_bed");
    public static final RegistryObject<Item> CARPENTER_GARAGE_DOOR =
        fromBlock(ModBlocks.CARPENTER_GARAGE_DOOR, "carpenter_garage_door");

    // Free-cut block
    public static final RegistryObject<Item> CUTTABLE_BLOCK =
        fromBlock(ModBlocks.CUTTABLE_BLOCK, "cuttable_block");

    // Tools
    public static final RegistryObject<Item> CUTTING_TOOL =
        ITEMS.register("cutting_tool",
            () -> new CuttingTool(new Item.Properties().tab(CuttableBlocksMod.TAB).durability(256)));

    public static final RegistryObject<Item> CARPENTER_HAMMER =
        ITEMS.register("carpenter_hammer",
            () -> new CarpenterHammer(new Item.Properties().tab(CuttableBlocksMod.TAB).durability(256)));

    private static RegistryObject<Item> fromBlock(RegistryObject<? extends Block> block, String name) {
        return ITEMS.register(name,
            () -> new BlockItem(block.get(), new Item.Properties().tab(CuttableBlocksMod.TAB)));
    }

    private ModItems() {}
}
