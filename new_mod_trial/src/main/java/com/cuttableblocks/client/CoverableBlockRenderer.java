package com.cuttableblocks.client;

import com.cuttableblocks.blocks.BlockCoverable;
import com.cuttableblocks.tileentities.TileEntityCoverable;
import cpw.mods.fml.client.registry.ISimpleBlockRenderingHandler;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.IIcon;
import net.minecraft.world.IBlockAccess;

public class CoverableBlockRenderer implements ISimpleBlockRenderingHandler {

    @Override
    public void renderInventoryBlock(Block block, int metadata, int modelId, RenderBlocks renderer) {
        renderer.setRenderBounds(0.0D, 0.0D, 0.0D, 1.0D, 1.0D, 1.0D);
        renderer.renderBlockAsItem(block, metadata, 1.0F);
    }

    @Override
    public boolean renderWorldBlock(IBlockAccess world, int x, int y, int z,
                                    Block block, int modelId, RenderBlocks renderer) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCoverable) || !(block instanceof BlockCoverable)) {
            return renderer.renderStandardBlock(block, x, y, z);
        }

        TileEntityCoverable cover = (TileEntityCoverable) te;
        Block coverBlock = cover.getCoverBlock();
        int kind = ((BlockCoverable) block).getKind();

        if (kind == BlockCoverable.KIND_BLOCK) {
            return renderBox(renderer, coverBlock, x, y, z, 0, 0, 0, 1, 1, 1);
        } else if (kind == BlockCoverable.KIND_SLOPE) {
            return renderSlope(renderer, coverBlock, x, y, z, cover);
        } else if (kind == BlockCoverable.KIND_STAIRS) {
            return renderStairs(renderer, coverBlock, x, y, z, cover);
        } else if (kind == BlockCoverable.KIND_BARRIER) {
            return renderBarrier(renderer, coverBlock, x, y, z, world);
        } else if (kind == BlockCoverable.KIND_DOOR) {
            return renderDoor(renderer, coverBlock, x, y, z, cover);
        }

        return renderer.renderStandardBlock(block, x, y, z);
    }

    @Override
    public boolean shouldRender3DInInventory(int modelId) {
        return true;
    }

    @Override
    public int getRenderId() {
        return ClientProxy.coverableRenderId;
    }

    private boolean renderBox(RenderBlocks renderer, Block block, int x, int y, int z,
                              double minX, double minY, double minZ,
                              double maxX, double maxY, double maxZ) {
        renderer.setRenderBounds(minX, minY, minZ, maxX, maxY, maxZ);
        return renderer.renderStandardBlock(block, x, y, z);
    }

    private boolean renderSlope(RenderBlocks renderer, Block block, int x, int y, int z,
                                TileEntityCoverable cover) {
        Tessellator tess = Tessellator.instance;
        int meta = cover.getCoverMeta();
        int brightness = block.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
        int color = block.colorMultiplier(renderer.blockAccess, x, y, z);
        float cr = ((color >> 16) & 0xFF) / 255.0F;
        float cg = ((color >> 8) & 0xFF) / 255.0F;
        float cb = (color & 0xFF) / 255.0F;
        boolean inverted = cover.getShape() % 2 == 1;

        double y00;
        double y10;
        double y01;
        double y11;
        if (!inverted) {
            y00 = slopeTopHeight(cover.getFacing(), 0, 0);
            y10 = slopeTopHeight(cover.getFacing(), 1, 0);
            y01 = slopeTopHeight(cover.getFacing(), 0, 1);
            y11 = slopeTopHeight(cover.getFacing(), 1, 1);
        } else {
            y00 = 1.0D - slopeTopHeight(cover.getFacing(), 0, 0);
            y10 = 1.0D - slopeTopHeight(cover.getFacing(), 1, 0);
            y01 = 1.0D - slopeTopHeight(cover.getFacing(), 0, 1);
            y11 = 1.0D - slopeTopHeight(cover.getFacing(), 1, 1);
        }

        IIcon topIcon = block.getIcon(inverted ? 0 : 1, meta);
        IIcon bottomIcon = block.getIcon(inverted ? 1 : 0, meta);
        IIcon northIcon = block.getIcon(2, meta);
        IIcon southIcon = block.getIcon(3, meta);
        IIcon westIcon = block.getIcon(4, meta);
        IIcon eastIcon = block.getIcon(5, meta);

        if (!inverted) {
            addQuad(tess, brightness, cr * 0.5F, cg * 0.5F, cb * 0.5F,
                x, y, z + 1, x + 1, y, z + 1, x + 1, y, z, x, y, z, bottomIcon);
            addNorthSouthFace(tess, brightness, cr, cg, cb, x, y, z, true, y00, y10, northIcon);
            addNorthSouthFace(tess, brightness, cr, cg, cb, x, y, z, false, y01, y11, southIcon);
            addWestEastFace(tess, brightness, cr, cg, cb, x, y, z, true, y00, y01, westIcon);
            addWestEastFace(tess, brightness, cr, cg, cb, x, y, z, false, y10, y11, eastIcon);
            addQuad(tess, brightness, cr, cg, cb,
                x, y + y01, z + 1, x + 1, y + y11, z + 1, x + 1, y + y10, z, x, y + y00, z, topIcon);
        } else {
            addQuad(tess, brightness, cr, cg, cb,
                x, y + 1, z, x + 1, y + 1, z, x + 1, y + 1, z + 1, x, y + 1, z + 1, topIcon);
            addNorthSouthFace(tess, brightness, cr, cg, cb, x, y, z, true, y00, y10, northIcon);
            addNorthSouthFace(tess, brightness, cr, cg, cb, x, y, z, false, y01, y11, southIcon);
            addWestEastFace(tess, brightness, cr, cg, cb, x, y, z, true, y00, y01, westIcon);
            addWestEastFace(tess, brightness, cr, cg, cb, x, y, z, false, y10, y11, eastIcon);
            addQuad(tess, brightness, cr, cg, cb,
                x, y + y00, z, x + 1, y + y10, z, x + 1, y + y11, z + 1, x, y + y01, z + 1, bottomIcon);
        }
        return true;
    }

    private double slopeTopHeight(int facing, int xSide, int zSide) {
        if (facing == 2) {
            return zSide == 0 ? 0.0D : 1.0D;
        } else if (facing == 3) {
            return zSide == 0 ? 1.0D : 0.0D;
        } else if (facing == 4) {
            return xSide == 0 ? 1.0D : 0.0D;
        }
        return xSide == 0 ? 0.0D : 1.0D;
    }

    private void addNorthSouthFace(Tessellator tess, int brightness, float cr, float cg, float cb,
                                   int x, int y, int z, boolean north,
                                   double leftHeight, double rightHeight, IIcon icon) {
        double zz = north ? z : z + 1;
        float shade = 0.8F;
        if (leftHeight <= 0.0D && rightHeight <= 0.0D) {
            return;
        }
        addQuad(tess, brightness, cr * shade, cg * shade, cb * shade,
            x, y, zz, x + 1, y, zz, x + 1, y + rightHeight, zz, x, y + leftHeight, zz, icon);
    }

    private void addWestEastFace(Tessellator tess, int brightness, float cr, float cg, float cb,
                                 int x, int y, int z, boolean west,
                                 double nearHeight, double farHeight, IIcon icon) {
        double xx = west ? x : x + 1;
        float shade = 0.6F;
        if (nearHeight <= 0.0D && farHeight <= 0.0D) {
            return;
        }
        addQuad(tess, brightness, cr * shade, cg * shade, cb * shade,
            xx, y, z + 1, xx, y, z, xx, y + nearHeight, z, xx, y + farHeight, z + 1, icon);
    }

    private void addQuad(Tessellator tess, int brightness, float cr, float cg, float cb,
                         double x1, double y1, double z1,
                         double x2, double y2, double z2,
                         double x3, double y3, double z3,
                         double x4, double y4, double z4,
                         IIcon icon) {
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(cr, cg, cb);
        tess.addVertexWithUV(x1, y1, z1, icon.getMinU(), icon.getMaxV());
        tess.addVertexWithUV(x2, y2, z2, icon.getMaxU(), icon.getMaxV());
        tess.addVertexWithUV(x3, y3, z3, icon.getMaxU(), icon.getMinV());
        tess.addVertexWithUV(x4, y4, z4, icon.getMinU(), icon.getMinV());
    }

    private boolean renderStairs(RenderBlocks renderer, Block block, int x, int y, int z,
                                 TileEntityCoverable cover) {
        boolean top = cover.getShape() % 2 == 1;
        double minY = top ? 0.5D : 0.0D;
        double maxY = top ? 1.0D : 0.5D;
        boolean rendered = renderBox(renderer, block, x, y, z, 0, minY, 0, 1, maxY, 1);
        int facing = cover.getFacing();
        if (facing == 2) {
            rendered |= renderBox(renderer, block, x, y, z, 0, top ? 0 : 0.5D, 0.5D, 1, top ? 0.5D : 1, 1);
        } else if (facing == 3) {
            rendered |= renderBox(renderer, block, x, y, z, 0, top ? 0 : 0.5D, 0, 1, top ? 0.5D : 1, 0.5D);
        } else if (facing == 4) {
            rendered |= renderBox(renderer, block, x, y, z, 0.5D, top ? 0 : 0.5D, 0, 1, top ? 0.5D : 1, 1);
        } else {
            rendered |= renderBox(renderer, block, x, y, z, 0, top ? 0 : 0.5D, 0, 0.5D, top ? 0.5D : 1, 1);
        }
        return rendered;
    }

    private boolean renderBarrier(RenderBlocks renderer, Block block, int x, int y, int z, IBlockAccess world) {
        boolean rendered = renderBox(renderer, block, x, y, z, 0.375D, 0, 0.375D, 0.625D, 1, 0.625D);
        if (connects(world, x, y, z - 1)) {
            rendered |= renderBox(renderer, block, x, y, z, 0.4375D, 0.25D, 0, 0.5625D, 0.875D, 0.5D);
        }
        if (connects(world, x, y, z + 1)) {
            rendered |= renderBox(renderer, block, x, y, z, 0.4375D, 0.25D, 0.5D, 0.5625D, 0.875D, 1);
        }
        if (connects(world, x - 1, y, z)) {
            rendered |= renderBox(renderer, block, x, y, z, 0, 0.25D, 0.4375D, 0.5D, 0.875D, 0.5625D);
        }
        if (connects(world, x + 1, y, z)) {
            rendered |= renderBox(renderer, block, x, y, z, 0.5D, 0.25D, 0.4375D, 1, 0.875D, 0.5625D);
        }
        return rendered;
    }

    private boolean renderDoor(RenderBlocks renderer, Block block, int x, int y, int z, TileEntityCoverable cover) {
        double thickness = 0.1875D;
        int facing = cover.getFacing();
        if (cover.isOpen()) {
            facing = openFacing(facing, cover.isRightHinge());
        }
        if (facing == 2) {
            return renderBox(renderer, block, x, y, z, 0, 0, 1.0D - thickness, 1, 1, 1);
        } else if (facing == 3) {
            return renderBox(renderer, block, x, y, z, 0, 0, 0, 1, 1, thickness);
        } else if (facing == 4) {
            return renderBox(renderer, block, x, y, z, 1.0D - thickness, 0, 0, 1, 1, 1);
        }
        return renderBox(renderer, block, x, y, z, 0, 0, 0, thickness, 1, 1);
    }

    private int openFacing(int facing, boolean rightHinge) {
        if (rightHinge) {
            if (facing == 2) return 4;
            if (facing == 4) return 3;
            if (facing == 3) return 5;
            return 2;
        }
        if (facing == 2) return 5;
        if (facing == 5) return 3;
        if (facing == 3) return 4;
        return 2;
    }

    private boolean connects(IBlockAccess world, int x, int y, int z) {
        Block block = world.getBlock(x, y, z);
        return block == com.cuttableblocks.blocks.ModBlocks.carpenterBarrier
            || block.isOpaqueCube();
    }
}
