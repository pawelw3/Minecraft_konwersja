package com.cuttableblocks.blocks;

import com.cuttableblocks.tileentities.TileEntityCoverable;
import net.minecraft.block.material.Material;
import net.minecraft.entity.EntityLivingBase;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.item.ItemStack;
import net.minecraft.item.ItemBlock;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.world.World;

public class BlockCoverableDoor extends BlockCoverable {

    public BlockCoverableDoor(Material material) {
        super(material, KIND_DOOR);
    }

    @Override
    public void onBlockPlacedBy(World world, int x, int y, int z, EntityLivingBase entity, ItemStack stack) {
        super.onBlockPlacedBy(world, x, y, z, entity, stack);
        if (!world.isRemote && world.isAirBlock(x, y + 1, z)) {
            world.setBlock(x, y + 1, z, this, 0, 3);
            TileEntity bottom = world.getTileEntity(x, y, z);
            TileEntity top = world.getTileEntity(x, y + 1, z);
            if (bottom instanceof TileEntityCoverable && top instanceof TileEntityCoverable) {
                TileEntityCoverable bottomCover = (TileEntityCoverable) bottom;
                TileEntityCoverable topCover = (TileEntityCoverable) top;
                topCover.setCover(bottomCover.getCoverBlock(), bottomCover.getCoverMeta());
                topCover.setFacing(bottomCover.getFacing());
                topCover.setUpperDoorHalf(true);
            }
        }
    }

    @Override
    public boolean onBlockActivated(World world, int x, int y, int z,
                                    EntityPlayer player, int side,
                                    float hitX, float hitY, float hitZ) {
        ItemStack held = player.getCurrentEquippedItem();
        if (held != null && (held.getItem() == com.cuttableblocks.items.ModItems.carpenterHammer
            || held.getItem() instanceof ItemBlock)) {
            return com.cuttableblocks.items.ItemCarpenterHammer.applyToCoverable(player, world, x, y, z, side);
        }
        if (!world.isRemote) {
            toggleDoor(world, x, y, z);
        }
        return true;
    }

    @Override
    public void onNeighborBlockChange(World world, int x, int y, int z, net.minecraft.block.Block block) {
        if (world.isRemote) {
            return;
        }
        TileEntityCoverable te = getDoorTe(world, x, y, z);
        if (te == null) {
            return;
        }
        int baseY = te.isUpperDoorHalf() ? y - 1 : y;
        boolean powered = world.isBlockIndirectlyGettingPowered(x, baseY, z)
            || world.isBlockIndirectlyGettingPowered(x, baseY + 1, z);
        if (powered != te.isPowered()) {
            setDoorOpen(world, x, baseY, z, powered, powered);
        }
    }

    public void toggleDoor(World world, int x, int y, int z) {
        TileEntityCoverable te = getDoorTe(world, x, y, z);
        if (te == null) {
            return;
        }
        int baseY = te.isUpperDoorHalf() ? y - 1 : y;
        setDoorOpen(world, x, baseY, z, !te.isOpen(), te.isPowered());
    }

    private void setDoorOpen(World world, int x, int y, int z, boolean open, boolean powered) {
        TileEntity bottom = world.getTileEntity(x, y, z);
        TileEntity top = world.getTileEntity(x, y + 1, z);
        if (bottom instanceof TileEntityCoverable) {
            ((TileEntityCoverable) bottom).setOpen(open);
            ((TileEntityCoverable) bottom).setPowered(powered);
        }
        if (top instanceof TileEntityCoverable) {
            ((TileEntityCoverable) top).setOpen(open);
            ((TileEntityCoverable) top).setPowered(powered);
        }
        world.markBlockForUpdate(x, y, z);
        world.markBlockForUpdate(x, y + 1, z);
    }

    private TileEntityCoverable getDoorTe(World world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        return te instanceof TileEntityCoverable ? (TileEntityCoverable) te : null;
    }
}
