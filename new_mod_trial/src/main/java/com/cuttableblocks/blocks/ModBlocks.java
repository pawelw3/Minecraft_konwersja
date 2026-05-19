package com.cuttableblocks.blocks;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import cpw.mods.fml.common.registry.GameRegistry;
import net.minecraft.block.Block;
import net.minecraft.block.material.Material;

public class ModBlocks {

    public static Block blockCuttable;
    public static Block blockCollapsible;
    public static Block carpenterBlock;
    public static Block carpenterSlope;
    public static Block carpenterStairs;
    public static Block carpenterBarrier;
    public static Block carpenterDoor;

    public static void registerBlocks() {
        blockCuttable = new BlockCuttable(Material.rock)
            .setUnlocalizedName("cuttableBlock")
            .setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
        GameRegistry.registerBlock(blockCuttable, "cuttable_block");

        blockCollapsible = new BlockCollapsible(Material.rock)
            .setUnlocalizedName("collapsibleBlock")
            .setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
        GameRegistry.registerBlock(blockCollapsible, "collapsible_block");

        carpenterBlock = new BlockCoverable(Material.rock, BlockCoverable.KIND_BLOCK)
            .setUnlocalizedName("carpenterBlock");
        GameRegistry.registerBlock(carpenterBlock, "carpenter_block");

        carpenterSlope = new BlockCoverable(Material.rock, BlockCoverable.KIND_SLOPE)
            .setUnlocalizedName("carpenterSlope");
        GameRegistry.registerBlock(carpenterSlope, "carpenter_slope");

        carpenterStairs = new BlockCoverable(Material.rock, BlockCoverable.KIND_STAIRS)
            .setUnlocalizedName("carpenterStairs");
        GameRegistry.registerBlock(carpenterStairs, "carpenter_stairs");

        carpenterBarrier = new BlockCoverable(Material.wood, BlockCoverable.KIND_BARRIER)
            .setUnlocalizedName("carpenterBarrier");
        GameRegistry.registerBlock(carpenterBarrier, "carpenter_barrier");

        carpenterDoor = new BlockCoverableDoor(Material.wood)
            .setUnlocalizedName("carpenterDoor");
        GameRegistry.registerBlock(carpenterDoor, "carpenter_door");
    }
}
