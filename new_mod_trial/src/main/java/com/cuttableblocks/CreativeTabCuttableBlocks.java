package com.cuttableblocks;

import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.init.Blocks;
import net.minecraft.item.Item;

public class CreativeTabCuttableBlocks {
    
    public static CreativeTabs tabCuttableBlocks = new CreativeTabs("cuttableblocks") {
        @Override
        public Item getTabIconItem() {
            // Uzywamy stone jako ikony - na pewno istnieje
            // ModBlocks.blockCuttable moze byc jeszcze null podczas inicjalizacji
            return Item.getItemFromBlock(Blocks.stone);
        }
    };
}
