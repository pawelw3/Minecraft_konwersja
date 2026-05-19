package com.cuttableblocks.items;

import com.cuttableblocks.blocks.BlockCollapsible;
import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.tileentities.TileEntityCollapsible;
import net.minecraft.block.Block;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.ChatComponentText;
import net.minecraft.world.World;

/**
 * Right-click on any solid block           → convert it to a CollapsibleBlock
 *                                             (all corners at max height = full block)
 * Right-click on a CollapsibleBlock        → raise the clicked quadrant by 1 step
 * Sneak + right-click on CollapsibleBlock  → lower the clicked quadrant by 1 step
 *
 * The hit coordinates (hitX, hitZ) from onItemUse map directly to the four
 * quadrants via TileEntityCollapsible.getQuadFromHit.
 */
public class ItemCollapsibleHammer extends Item {

    public ItemCollapsibleHammer() {
        setMaxStackSize(1);
        setFull3D();
    }

    @Override
    public boolean onItemUse(ItemStack stack, EntityPlayer player, World world,
                              int x, int y, int z, int side,
                              float hitX, float hitY, float hitZ) {
        if (world.isRemote) return true;

        Block block = world.getBlock(x, y, z);

        // ---- Adjust existing collapsible block ----
        if (block == ModBlocks.blockCollapsible) {
            TileEntity te = world.getTileEntity(x, y, z);
            if (!(te instanceof TileEntityCollapsible)) return false;

            TileEntityCollapsible col = (TileEntityCollapsible) te;
            int quad  = TileEntityCollapsible.getQuadFromHit(hitX, hitZ);
            int delta = player.isSneaking() ? -1 : 1;
            int newDepth = col.getCornerDepth(quad) + delta;

            col.setCornerDepth(quad, newDepth);
            BlockCollapsible.smoothAdjacentCollapsibles(world, col, quad);
            world.markBlockForUpdate(x, y, z);

            debugMsg(player, quad, col.getCornerDepth(quad));
            return true;
        }

        // ---- Convert a normal block to a CollapsibleBlock ----
        if (block == Blocks.air || block == Blocks.bedrock
                || block == ModBlocks.blockCuttable) {
            return false;
        }

        int origMeta = world.getBlockMetadata(x, y, z);
        world.setBlock(x, y, z, ModBlocks.blockCollapsible, 0, 3);

        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCollapsible) {
            ((TileEntityCollapsible) te).setBlockData(block, origMeta);
        }

        world.markBlockForUpdate(x, y, z);
        player.addChatMessage(new ChatComponentText(
                "[CollapsibleHammer] Converted block. Right-click corners to shape."));
        return true;
    }

    private static void debugMsg(EntityPlayer player, int quad, int depth) {
        String[] names = {"NW", "SW", "NE", "SE"};
        player.addChatMessage(new ChatComponentText(
                "[CollapsibleHammer] " + names[quad] + " = " + depth + "/16"));
    }
}
