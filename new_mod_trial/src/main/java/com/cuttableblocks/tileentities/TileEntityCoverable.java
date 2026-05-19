package com.cuttableblocks.tileentities;

import net.minecraft.block.Block;
import net.minecraft.init.Blocks;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.network.NetworkManager;
import net.minecraft.network.Packet;
import net.minecraft.network.play.server.S35PacketUpdateTileEntity;
import net.minecraft.tileentity.TileEntity;

public class TileEntityCoverable extends TileEntity {

    private Block coverBlock = Blocks.planks;
    private int coverMeta = 0;
    private int facing = 2;
    private int shape = 0;
    private int flags = 0;
    private String sourceCarpentersTeId = "";

    public Block getCoverBlock() {
        return coverBlock == null ? Blocks.planks : coverBlock;
    }

    public int getCoverMeta() {
        return coverMeta;
    }

    public int getFacing() {
        return facing;
    }

    public int getShape() {
        return shape;
    }

    public int getFlags() {
        return flags;
    }

    public String getSourceCarpentersTeId() {
        return sourceCarpentersTeId;
    }

    public boolean isOpen() {
        return (flags & 1) != 0;
    }

    public boolean isUpperDoorHalf() {
        return (flags & 2) != 0;
    }

    public boolean isPowered() {
        return (flags & 4) != 0;
    }

    public boolean isRightHinge() {
        return (flags & 8) != 0;
    }

    public void setCover(Block block, int meta) {
        if (block == null || block == Blocks.air) {
            return;
        }
        this.coverBlock = block;
        this.coverMeta = meta;
        sync();
    }

    public void setFacing(int facing) {
        this.facing = normalizeFacing(facing);
        sync();
    }

    public void rotateFacing() {
        switch (facing) {
            case 2:
                setFacing(5);
                break;
            case 5:
                setFacing(3);
                break;
            case 3:
                setFacing(4);
                break;
            default:
                setFacing(2);
                break;
        }
    }

    public void setShape(int shape) {
        this.shape = Math.max(0, shape);
        sync();
    }

    public void cycleShape(int count) {
        if (count <= 0) {
            return;
        }
        this.shape = (this.shape + 1) % count;
        sync();
    }

    public void setFlags(int flags) {
        this.flags = flags;
        sync();
    }

    public void setFlag(int mask, boolean enabled) {
        if (enabled) {
            flags |= mask;
        } else {
            flags &= ~mask;
        }
        sync();
    }

    public void setOpen(boolean open) {
        setFlag(1, open);
    }

    public void setUpperDoorHalf(boolean upper) {
        setFlag(2, upper);
    }

    public void setPowered(boolean powered) {
        setFlag(4, powered);
    }

    public void setRightHinge(boolean rightHinge) {
        setFlag(8, rightHinge);
    }

    public void setSourceCarpentersTeId(String sourceCarpentersTeId) {
        this.sourceCarpentersTeId = sourceCarpentersTeId == null ? "" : sourceCarpentersTeId;
        sync();
    }

    private int normalizeFacing(int value) {
        return value >= 2 && value <= 5 ? value : 2;
    }

    private void sync() {
        markDirty();
        if (worldObj != null) {
            worldObj.markBlockForUpdate(xCoord, yCoord, zCoord);
        }
    }

    @Override
    public void writeToNBT(NBTTagCompound nbt) {
        super.writeToNBT(nbt);
        if (coverBlock != null) {
            nbt.setString("coverBlock", Block.blockRegistry.getNameForObject(coverBlock));
        }
        nbt.setInteger("coverMeta", coverMeta);
        nbt.setInteger("facing", facing);
        nbt.setInteger("shape", shape);
        nbt.setInteger("flags", flags);
        nbt.setString("sourceCarpentersTeId", sourceCarpentersTeId);
    }

    @Override
    public void readFromNBT(NBTTagCompound nbt) {
        super.readFromNBT(nbt);
        if (nbt.hasKey("coverBlock")) {
            Block block = (Block) Block.blockRegistry.getObject(nbt.getString("coverBlock"));
            coverBlock = block == null ? Blocks.planks : block;
        }
        coverMeta = nbt.getInteger("coverMeta");
        facing = normalizeFacing(nbt.getInteger("facing"));
        shape = Math.max(0, nbt.getInteger("shape"));
        flags = nbt.getInteger("flags");
        sourceCarpentersTeId = nbt.getString("sourceCarpentersTeId");
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
