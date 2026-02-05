package com.cuttableblocks;

import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.client.ClientProxy;
import com.cuttableblocks.common.CommonProxy;
import com.cuttableblocks.items.ModItems;
import com.cuttableblocks.tileentities.ModTileEntities;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.EventHandler;
import cpw.mods.fml.common.SidedProxy;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;

@Mod(
    modid = CuttableBlocksMod.MODID,
    name = CuttableBlocksMod.NAME,
    version = CuttableBlocksMod.VERSION,
    acceptedMinecraftVersions = "[1.7.10]"
)
public class CuttableBlocksMod {
    
    public static final String MODID = "cuttableblocks";
    public static final String NAME = "Cuttable Blocks";
    public static final String VERSION = "1.0.0";
    
    @Mod.Instance(MODID)
    public static CuttableBlocksMod instance;
    
    @SidedProxy(
        clientSide = "com.cuttableblocks.client.ClientProxy",
        serverSide = "com.cuttableblocks.common.CommonProxy"
    )
    public static CommonProxy proxy;
    
    @EventHandler
    public void preInit(FMLPreInitializationEvent event) {
        // Inicjalizacja CreativeTab (musi być przed rejestracją bloków/itemów)
        CreativeTabCuttableBlocks.tabCuttableBlocks.setBackgroundImageName("item_search.png");
        
        // Proxy preInit MUSI być przed rejestracją bloków - inicjalizuje renderId
        proxy.preInit();
        
        ModBlocks.registerBlocks();
        ModItems.registerItems();
        ModTileEntities.registerTileEntities();
    }
    
    @EventHandler
    public void init(FMLInitializationEvent event) {
        proxy.init();
    }
    
    @EventHandler
    public void postInit(FMLPostInitializationEvent event) {
        proxy.postInit();
    }
}
