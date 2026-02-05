package com.cuttableblocks.blocks;

import com.cuttableblocks.client.ClientProxy;
import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.block.BlockContainer;
import net.minecraft.block.material.Material;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.item.ItemStack;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.MovingObjectPosition;
import net.minecraft.world.IBlockAccess;
import net.minecraft.world.World;

import java.util.ArrayList;

public class BlockCuttable extends BlockContainer {
    
    public BlockCuttable(Material material) {
        super(material);
        this.setHardness(1.0f);
        this.setResistance(5.0f);
    }
    
    @Override
    public TileEntity createNewTileEntity(World world, int metadata) {
        return new TileEntityCuttable();
    }
    
    @Override
    public int getRenderType() {
        return ClientProxy.cuttableRenderId;
    }
    
    @Override
    public boolean isOpaqueCube() {
        return false;
    }
    
    @Override
    public boolean renderAsNormalBlock() {
        return false;
    }
    
    @Override
    public void setBlockBoundsBasedOnState(IBlockAccess world, int x, int y, int z) {
        // Calculate bounds based on the cut plane
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCuttable) {
            TileEntityCuttable cutTE = (TileEntityCuttable) te;
            setBoundsForCut(cutTE);
            return;
        }
        // Default to full block
        this.setBlockBounds(0.0f, 0.0f, 0.0f, 1.0f, 1.0f, 1.0f);
    }
    
    private void setBoundsForCut(TileEntityCuttable te) {
        float nx = te.getNormalX();
        float ny = te.getNormalY();
        float nz = te.getNormalZ();
        boolean keepPositive = te.keepPositiveSide();
        
        float absNx = Math.abs(nx);
        float absNy = Math.abs(ny);
        float absNz = Math.abs(nz);
        
        // Axis-aligned cuts get precise bounds
        if (absNy > 0.95f) {
            // Horizontal cut
            if (ny > 0 == keepPositive) {
                this.setBlockBounds(0.0f, 0.5f, 0.0f, 1.0f, 1.0f, 1.0f); // Top half
            } else {
                this.setBlockBounds(0.0f, 0.0f, 0.0f, 1.0f, 0.5f, 1.0f); // Bottom half
            }
        } else if (absNx > 0.95f) {
            // Vertical X cut
            if (nx > 0 == keepPositive) {
                this.setBlockBounds(0.5f, 0.0f, 0.0f, 1.0f, 1.0f, 1.0f); // East half
            } else {
                this.setBlockBounds(0.0f, 0.0f, 0.0f, 0.5f, 1.0f, 1.0f); // West half
            }
        } else if (absNz > 0.95f) {
            // Vertical Z cut
            if (nz > 0 == keepPositive) {
                this.setBlockBounds(0.0f, 0.0f, 0.5f, 1.0f, 1.0f, 1.0f); // South half
            } else {
                this.setBlockBounds(0.0f, 0.0f, 0.0f, 1.0f, 1.0f, 0.5f); // North half
            }
        } else {
            // Diagonal cut - use full block for simplicity
            this.setBlockBounds(0.0f, 0.0f, 0.0f, 1.0f, 1.0f, 1.0f);
        }
    }
    
    @Override
    public ItemStack getPickBlock(MovingObjectPosition target, World world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCuttable) {
            TileEntityCuttable cutTE = (TileEntityCuttable) te;
            Block original = cutTE.getOriginalBlock();
            int meta = cutTE.getOriginalMetadata();
            if (original != null) {
                return new ItemStack(original, 1, meta);
            }
        }
        return super.getPickBlock(target, world, x, y, z);
    }
    
    @Override
    public ArrayList<ItemStack> getDrops(World world, int x, int y, int z, int metadata, int fortune) {
        ArrayList<ItemStack> drops = new ArrayList<>();
        
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCuttable) {
            TileEntityCuttable cutTE = (TileEntityCuttable) te;
            Block original = cutTE.getOriginalBlock();
            int meta = cutTE.getOriginalMetadata();
            if (original != null) {
                drops.add(new ItemStack(original, 1, meta));
                return drops;
            }
        }
        
        return super.getDrops(world, x, y, z, metadata, fortune);
    }
    
    @Override
    public boolean removedByPlayer(World world, EntityPlayer player, int x, int y, int z, boolean willHarvest) {
        // Drop the original block when harvested
        return super.removedByPlayer(world, player, x, y, z, willHarvest);
    }
    
    @Override
    public void addCollisionBoxesToList(World world, int x, int y, int z, 
                                        net.minecraft.util.AxisAlignedBB mask, 
                                        java.util.List list, Entity entity) {
        // Set bounds based on cut before adding collision boxes
        setBlockBoundsBasedOnState(world, x, y, z);
        super.addCollisionBoxesToList(world, x, y, z, mask, list, entity);
        // Reset to full block for safety
        this.setBlockBounds(0.0f, 0.0f, 0.0f, 1.0f, 1.0f, 1.0f);
    }
}
