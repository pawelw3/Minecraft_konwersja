package com.cuttableblocks.tileentities;

import net.minecraft.block.Block;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.network.NetworkManager;
import net.minecraft.network.Packet;
import net.minecraft.network.play.server.S35PacketUpdateTileEntity;
import net.minecraft.tileentity.TileEntity;

public class TileEntityCuttable extends TileEntity {
    
    private Block originalBlock;
    private int originalMetadata;
    private float normalX, normalY, normalZ;
    private boolean keepPositiveSide;
    
    public TileEntityCuttable() {
        this.originalBlock = null;
        this.originalMetadata = 0;
        this.normalX = 0.0f;
        this.normalY = 1.0f;
        this.normalZ = 0.0f;
        this.keepPositiveSide = true;
    }
    
    public void setCutData(Block block, int meta, float nx, float ny, float nz, boolean keepPositive) {
        this.originalBlock = block;
        this.originalMetadata = meta;
        this.normalX = nx;
        this.normalY = ny;
        this.normalZ = nz;
        this.keepPositiveSide = keepPositive;
        
        this.markDirty();
        if (this.worldObj != null) {
            this.worldObj.markBlockForUpdate(this.xCoord, this.yCoord, this.zCoord);
        }
    }
    
    public Block getOriginalBlock() {
        return originalBlock;
    }
    
    public int getOriginalMetadata() {
        return originalMetadata;
    }
    
    public float getNormalX() {
        return normalX;
    }
    
    public float getNormalY() {
        return normalY;
    }
    
    public float getNormalZ() {
        return normalZ;
    }
    
    public boolean keepPositiveSide() {
        return keepPositiveSide;
    }
    
    @Override
    public void writeToNBT(NBTTagCompound nbt) {
        super.writeToNBT(nbt);
        
        if (originalBlock != null) {
            String blockName = Block.blockRegistry.getNameForObject(originalBlock);
            nbt.setString("originalBlock", blockName);
        }
        nbt.setInteger("originalMeta", originalMetadata);
        nbt.setFloat("normalX", normalX);
        nbt.setFloat("normalY", normalY);
        nbt.setFloat("normalZ", normalZ);
        nbt.setBoolean("keepPositive", keepPositiveSide);
    }
    
    @Override
    public void readFromNBT(NBTTagCompound nbt) {
        super.readFromNBT(nbt);
        
        if (nbt.hasKey("originalBlock")) {
            String blockName = nbt.getString("originalBlock");
            this.originalBlock = (Block) Block.blockRegistry.getObject(blockName);
        }
        this.originalMetadata = nbt.getInteger("originalMeta");
        this.normalX = nbt.getFloat("normalX");
        this.normalY = nbt.getFloat("normalY");
        this.normalZ = nbt.getFloat("normalZ");
        this.keepPositiveSide = nbt.getBoolean("keepPositive");
    }
    
    @Override
    public Packet getDescriptionPacket() {
        NBTTagCompound nbt = new NBTTagCompound();
        this.writeToNBT(nbt);
        return new S35PacketUpdateTileEntity(this.xCoord, this.yCoord, this.zCoord, 0, nbt);
    }
    
    @Override
    public void onDataPacket(NetworkManager net, S35PacketUpdateTileEntity pkt) {
        this.readFromNBT(pkt.func_148857_g());
        this.worldObj.markBlockRangeForRenderUpdate(
            this.xCoord, this.yCoord, this.zCoord,
            this.xCoord, this.yCoord, this.zCoord
        );
    }
}
