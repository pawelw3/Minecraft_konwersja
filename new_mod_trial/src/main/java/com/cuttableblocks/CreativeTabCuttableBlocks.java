package com.cuttableblocks;

import com.cuttableblocks.blocks.ModBlocks;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.Item;

public class CreativeTabCuttableBlocks {
    
    public static CreativeTabs tabCuttableBlocks = new CreativeTabs("cuttableblocks") {
        @Override
        public Item getTabIconItem() {
            return Item.getItemFromBlock(ModBlocks.blockCuttable);
        }
    };
}
