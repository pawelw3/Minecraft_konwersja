package com.cuttableblocks.items;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import cpw.mods.fml.common.registry.GameRegistry;
import net.minecraft.item.Item;

public class ModItems {
    
    public static Item cuttingTool;
    
    public static void registerItems() {
        cuttingTool = new ItemCuttingTool()
            .setUnlocalizedName("cuttingTool")
            .setTextureName("cuttableblocks:cutting_tool")
            .setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
        
        GameRegistry.registerItem(cuttingTool, "cutting_tool");
    }
}
