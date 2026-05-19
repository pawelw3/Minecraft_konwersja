package com.cuttableblocks.blocks;

import com.cuttableblocks.client.ClientProxy;
import com.cuttableblocks.tileentities.TileEntityCollapsible;
import cpw.mods.fml.relauncher.Side;
import cpw.mods.fml.relauncher.SideOnly;
import net.minecraft.block.Block;
import net.minecraft.block.BlockContainer;
import net.minecraft.block.material.Material;
import net.minecraft.client.renderer.texture.IIconRegister;
import net.minecraft.entity.Entity;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.Blocks;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.AxisAlignedBB;
import net.minecraft.util.IIcon;
import net.minecraft.util.MovingObjectPosition;
import net.minecraft.util.Vec3;
import net.minecraft.world.IBlockAccess;
import net.minecraft.world.World;

import java.util.ArrayList;
import java.util.List;

public class BlockCollapsible extends BlockContainer {

    @SideOnly(Side.CLIENT)
    private IIcon ownIcon;

    public BlockCollapsible(Material material) {
        super(material);
        this.setHardness(1.0f);
        this.setResistance(5.0f);
    }

    @Override
    @SideOnly(Side.CLIENT)
    public void registerIcons(IIconRegister register) {
        this.ownIcon = register.registerIcon("cuttableblocks:collapsible_block");
    }

    @Override
    @SideOnly(Side.CLIENT)
    public IIcon getIcon(int side, int meta) {
        return this.ownIcon;
    }

    @Override
    public TileEntity createNewTileEntity(World world, int metadata) {
        return new TileEntityCollapsible();
    }

    @Override
    public boolean onBlockActivated(World world, int x, int y, int z,
                                    EntityPlayer player, int side,
                                    float hitX, float hitY, float hitZ) {
        ItemStack held = player.getCurrentEquippedItem();
        if (held == null || !(held.getItem() instanceof ItemBlock)) return false;
        Block heldBlock = Block.getBlockFromItem(held.getItem());
        if (heldBlock == null || heldBlock == Blocks.air) return false;
        if (!world.isRemote) {
            TileEntity te = world.getTileEntity(x, y, z);
            if (te instanceof TileEntityCollapsible) {
                ((TileEntityCollapsible) te).setBlockData(heldBlock, held.getMetadata());
            }
        }
        return true;
    }

    @Override
    public int getRenderType() {
        return ClientProxy.collapsibleRenderId;
    }

    @Override
    public boolean isOpaqueCube() { return false; }

    @Override
    public boolean renderAsNormalBlock() { return false; }

    // -------------------------------------------------------------------------
    // Bounding box — single AABB covering the tallest corner
    // -------------------------------------------------------------------------

    @Override
    public void setBlockBoundsBasedOnState(IBlockAccess world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCollapsible) {
            TileEntityCollapsible col = (TileEntityCollapsible) te;
            float maxD = col.getMaxOffset();
            if (col.isPositive()) {
                setBlockBounds(0f, 0f, 0f, 1f, maxD, 1f);
            } else {
                setBlockBounds(0f, 1f - maxD, 0f, 1f, 1f, 1f);
            }
            return;
        }
        setBlockBounds(0f, 0f, 0f, 1f, 1f, 1f);
    }

    // -------------------------------------------------------------------------
    // Collision — 4 separate AABB boxes, one per quadrant
    // -------------------------------------------------------------------------

    @Override
    @SuppressWarnings("unchecked")
    public void addCollisionBoxesToList(World world, int x, int y, int z,
                                        AxisAlignedBB mask, List list, Entity entity) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCollapsible)) return;

        TileEntityCollapsible col = (TileEntityCollapsible) te;
        for (int quad = 0; quad < 4; quad++) {
            float[] b = genQuadBounds(col, quad);
            AxisAlignedBB box = AxisAlignedBB.getBoundingBox(
                    x + b[0], y + b[1], z + b[2],
                    x + b[3], y + b[4], z + b[5]);
            if (mask.intersectsWith(box)) {
                list.add(box);
            }
        }
    }

    /**
     * Returns [xMin, yMin, zMin, xMax, yMax, zMax] for a quadrant's collision box.
     * Adjacent quadrants stagger by at most 0.5 so the player can always walk across.
     */
    public static float[] genQuadBounds(TileEntityCollapsible col, int quad) {
        float xMin = 0f, zMin = 0f, xMax = 1f, zMax = 1f;
        switch (quad) {
            case TileEntityCollapsible.QUAD_XZNN: xMax = 0.5f; zMax = 0.5f; break;
            case TileEntityCollapsible.QUAD_XZNP: xMax = 0.5f; zMin = 0.5f; break;
            case TileEntityCollapsible.QUAD_XZPN: xMin = 0.5f; zMax = 0.5f; break;
            case TileEntityCollapsible.QUAD_XZPP: xMin = 0.5f; zMin = 0.5f; break;
        }

        float maxOffset = col.getMaxOffset();
        float depth = col.getCornerOffset(quad);

        if (col.isPositive()) {
            // Limit stagger to 0.5 so the player can always step up
            if (maxOffset - depth > 0.5f) depth = maxOffset - 0.5f;
            return new float[]{xMin, 0f, zMin, xMax, depth, zMax};
        } else {
            if (maxOffset - depth > 0.5f) depth = maxOffset - 0.5f;
            return new float[]{xMin, 1f - depth, zMin, xMax, 1f, zMax};
        }
    }

    // -------------------------------------------------------------------------
    // Ray trace — test all 4 quadrant boxes, return nearest hit
    // -------------------------------------------------------------------------

    @Override
    public MovingObjectPosition collisionRayTrace(World world, int x, int y, int z,
                                                   Vec3 startVec, Vec3 endVec) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCollapsible)) return null;

        TileEntityCollapsible col = (TileEntityCollapsible) te;
        MovingObjectPosition best = null;
        double bestDist = Double.MAX_VALUE;

        for (int quad = 0; quad < 4; quad++) {
            float[] b = genQuadBounds(col, quad);
            setBlockBounds(b[0], b[1], b[2], b[3], b[4], b[5]);
            MovingObjectPosition hit = super.collisionRayTrace(world, x, y, z, startVec, endVec);
            if (hit != null) {
                double dist = hit.hitVec.squareDistanceTo(startVec);
                if (dist < bestDist) {
                    bestDist = dist;
                    best = hit;
                }
            }
        }

        setBlockBounds(0f, 0f, 0f, 1f, 1f, 1f);
        return best;
    }

    // -------------------------------------------------------------------------
    // Drops / pick block — return original wrapped block
    // -------------------------------------------------------------------------

    @Override
    public ArrayList<ItemStack> getDrops(World world, int x, int y, int z,
                                          int metadata, int fortune) {
        ArrayList<ItemStack> drops = new ArrayList<ItemStack>();
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCollapsible) {
            TileEntityCollapsible col = (TileEntityCollapsible) te;
            Block orig = col.getOriginalBlock();
            if (orig != null) {
                drops.add(new ItemStack(orig, 1, col.getOriginalMetadata()));
                return drops;
            }
        }
        return super.getDrops(world, x, y, z, metadata, fortune);
    }

    @Override
    public ItemStack getPickBlock(MovingObjectPosition target, World world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (te instanceof TileEntityCollapsible) {
            TileEntityCollapsible col = (TileEntityCollapsible) te;
            Block orig = col.getOriginalBlock();
            if (orig != null) {
                return new ItemStack(orig, 1, col.getOriginalMetadata());
            }
        }
        return super.getPickBlock(target, world, x, y, z);
    }

    // -------------------------------------------------------------------------
    // Smoothing — propagate a changed corner to adjacent collapsible blocks
    // so terrain transitions are seamless.
    // -------------------------------------------------------------------------

    public static void smoothAdjacentCollapsibles(World world,
                                                   TileEntityCollapsible src,
                                                   int changedQuad) {
        int cx = src.xCoord, cy = src.yCoord, cz = src.zCoord;
        int depth = src.getCornerDepth(changedQuad);

        // Fetch the 8 potential neighbours (cardinal + diagonal at same Y)
        TileEntityCollapsible xN  = getColTE(world, cx - 1, cy, cz);
        TileEntityCollapsible xP  = getColTE(world, cx + 1, cy, cz);
        TileEntityCollapsible zN  = getColTE(world, cx,     cy, cz - 1);
        TileEntityCollapsible zP  = getColTE(world, cx,     cy, cz + 1);
        TileEntityCollapsible xNzN = getColTE(world, cx - 1, cy, cz - 1);
        TileEntityCollapsible xNzP = getColTE(world, cx - 1, cy, cz + 1);
        TileEntityCollapsible xPzN = getColTE(world, cx + 1, cy, cz - 1);
        TileEntityCollapsible xPzP = getColTE(world, cx + 1, cy, cz + 1);

        switch (changedQuad) {
            case TileEntityCollapsible.QUAD_XZNN: // NW changed
                setIfSameDir(zN,   TileEntityCollapsible.QUAD_XZNP, depth, src);
                setIfSameDir(xN,   TileEntityCollapsible.QUAD_XZPN, depth, src);
                setIfSameDir(xNzN, TileEntityCollapsible.QUAD_XZPP, depth, src);
                break;
            case TileEntityCollapsible.QUAD_XZNP: // SW changed
                setIfSameDir(xN,   TileEntityCollapsible.QUAD_XZPP, depth, src);
                setIfSameDir(zP,   TileEntityCollapsible.QUAD_XZNN, depth, src);
                setIfSameDir(xNzP, TileEntityCollapsible.QUAD_XZPN, depth, src);
                break;
            case TileEntityCollapsible.QUAD_XZPN: // NE changed
                setIfSameDir(xP,   TileEntityCollapsible.QUAD_XZNN, depth, src);
                setIfSameDir(zN,   TileEntityCollapsible.QUAD_XZPP, depth, src);
                setIfSameDir(xPzN, TileEntityCollapsible.QUAD_XZNP, depth, src);
                break;
            case TileEntityCollapsible.QUAD_XZPP: // SE changed
                setIfSameDir(zP,   TileEntityCollapsible.QUAD_XZPN, depth, src);
                setIfSameDir(xP,   TileEntityCollapsible.QUAD_XZNP, depth, src);
                setIfSameDir(xPzP, TileEntityCollapsible.QUAD_XZNN, depth, src);
                break;
        }
    }

    private static TileEntityCollapsible getColTE(World world, int x, int y, int z) {
        TileEntity te = world.getTileEntity(x, y, z);
        return (te instanceof TileEntityCollapsible) ? (TileEntityCollapsible) te : null;
    }

    // Only smooth if the neighbour has the same orientation (both positive or both negative)
    private static void setIfSameDir(TileEntityCollapsible nb, int quad,
                                      int depth, TileEntityCollapsible src) {
        if (nb != null && nb.isPositive() == src.isPositive()) {
            nb.setCornerDepth(quad, depth);
        }
    }
}
