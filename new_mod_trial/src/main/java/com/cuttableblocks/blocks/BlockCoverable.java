package com.cuttableblocks.blocks;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import com.cuttableblocks.tileentities.TileEntityCoverable;
import cpw.mods.fml.relauncher.Side;
import cpw.mods.fml.relauncher.SideOnly;
import net.minecraft.block.Block;
import net.minecraft.block.BlockContainer;
import net.minecraft.block.material.Material;
import net.minecraft.client.renderer.texture.IIconRegister;
import net.minecraft.entity.EntityLivingBase;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.item.ItemStack;
import net.minecraft.item.ItemBlock;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.IIcon;
import net.minecraft.util.MathHelper;
import net.minecraft.util.MovingObjectPosition;
import net.minecraft.world.World;

import java.util.ArrayList;

public class BlockCoverable extends BlockContainer {

    public static final int KIND_BLOCK = 0;
    public static final int KIND_SLOPE = 1;
    public static final int KIND_STAIRS = 2;
    public static final int KIND_BARRIER = 3;
    public static final int KIND_DOOR = 4;

    private final int kind;

    @SideOnly(Side.CLIENT)
    private IIcon ownIcon;

    public BlockCoverable(Material material, int kind) {
        super(material);
        this.kind = kind;
        this.setHardness(1.0f);
        this.setResistance(5.0f);
        this.setCreativeTab(CreativeTabCuttableBlocks.tabCuttableBlocks);
    }

    public int getKind() {
        return kind;
    }

    @Override
    @SideOnly(Side.CLIENT)
    public void registerIcons(IIconRegister register) {
        this.ownIcon = register.registerIcon("cuttableblocks:cuttable_block");
    }

    @Override
    @SideOnly(Side.CLIENT)
    public IIcon getIcon(int side, int meta) {
        return ownIcon;
    }

    @Override
    public TileEntity createNewTileEntity(World world, int metadata) {
        return new TileEntityCoverable();
    }

    @Override
    public int getRenderType() {
        return com.cuttableblocks.client.ClientProxy.coverableRenderId;
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
    public void onBlockPlacedBy(World world, int x, int y, int z, EntityLivingBase entity, ItemStack stack) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCoverable) {
            int quadrant = MathHelper.floor_double((double) (entity.rotationYaw * 4.0F / 360.0F) + 0.5D) & 3;
            int facing;
            switch (quadrant) {
                case 0:
                    facing = 2;
                    break;
                case 1:
                    facing = 5;
                    break;
                case 2:
                    facing = 3;
                    break;
                default:
                    facing = 4;
                    break;
            }
            ((TileEntityCoverable) te).setFacing(facing);
        }
    }

    @Override
    public boolean onBlockActivated(World world, int x, int y, int z,
                                    EntityPlayer player, int side,
                                    float hitX, float hitY, float hitZ) {
        ItemStack held = player.getCurrentEquippedItem();
        if (held != null && held.getItem() instanceof ItemBlock) {
            return com.cuttableblocks.items.ItemCarpenterHammer.applyToCoverable(player, world, x, y, z, side);
        }
        if (held != null && held.getItem() == com.cuttableblocks.items.ModItems.carpenterHammer) {
            return com.cuttableblocks.items.ItemCarpenterHammer.applyToCoverable(player, world, x, y, z, side);
        }
        return false;
    }

    @Override
    public ItemStack getPickBlock(MovingObjectPosition target, World world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCoverable) {
            TileEntityCoverable cover = (TileEntityCoverable) te;
            Block block = cover.getCoverBlock();
            if (block != null && block != Blocks.air) {
                return new ItemStack(block, 1, cover.getCoverMeta());
            }
        }
        return super.getPickBlock(target, world, x, y, z);
    }

    @Override
    public ArrayList<ItemStack> getDrops(World world, int x, int y, int z, int metadata, int fortune) {
        ArrayList<ItemStack> drops = new ArrayList<ItemStack>();
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCoverable) {
            TileEntityCoverable cover = (TileEntityCoverable) te;
            Block block = cover.getCoverBlock();
            if (block != null && block != Blocks.air) {
                drops.add(new ItemStack(block, 1, cover.getCoverMeta()));
                return drops;
            }
        }
        return super.getDrops(world, x, y, z, metadata, fortune);
    }
}
