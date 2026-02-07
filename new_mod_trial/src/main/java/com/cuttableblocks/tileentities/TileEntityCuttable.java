package com.cuttableblocks.tileentities;

import com.cuttableblocks.util.CutDirections;
import net.minecraft.block.Block;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.network.NetworkManager;
import net.minecraft.network.Packet;
import net.minecraft.network.play.server.S35PacketUpdateTileEntity;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.Vec3;

public class TileEntityCuttable extends TileEntity {
    
    private Block originalBlock;
    private int originalMetadata;
    
    // Discrete direction storage (replaces normalX/Y/Z)
    private byte rotId;          // Block rotation 0..23
    private byte dirId;          // Direction 0..17
    private boolean keepPositiveSide;
    
    // Anchor point - kept for backward compatibility only, NOT used for geometry/UV
    private float anchorX, anchorY, anchorZ;
    
    // Cached normal (reconstructed from rotId/dirId)
    private float normalX, normalY, normalZ;
    private boolean normalDirty = true;
    
    public TileEntityCuttable() {
        this.originalBlock = null;
        this.originalMetadata = 0;
        this.rotId = 0;
        this.dirId = 0;
        this.keepPositiveSide = true;
        this.anchorX = 0.5f;
        this.anchorY = 0.5f;
        this.anchorZ = 0.5f;
    }
    
    /**
     * Set cut data with discrete directions.
     * Plane ALWAYS passes through center (0.5, 0.5, 0.5).
     * NO anchor/hitpoint influence on geometry!
     */
    public void setCutData(Block block, int meta, int rotId, int dirId, boolean keepPositive) {
        this.originalBlock = block;
        this.originalMetadata = meta;
        this.rotId = (byte) rotId;
        this.dirId = (byte) dirId;
        this.keepPositiveSide = keepPositive;
        // Anchor always center - not used for geometry anyway
        this.anchorX = 0.5f;
        this.anchorY = 0.5f;
        this.anchorZ = 0.5f;
        this.normalDirty = true;
        
        this.markDirty();
        if (this.worldObj != null) {
            this.worldObj.markBlockForUpdate(this.xCoord, this.yCoord, this.zCoord);
        }
    }
    
    /**
     * Legacy overload for backward compatibility - converts old format to new.
     */
    public void setCutData(Block block, int meta, float nx, float ny, float nz, 
                           boolean keepPositive, double planeD, 
                           float anchorX, float anchorY, float anchorZ) {
        // Approximate the normal to find closest dirId with rotId=0
        Vec3 lookVec = Vec3.createVectorHelper(nx, ny, nz);
        lookVec = lookVec.normalize();
        int bestDirId = CutDirections.findBestDirection(lookVec, 0);
        
        setCutData(block, meta, 0, bestDirId, keepPositive);
    }
    
    // ====================================================================================
    // GETTERS
    // ====================================================================================
    
    public Block getOriginalBlock() {
        return originalBlock;
    }
    
    public int getOriginalMetadata() {
        return originalMetadata;
    }
    
    public int getRotId() {
        return rotId & 0xFF;
    }
    
    public int getDirId() {
        return dirId & 0xFF;
    }
    
    public boolean keepPositiveSide() {
        return keepPositiveSide;
    }
    
    /**
     * Get reconstructed normal vector (cached).
     */
    public float getNormalX() {
        rebuildNormalIfNeeded();
        return normalX;
    }
    
    public float getNormalY() {
        rebuildNormalIfNeeded();
        return normalY;
    }
    
    public float getNormalZ() {
        rebuildNormalIfNeeded();
        return normalZ;
    }
    
    /**
     * Get plane D (distance from origin).
     * Plane always passes through center: d = 0.5*(nx+ny+nz)
     */
    public double getPlaneD() {
        rebuildNormalIfNeeded();
        return 0.5 * (normalX + normalY + normalZ);
    }
    
    /**
     * Get world-space normal vector.
     */
    public Vec3 getWorldNormal() {
        return CutDirections.getWorldDir(getRotId(), getDirId());
    }
    
    /**
     * Get block center in world coordinates.
     */
    public Vec3 getCenter() {
        return Vec3.createVectorHelper(this.xCoord + 0.5, this.yCoord + 0.5, this.zCoord + 0.5);
    }
    
    private void rebuildNormalIfNeeded() {
        if (normalDirty) {
            Vec3 n = CutDirections.getWorldDir(getRotId(), getDirId());
            normalX = (float) n.xCoord;
            normalY = (float) n.yCoord;
            normalZ = (float) n.zCoord;
            normalDirty = false;
        }
    }
    
    // ====================================================================================
    // NBT
    // ====================================================================================
    
    @Override
    public void writeToNBT(NBTTagCompound nbt) {
        super.writeToNBT(nbt);
        
        if (originalBlock != null) {
            String blockName = Block.blockRegistry.getNameForObject(originalBlock);
            nbt.setString("originalBlock", blockName);
        }
        nbt.setInteger("originalMeta", originalMetadata);
        
        // New discrete direction storage
        nbt.setByte("rotId", rotId);
        nbt.setByte("dirId", dirId);
        nbt.setBoolean("keepPositive", keepPositiveSide);
        
        // Anchor kept for backward compatibility only
        nbt.setFloat("anchorX", anchorX);
        nbt.setFloat("anchorY", anchorY);
        nbt.setFloat("anchorZ", anchorZ);
        
        // Legacy compatibility - also store computed normal
        rebuildNormalIfNeeded();
        nbt.setFloat("normalX", normalX);
        nbt.setFloat("normalY", normalY);
        nbt.setFloat("normalZ", normalZ);
    }
    
    @Override
    public void readFromNBT(NBTTagCompound nbt) {
        super.readFromNBT(nbt);
        
        if (nbt.hasKey("originalBlock")) {
            String blockName = nbt.getString("originalBlock");
            this.originalBlock = (Block) Block.blockRegistry.getObject(blockName);
        }
        this.originalMetadata = nbt.getInteger("originalMeta");
        
        // Read discrete directions (with legacy fallback)
        if (nbt.hasKey("rotId")) {
            this.rotId = nbt.getByte("rotId");
            this.dirId = nbt.getByte("dirId");
        } else {
            // Legacy: reconstruct from stored normal
            float nx = nbt.getFloat("normalX");
            float ny = nbt.getFloat("normalY");
            float nz = nbt.getFloat("normalZ");
            Vec3 lookVec = Vec3.createVectorHelper(nx, ny, nz);
            lookVec = lookVec.normalize();
            this.dirId = (byte) CutDirections.findBestDirection(lookVec, 0);
            this.rotId = 0;
        }
        
        this.keepPositiveSide = nbt.getBoolean("keepPositive");
        
        // Anchor (with default) - kept for backward compat, not used
        this.anchorX = nbt.hasKey("anchorX") ? nbt.getFloat("anchorX") : 0.5f;
        this.anchorY = nbt.hasKey("anchorY") ? nbt.getFloat("anchorY") : 0.5f;
        this.anchorZ = nbt.hasKey("anchorZ") ? nbt.getFloat("anchorZ") : 0.5f;
        
        this.normalDirty = true;
    }
    
    @Override
    public Packet getDescriptionPacket() {
        NBTTagCompound nbt = new NBTTagCompound();
        this.writeToNBT(nbt);
        return new S35PacketUpdateTileEntity(this.xCoord, this.yCoord, this.zCoord, 0, nbt);
    }
    
    @Override
    public void onDataPacket(NetworkManager net, S35PacketUpdateTileEntity pkt) {
        this.readFromNBT(pkt.getNbtCompound());
        this.worldObj.markBlockRangeForRenderUpdate(
            this.xCoord, this.yCoord, this.zCoord,
            this.xCoord, this.yCoord, this.zCoord
        );
    }
}
