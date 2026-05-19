package com.cuttableblocks.blocks;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import cpw.mods.fml.common.registry.GameRegistry;
import net.minecraft.block.Block;
import net.minecraft.block.material.Material;

public class ModBlocks {

    public static Block blockCuttable;
    public static Block blockCollapsible;

    public static void registerBlocks() {
        blockCuttable = new BlockCuttable(Material.rock)
            .setUnlocalizedName("cuttableBlock")
            .setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
        GameRegistry.registerBlock(blockCuttable, "cuttable_block");

        blockCollapsible = new BlockCollapsible(Material.rock)
            .setUnlocalizedName("collapsibleBlock")
            .setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
        GameRegistry.registerBlock(blockCollapsible, "collapsible_block");
    }
}
