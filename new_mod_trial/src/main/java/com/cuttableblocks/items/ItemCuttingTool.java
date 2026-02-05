package com.cuttableblocks.items;

import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.util.ChatComponentText;
import net.minecraft.util.Vec3;
import net.minecraft.world.World;

public class ItemCuttingTool extends Item {
    
    public ItemCuttingTool() {
        this.setMaxStackSize(1);
        this.setFull3D();
    }
    
    @Override
    public boolean onItemUse(ItemStack stack, EntityPlayer player, World world, 
                             int x, int y, int z, int side, 
                             float hitX, float hitY, float hitZ) {
        
        if (world.isRemote) {
            return true;
        }
        
        Block targetBlock = world.getBlock(x, y, z);
        int targetMeta = world.getBlockMetadata(x, y, z);
        
        // Cannot cut air, bedrock, or already cut blocks
        if (targetBlock == Blocks.air || targetBlock == Blocks.bedrock 
            || targetBlock == ModBlocks.blockCuttable) {
            return false;
        }
        
        // Get player's look vector
        Vec3 lookVec = player.getLookVec();
        
        // Normalize the vector
        double len = Math.sqrt(lookVec.xCoord * lookVec.xCoord 
                             + lookVec.yCoord * lookVec.yCoord 
                             + lookVec.zCoord * lookVec.zCoord);
        
        if (len < 0.0001) {
            return false;
        }
        
        float nx = (float)(lookVec.xCoord / len);
        float ny = (float)(lookVec.yCoord / len);
        float nz = (float)(lookVec.zCoord / len);
        
        // Determine which side to keep based on player position relative to block center
        double playerToCenterX = player.posX - (x + 0.5);
        double playerToCenterY = player.posY + player.getEyeHeight() - (y + 0.5);
        double playerToCenterZ = player.posZ - (z + 0.5);
        
        // Dot product: positive means player is on the positive side of the plane
        double dotProduct = playerToCenterX * nx + playerToCenterY * ny + playerToCenterZ * nz;
        boolean keepPositive = dotProduct > 0;
        
        // Debug message
        player.addChatMessage(new ChatComponentText(
            String.format("Cutting with normal (%.2f, %.2f, %.2f), keeping %s side",
                nx, ny, nz, keepPositive ? "positive" : "negative")
        ));
        
        // Replace with cuttable block
        world.setBlock(x, y, z, ModBlocks.blockCuttable, 0, 3);
        
        // Set the tile entity data
        TileEntityCuttable te = (TileEntityCuttable) world.getTileEntity(x, y, z);
        if (te != null) {
            te.setCutData(targetBlock, targetMeta, nx, ny, nz, keepPositive);
        }
        
        world.markBlockForUpdate(x, y, z);
        
        return true;
    }
}
