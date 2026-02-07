package com.cuttableblocks.items;

import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.tileentities.TileEntityCuttable;
import com.cuttableblocks.util.CutDirections;
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
        
        // Block rotation (for now always 0, can be extended later)
        int rotId = 0;
        
        // Get player's look vector and normalize
        Vec3 lookVec = player.getLookVec().normalize();
        
        // Find best matching discrete direction based ONLY on look vector
        int dirId = CutDirections.findBestDirection(lookVec, rotId);
        
        // Get the actual world-space normal for this direction
        Vec3 nWorld = CutDirections.getWorldDir(rotId, dirId);
        double nx = nWorld.xCoord;
        double ny = nWorld.yCoord;
        double nz = nWorld.zCoord;
        
        // Plane ALWAYS passes through center (0.5,0.5,0.5) of the block
        double planeD = 0.5 * (nx + ny + nz);
        
        // Calculate keepPositive deterministically:
        // Keep the side closer to the player (camera)
        // Player eye position in block-local coordinates
        double plx = player.posX - x;
        double ply = (player.posY + player.getEyeHeight()) - y;
        double plz = player.posZ - z;
        
        // Distance from player to plane (positive = player is on positive side)
        double playerDist = nx * plx + ny * ply + nz * plz - planeD;
        
        // Keep the side closer to player (opposite to where player stands)
        boolean keepPositive = playerDist < 0;
        
        // Log for debugging
        System.out.println(String.format(
            "[CuttableBlocks] LookVec: (%.4f, %.4f, %.4f) | dirId=%d | nWorld: (%.4f, %.4f, %.4f) | keepPos=%s",
            lookVec.xCoord, lookVec.yCoord, lookVec.zCoord, dirId, nx, ny, nz, keepPositive));
        
        // Debug message to player
        player.addChatMessage(new ChatComponentText(
            String.format("Cut: look=(%.2f, %.2f, %.2f), dir=%d, keepPos=%s",
                lookVec.xCoord, lookVec.yCoord, lookVec.zCoord, dirId, keepPositive)
        ));
        
        // Replace with cuttable block
        world.setBlock(x, y, z, ModBlocks.blockCuttable, 0, 3);
        
        // Set the tile entity data - NO anchor/hitpoint influence on geometry!
        TileEntityCuttable te = (TileEntityCuttable) world.getTileEntity(x, y, z);
        if (te != null) {
            te.setCutData(targetBlock, targetMeta, rotId, dirId, keepPositive);
        }
        
        world.markBlockForUpdate(x, y, z);
        
        return true;
    }
}
