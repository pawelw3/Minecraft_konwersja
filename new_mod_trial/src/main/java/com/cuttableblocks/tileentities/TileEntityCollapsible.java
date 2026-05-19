package com.cuttableblocks.tileentities;

import net.minecraft.block.Block;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.network.NetworkManager;
import net.minecraft.network.Packet;
import net.minecraft.network.play.server.S35PacketUpdateTileEntity;
import net.minecraft.tileentity.TileEntity;

public class TileEntityCollapsible extends TileEntity {

    // Quadrant indices — same naming convention as Carpenter's Blocks
    public static final int QUAD_XZNN = 0; // NW corner (min X, min Z)
    public static final int QUAD_XZNP = 1; // SW corner (min X, max Z)
    public static final int QUAD_XZPN = 2; // NE corner (max X, min Z)
    public static final int QUAD_XZPP = 3; // SE corner (max X, max Z)

    private Block originalBlock;
    private int originalMetadata;
    // Corner heights: 0 = flat (no height), 16 = full block height (1/16 units)
    private final int[] cornerDepths = new int[4];
    // true = top surface is shaped (grows up from Y=0), false = bottom surface is shaped
    private boolean isPositive;

    public TileEntityCollapsible() {
        for (int i = 0; i < 4; i++) cornerDepths[i] = 16;
        isPositive = true;
    }

    // -------------------------------------------------------------------------
    // Setup
    // -------------------------------------------------------------------------

    public void setBlockData(Block block, int meta) {
        originalBlock = block;
        originalMetadata = meta;
        for (int i = 0; i < 4; i++) cornerDepths[i] = 16;
        isPositive = true;
        sync();
    }

    public void setCornerDepth(int quad, int depth) {
        if (depth < 0) depth = 0;
        if (depth > 16) depth = 16;
        cornerDepths[quad] = depth;
        sync();
    }

    public void setPositive(boolean pos) {
        isPositive = pos;
        sync();
    }

    private void sync() {
        markDirty();
        if (worldObj != null) {
            worldObj.markBlockForUpdate(xCoord, yCoord, zCoord);
        }
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    public Block getOriginalBlock() { return originalBlock; }
    public int getOriginalMetadata() { return originalMetadata; }
    public boolean isPositive() { return isPositive; }

    public int getCornerDepth(int quad) {
        return cornerDepths[quad];
    }

    /** Corner height as a float in [0.0, 1.0]. */
    public float getCornerOffset(int quad) {
        return cornerDepths[quad] / 16.0f;
    }

    /** Tallest corner offset — used for bounding box. */
    public float getMaxOffset() {
        float max = 0;
        for (int i = 0; i < 4; i++) {
            float d = cornerDepths[i] / 16.0f;
            if (d > max) max = d;
        }
        return max;
    }

    /**
     * Y height of the centre point of the sloped face.
     * The surface is split into 4 triangles meeting here.
     * Uses the diagonal with the smaller height difference to minimise visible seam.
     */
    public float getCenterY() {
        float nn = getCornerOffset(QUAD_XZNN);
        float np = getCornerOffset(QUAD_XZNP);
        float pn = getCornerOffset(QUAD_XZPN);
        float pp = getCornerOffset(QUAD_XZPP);

        float diagNWSE = Math.abs(nn - pp);
        float diagNESW = Math.abs(pn - np);

        return diagNWSE < diagNESW ? (pn + np) / 2.0f : (nn + pp) / 2.0f;
    }

    /**
     * Maps a hit-point (0..1) on the block face to one of the 4 corner quadrants.
     * hitX / hitZ come directly from onItemUse parameters.
     */
    public static int getQuadFromHit(float hitX, float hitZ) {
        int xSide = Math.round(hitX); // 0 = West half, 1 = East half
        int zSide = Math.round(hitZ); // 0 = North half, 1 = South half
        if (xSide == 0 && zSide == 0) return QUAD_XZNN;
        if (xSide == 0)               return QUAD_XZNP;
        if (zSide == 0)               return QUAD_XZPN;
        return QUAD_XZPP;
    }

    // -------------------------------------------------------------------------
    // NBT
    // -------------------------------------------------------------------------

    @Override
    public void writeToNBT(NBTTagCompound nbt) {
        super.writeToNBT(nbt);
        if (originalBlock != null) {
            nbt.setString("origBlock", Block.blockRegistry.getNameForObject(originalBlock));
        }
        nbt.setInteger("origMeta", originalMetadata);
        nbt.setIntArray("corners", cornerDepths);
        nbt.setBoolean("isPositive", isPositive);
    }

    @Override
    public void readFromNBT(NBTTagCompound nbt) {
        super.readFromNBT(nbt);
        if (nbt.hasKey("origBlock")) {
            originalBlock = (Block) Block.blockRegistry.getObject(nbt.getString("origBlock"));
        }
        originalMetadata = nbt.getInteger("origMeta");
        if (nbt.hasKey("corners")) {
            int[] stored = nbt.getIntArray("corners");
            for (int i = 0; i < 4 && i < stored.length; i++) {
                cornerDepths[i] = stored[i];
            }
        }
        isPositive = nbt.getBoolean("isPositive");
    }

    @Override
    public Packet getDescriptionPacket() {
        NBTTagCompound nbt = new NBTTagCompound();
        writeToNBT(nbt);
        return new S35PacketUpdateTileEntity(xCoord, yCoord, zCoord, 0, nbt);
    }

    @Override
    public void onDataPacket(NetworkManager net, S35PacketUpdateTileEntity pkt) {
        readFromNBT(pkt.getNbtCompound());
        worldObj.markBlockRangeForRenderUpdate(xCoord, yCoord, zCoord, xCoord, yCoord, zCoord);
    }
}
