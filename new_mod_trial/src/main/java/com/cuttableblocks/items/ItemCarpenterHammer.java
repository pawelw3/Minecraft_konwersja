package com.cuttableblocks.items;

import com.cuttableblocks.blocks.BlockCoverable;
import com.cuttableblocks.tileentities.TileEntityCoverable;
import net.minecraft.block.Block;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.ChatComponentText;
import net.minecraft.world.World;

public class ItemCarpenterHammer extends Item {

    public ItemCarpenterHammer() {
        setMaxStackSize(1);
        setFull3D();
    }

    public static boolean applyToCoverable(EntityPlayer player, World world, int x, int y, int z, int side) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCoverable)) {
            return false;
        }
        if (world.isRemote) {
            return true;
        }

        TileEntityCoverable cover = (TileEntityCoverable) te;
        ItemStack held = player.getCurrentEquippedItem();

        if (!player.isSneaking() && held != null && held.getItem() instanceof ItemBlock) {
            Block block = Block.getBlockFromItem(held.getItem());
            if (block != null && block != Blocks.air && !(block instanceof BlockCoverable)) {
                setCoverOnDoorPair(world, x, y, z, cover, block, held.getMetadata());
                player.addChatMessage(new ChatComponentText("[CarpenterHammer] Cover set to "
                    + Block.blockRegistry.getNameForObject(block) + ":" + held.getMetadata()));
                return true;
            }
        }

        Block blockAtPos = world.getBlock(x, y, z);
        if (blockAtPos instanceof BlockCoverable) {
            BlockCoverable coverableBlock = (BlockCoverable) blockAtPos;
            switch (coverableBlock.getKind()) {
                case BlockCoverable.KIND_SLOPE:
                    cover.cycleShape(2);
                    player.addChatMessage(new ChatComponentText("[CarpenterHammer] Slope shape = " + cover.getShape()));
                    return true;
                case BlockCoverable.KIND_STAIRS:
                    cover.cycleShape(2);
                    player.addChatMessage(new ChatComponentText("[CarpenterHammer] Stairs shape = " + cover.getShape()));
                    return true;
                case BlockCoverable.KIND_DOOR:
                    cover.setRightHinge(!cover.isRightHinge());
                    syncDoorPairFlags(world, x, y, z, cover);
                    player.addChatMessage(new ChatComponentText("[CarpenterHammer] Door hinge toggled"));
                    return true;
                default:
                    cover.rotateFacing();
                    player.addChatMessage(new ChatComponentText("[CarpenterHammer] Facing = " + cover.getFacing()));
                    return true;
            }
        }
        return false;
    }

    @Override
    public boolean onItemUse(ItemStack stack, EntityPlayer player, World world,
                             int x, int y, int z, int side,
                             float hitX, float hitY, float hitZ) {
        return applyToCoverable(player, world, x, y, z, side);
    }

    private static void setCoverOnDoorPair(World world, int x, int y, int z,
                                           TileEntityCoverable cover, Block block, int meta) {
        cover.setCover(block, meta);
        if (world.getBlock(x, y, z) == com.cuttableblocks.blocks.ModBlocks.carpenterDoor) {
            int otherY = cover.isUpperDoorHalf() ? y - 1 : y + 1;
            TileEntity other = world.getTileEntity(x, otherY, z);
            if (other instanceof TileEntityCoverable) {
                ((TileEntityCoverable) other).setCover(block, meta);
            }
        }
    }

    private static void syncDoorPairFlags(World world, int x, int y, int z, TileEntityCoverable cover) {
        if (world.getBlock(x, y, z) != com.cuttableblocks.blocks.ModBlocks.carpenterDoor) {
            return;
        }
        int otherY = cover.isUpperDoorHalf() ? y - 1 : y + 1;
        TileEntity other = world.getTileEntity(x, otherY, z);
        if (other instanceof TileEntityCoverable) {
            TileEntityCoverable otherCover = (TileEntityCoverable) other;
            otherCover.setFlags(copyDoorPairBits(cover.getFlags(), otherCover.getFlags()));
        }
    }

    private static int copyDoorPairBits(int sourceFlags, int targetFlags) {
        int keepUpperBit = targetFlags & 2;
        int sharedBits = sourceFlags & ~2;
        return keepUpperBit | sharedBits;
    }
}
