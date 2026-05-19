package pl.pawel.minecraftkonwersja.placeholders1710;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.EventHandler;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.registry.GameRegistry;
import net.minecraft.block.Block;
import net.minecraft.block.material.Material;
import net.minecraft.creativetab.CreativeTabs;

@Mod(
    modid = ConversionPlaceholders1710Mod.MODID,
    name = ConversionPlaceholders1710Mod.NAME,
    version = ConversionPlaceholders1710Mod.VERSION,
    acceptedMinecraftVersions = "[1.7.10]"
)
public class ConversionPlaceholders1710Mod {
    public static final String MODID = "conversionplaceholders1710";
    public static final String NAME = "Conversion Placeholders 1.7.10";
    public static final String VERSION = "1.0.0";
    public static final String PLACEHOLDER_TE_ID = "conversionplaceholders1710.block_entity_placeholder";
    public static final String LEGACY_PLACEHOLDER_TE_ID = MODID + ":block_entity_placeholder";

    public static Block blockEntityPlaceholder;

    @EventHandler
    public void preInit(FMLPreInitializationEvent event) {
        blockEntityPlaceholder = new BlockEntityPlaceholderBlock(Material.rock)
            .setUnlocalizedName("blockEntityPlaceholder")
            .setCreativeTab(CreativeTabs.tabBlock)
            .setHardness(0.8F)
            .setResistance(4.0F);
        GameRegistry.registerBlock(blockEntityPlaceholder, "block_entity_placeholder");
        GameRegistry.registerTileEntityWithAlternatives(
            TileEntityPlaceholder.class,
            PLACEHOLDER_TE_ID,
            LEGACY_PLACEHOLDER_TE_ID
        );
        event.getModLog().info(
            "Registered block conversionplaceholders1710:block_entity_placeholder and TE "
                + PLACEHOLDER_TE_ID
                + " alias "
                + LEGACY_PLACEHOLDER_TE_ID
        );
    }

    @EventHandler
    public void init(FMLInitializationEvent event) {
    }
}
