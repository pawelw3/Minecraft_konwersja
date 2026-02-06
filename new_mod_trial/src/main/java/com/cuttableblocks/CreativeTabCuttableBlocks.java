package com.cuttableblocks;

import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.init.Items;
import net.minecraft.item.Item;

public class CreativeTabCuttableBlocks {
    
    public static CreativeTabs tabCuttableBlocks = new CreativeTabs("cuttableblocks") {
        @Override
        public Item getTabIconItem() {
            // Używamy apple jako ikony - to Item (nie Block), więc na pewno działa
            // Blocks.stone może być null podczas wczesnej inicjalizacji
            return Items.apple;
        }
    };
}
