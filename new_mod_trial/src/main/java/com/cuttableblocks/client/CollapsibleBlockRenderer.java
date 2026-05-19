package com.cuttableblocks.client;

import com.cuttableblocks.tileentities.TileEntityCollapsible;
import cpw.mods.fml.client.registry.ISimpleBlockRenderingHandler;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.tileentity.TileEntity;
import net.minecraft.util.IIcon;
import net.minecraft.world.IBlockAccess;
import org.lwjgl.opengl.GL11;

/**
 * Renders a CollapsibleBlock:
 *   - Flat base face (bottom for positive / top for negative) via RenderBlocks.
 *   - Four trapezoidal side faces (sloped top or bottom edge) as GL_QUADS.
 *   - Height-mapped surface as four GL_TRIANGLES meeting at the block centre.
 *
 * Tessellator state contract in renderWorldBlock:
 *   Phase 1: use the GL_QUADS batch already started by the chunk renderer
 *            → flat base face + 4 side faces
 *   Phase 2: tess.draw() + startDrawing(GL_TRIANGLES)
 *            → 4 triangles of the sloped surface
 *   Phase 3: tess.draw() + startDrawing(GL_QUADS)
 *            → restore mode so subsequent blocks in the chunk work normally
 */
public class CollapsibleBlockRenderer implements ISimpleBlockRenderingHandler {

    // Matches vanilla Minecraft's per-face directional lighting constants
    private static final float LIT_TOP    = 1.0f;
    private static final float LIT_BOTTOM = 0.5f;
    private static final float LIT_NS     = 0.8f;
    private static final float LIT_WE     = 0.6f;

    // -------------------------------------------------------------------------
    // ISimpleBlockRenderingHandler
    // -------------------------------------------------------------------------

    @Override
    public int getRenderId() {
        return ClientProxy.collapsibleRenderId;
    }

    @Override
    public boolean shouldRender3DInInventory(int modelId) {
        return true;
    }

    /**
     * Inventory icon: a recognisable diagonal slope (NW=0, SE=1).
     *
     * IMPORTANT: must NOT call tess.draw() / tess.startDrawing() here.
     * In the inventory rendering path the caller (RenderBlocks.renderBlockAsItem)
     * owns the tessellator lifecycle; our handler just adds vertices to the
     * already-started GL_QUADS batch.
     * Triangles are faked via degenerate quads (v0,v1,v2,v2) -- the second
     * "triangle" of the quad is zero-area and invisible.
     */
    @Override
    public void renderInventoryBlock(Block block, int metadata, int modelId,
                                     RenderBlocks renderer) {
        Tessellator tess = Tessellator.instance;
        GL11.glTranslatef(-0.5f, -0.5f, -0.5f);

        IIcon icon = block.getIcon(0, metadata);

        tess.startDrawingQuads();
        tess.setNormal(0, 1, 0);

        // Sides
        tess.setColorOpaque_F(LIT_BOTTOM, LIT_BOTTOM, LIT_BOTTOM);
        renderer.renderFaceYNeg(block, 0, 0, 0, icon);
        tess.setColorOpaque_F(LIT_NS, LIT_NS, LIT_NS);
        renderer.renderFaceZNeg(block, 0, 0, 0, icon);
        renderer.renderFaceZPos(block, 0, 0, 0, icon);
        tess.setColorOpaque_F(LIT_WE, LIT_WE, LIT_WE);
        renderer.renderFaceXNeg(block, 0, 0, 0, icon);
        renderer.renderFaceXPos(block, 0, 0, 0, icon);

        // Sloped top: four degenerate quads faking triangles (v0,v1,v2,v2)
        float nn = 0f, pn = 0.5f, np = 0.5f, pp = 1.0f;
        float cy = (nn + pn + np + pp) / 4f;
        double minU = icon.getMinU(), maxU = icon.getMaxU();
        double minV = icon.getMinV(), maxV = icon.getMaxV();
        double midU = (minU + maxU) * 0.5, midV = (minV + maxV) * 0.5;
        tess.setColorOpaque_F(LIT_TOP, LIT_TOP, LIT_TOP);

        tess.addVertexWithUV(0,   nn, 0,   minU, minV);
        tess.addVertexWithUV(1,   pn, 0,   maxU, minV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);

        tess.addVertexWithUV(1,   pn, 0,   maxU, minV);
        tess.addVertexWithUV(1,   pp, 1,   maxU, maxV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);

        tess.addVertexWithUV(1,   pp, 1,   maxU, maxV);
        tess.addVertexWithUV(0,   np, 1,   minU, maxV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);

        tess.addVertexWithUV(0,   np, 1,   minU, maxV);
        tess.addVertexWithUV(0,   nn, 0,   minU, minV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);
        tess.addVertexWithUV(0.5, cy, 0.5, midU, midV);

        tess.draw();
        GL11.glTranslatef(0.5f, 0.5f, 0.5f);
    }

    // -------------------------------------------------------------------------
    // World render
    // -------------------------------------------------------------------------

    @Override
    public boolean renderWorldBlock(IBlockAccess world, int x, int y, int z,
                                    Block block, int modelId, RenderBlocks renderer) {
        TileEntity te = world.getTileEntity(x, y, z);
        if (!(te instanceof TileEntityCollapsible)) return false;

        TileEntityCollapsible col = (TileEntityCollapsible) te;
        Block orig = col.getOriginalBlock();
        if (orig == null) {
            return renderer.renderStandardBlock(block, x, y, z);
        }

        int  meta = col.getOriginalMetadata();
        boolean pos = col.isPositive();

        float nn = col.getCornerOffset(TileEntityCollapsible.QUAD_XZNN); // NW
        float np = col.getCornerOffset(TileEntityCollapsible.QUAD_XZNP); // SW
        float pn = col.getCornerOffset(TileEntityCollapsible.QUAD_XZPN); // NE
        float pp = col.getCornerOffset(TileEntityCollapsible.QUAD_XZPP); // SE
        float cy = col.getCenterY();

        Tessellator tess = Tessellator.instance;

        int brTop    = world.getLightBrightnessForSkyBlocks(x, y + 1, z,     0);
        int brBottom = world.getLightBrightnessForSkyBlocks(x, y - 1, z,     0);
        int brNorth  = world.getLightBrightnessForSkyBlocks(x, y,     z - 1, 0);
        int brSouth  = world.getLightBrightnessForSkyBlocks(x, y,     z + 1, 0);
        int brWest   = world.getLightBrightnessForSkyBlocks(x - 1, y, z,     0);
        int brEast   = world.getLightBrightnessForSkyBlocks(x + 1, y, z,     0);

        // All rendering adds vertices to the GL_QUADS batch already started by the
        // chunk renderer. We NEVER call tess.draw() or tess.startDrawing() here --
        // doing so breaks FastCraft and other tessellator-replacing mods.
        // Triangles are faked as degenerate quads (v0, v1, v2, v2).

        // 1. Flat base face
        // Normal must point AWAY from the block interior.
        // pos=true  → bottom face at y=0, normal -Y: NW→NE→SE→SW (CCW from below)
        // pos=false → top face   at y=1, normal +Y: SW→SE→NE→NW (CCW from above)
        if (pos) {
            IIcon ic = orig.getIcon(0, meta);
            tess.setBrightness(brBottom);
            tess.setColorOpaque_F(LIT_BOTTOM, LIT_BOTTOM, LIT_BOTTOM);
            tess.addVertexWithUV(x,     y, z,     ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y, z,     ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y, z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(16));
            tess.addVertexWithUV(x,     y, z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
        } else {
            IIcon ic = orig.getIcon(1, meta);
            tess.setBrightness(brTop);
            tess.setColorOpaque_F(LIT_TOP, LIT_TOP, LIT_TOP);
            tess.addVertexWithUV(x,     y + 1, z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
            tess.addVertexWithUV(x + 1, y + 1, z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(16));
            tess.addVertexWithUV(x + 1, y + 1, z,     ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x,     y + 1, z,     ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
        }

        // 2. Trapezoidal side faces
        renderNorthFace(tess, orig, meta, x, y, z, nn, pn, pos, brNorth);
        renderSouthFace(tess, orig, meta, x, y, z, np, pp, pos, brSouth);
        renderWestFace (tess, orig, meta, x, y, z, nn, np, pos, brWest);
        renderEastFace (tess, orig, meta, x, y, z, pn, pp, pos, brEast);

        // 3. Height-mapped sloped surface (degenerate quads -- no mode switching)
        IIcon iconFace = orig.getIcon(pos ? 1 : 0, meta);
        float litFace  = pos ? LIT_TOP : LIT_BOTTOM;
        tess.setBrightness(pos ? brTop : brBottom);
        tess.setColorOpaque_F(litFace, litFace, litFace);
        renderSlopedFace(tess, iconFace, x, y, z, nn, np, pn, pp, cy, pos);

        return true;
    }

    // -------------------------------------------------------------------------
    // Side-face helpers -- trapezoidal quads, GL_QUADS mode
    //
    // For "positive" blocks (UP):
    //   bottom edge is at y=0, top edge follows corner heights.
    // For "negative" blocks (DOWN):
    //   top edge is at y=1, bottom edge follows (1 - corner height).
    //
    // UV: u follows the horizontal axis across the face [0→16],
    //     v follows height from bottom (=16) to top (=0), Minecraft's convention.
    // -------------------------------------------------------------------------

    private static void renderNorthFace(Tessellator tess, Block orig, int meta,
                                         int x, int y, int z,
                                         float hW, float hE, boolean pos, int br) {
        if (hW <= 0 && hE <= 0) return;
        IIcon ic = orig.getIcon(2, meta);
        tess.setBrightness(br);
        tess.setColorOpaque_F(LIT_NS, LIT_NS, LIT_NS);
        if (pos) {
            tess.addVertexWithUV(x,     y,      z, ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
            tess.addVertexWithUV(x,     y + hW, z, ic.getInterpolatedU(0),  ic.getInterpolatedV((1 - hW) * 16));
            tess.addVertexWithUV(x + 1, y + hE, z, ic.getInterpolatedU(16), ic.getInterpolatedV((1 - hE) * 16));
            tess.addVertexWithUV(x + 1, y,      z, ic.getInterpolatedU(16), ic.getInterpolatedV(16));
        } else {
            tess.addVertexWithUV(x,     y + (1 - hW), z, ic.getInterpolatedU(0),  ic.getInterpolatedV(hW * 16));
            tess.addVertexWithUV(x,     y + 1,        z, ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y + 1,        z, ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y + (1 - hE), z, ic.getInterpolatedU(16), ic.getInterpolatedV(hE * 16));
        }
    }

    private static void renderSouthFace(Tessellator tess, Block orig, int meta,
                                         int x, int y, int z,
                                         float hW, float hE, boolean pos, int br) {
        if (hW <= 0 && hE <= 0) return;
        IIcon ic = orig.getIcon(3, meta);
        tess.setBrightness(br);
        tess.setColorOpaque_F(LIT_NS, LIT_NS, LIT_NS);
        // Viewed from outside (+Z): left = East (x+1), right = West (x+0)
        if (pos) {
            tess.addVertexWithUV(x + 1, y,      z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
            tess.addVertexWithUV(x + 1, y + hE, z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV((1 - hE) * 16));
            tess.addVertexWithUV(x,     y + hW, z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV((1 - hW) * 16));
            tess.addVertexWithUV(x,     y,      z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(16));
        } else {
            tess.addVertexWithUV(x + 1, y + (1 - hE), z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(hE * 16));
            tess.addVertexWithUV(x + 1, y + 1,        z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
            tess.addVertexWithUV(x,     y + 1,        z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x,     y + (1 - hW), z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(hW * 16));
        }
    }

    private static void renderWestFace(Tessellator tess, Block orig, int meta,
                                        int x, int y, int z,
                                        float hN, float hS, boolean pos, int br) {
        if (hN <= 0 && hS <= 0) return;
        IIcon ic = orig.getIcon(4, meta);
        tess.setBrightness(br);
        tess.setColorOpaque_F(LIT_WE, LIT_WE, LIT_WE);
        // Viewed from outside (-X): left = South (z+1), right = North (z+0)
        if (pos) {
            tess.addVertexWithUV(x, y,      z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
            tess.addVertexWithUV(x, y + hS, z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV((1 - hS) * 16));
            tess.addVertexWithUV(x, y + hN, z,     ic.getInterpolatedU(16), ic.getInterpolatedV((1 - hN) * 16));
            tess.addVertexWithUV(x, y,      z,     ic.getInterpolatedU(16), ic.getInterpolatedV(16));
        } else {
            tess.addVertexWithUV(x, y + (1 - hS), z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(hS * 16));
            tess.addVertexWithUV(x, y + 1,        z + 1, ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
            tess.addVertexWithUV(x, y + 1,        z,     ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x, y + (1 - hN), z,     ic.getInterpolatedU(16), ic.getInterpolatedV(hN * 16));
        }
    }

    private static void renderEastFace(Tessellator tess, Block orig, int meta,
                                        int x, int y, int z,
                                        float hN, float hS, boolean pos, int br) {
        if (hN <= 0 && hS <= 0) return;
        IIcon ic = orig.getIcon(5, meta);
        tess.setBrightness(br);
        tess.setColorOpaque_F(LIT_WE, LIT_WE, LIT_WE);
        // Viewed from outside (+X): left = North (z+0), right = South (z+1)
        if (pos) {
            tess.addVertexWithUV(x + 1, y,      z,     ic.getInterpolatedU(0),  ic.getInterpolatedV(16));
            tess.addVertexWithUV(x + 1, y + hN, z,     ic.getInterpolatedU(0),  ic.getInterpolatedV((1 - hN) * 16));
            tess.addVertexWithUV(x + 1, y + hS, z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV((1 - hS) * 16));
            tess.addVertexWithUV(x + 1, y,      z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(16));
        } else {
            tess.addVertexWithUV(x + 1, y + (1 - hN), z,     ic.getInterpolatedU(0),  ic.getInterpolatedV(hN * 16));
            tess.addVertexWithUV(x + 1, y + 1,        z,     ic.getInterpolatedU(0),  ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y + 1,        z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(0));
            tess.addVertexWithUV(x + 1, y + (1 - hS), z + 1, ic.getInterpolatedU(16), ic.getInterpolatedV(hS * 16));
        }
    }

    // -------------------------------------------------------------------------
    // Sloped surface -- 4 triangles as degenerate quads (v0, v1, v2, v2).
    //
    // Stays in GL_QUADS mode; never calls draw()/startDrawing().
    // This is safe with FastCraft and other tessellator-replacing mods.
    //
    //   NW(0,0)---NE(1,0)
    //      \   N   /
    //    W  \ | /  E
    //        (C)
    //      /   S   \
    //   SW(0,1)---SE(1,1)
    //
    // UV: u=minU at X=0, u=maxU at X=1; v=minV at Z=0, v=maxV at Z=1
    // -------------------------------------------------------------------------

    // Winding verified via cross product (v1-v0)×(v2-v0):
    //   pos=true  → top surface, normal must be +Y → CCW from above: NW,C,NE order
    //   pos=false → bottom surface, normal must be -Y → CW from above: NW,NE,C order
    private static void renderSlopedFace(Tessellator tess, IIcon icon,
                                          int bx, int by, int bz,
                                          float nn, float np, float pn, float pp,
                                          float cy, boolean pos) {
        double minU = icon.getMinU(), maxU = icon.getMaxU();
        double minV = icon.getMinV(), maxV = icon.getMaxV();
        double midU = (minU + maxU) * 0.5, midV = (minV + maxV) * 0.5;

        if (pos) {
            // Top surface (grows upward) -- normal +Y -- CCW from above: NW,C,NE per tri
            double yNW = by + nn, yNE = by + pn, ySW = by + np, ySE = by + pp, yC = by + cy;
            // North tri (NW, C, NE) → normal +Y
            tess.addVertexWithUV(bx,       yNW, bz,       minU, minV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 1,   yNE, bz,       maxU, minV);
            tess.addVertexWithUV(bx + 1,   yNE, bz,       maxU, minV);
            // East tri (NE, C, SE)
            tess.addVertexWithUV(bx + 1,   yNE, bz,       maxU, minV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 1,   ySE, bz + 1,   maxU, maxV);
            tess.addVertexWithUV(bx + 1,   ySE, bz + 1,   maxU, maxV);
            // South tri (SE, C, SW)
            tess.addVertexWithUV(bx + 1,   ySE, bz + 1,   maxU, maxV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx,       ySW, bz + 1,   minU, maxV);
            tess.addVertexWithUV(bx,       ySW, bz + 1,   minU, maxV);
            // West tri (SW, C, NW)
            tess.addVertexWithUV(bx,       ySW, bz + 1,   minU, maxV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx,       yNW, bz,       minU, minV);
            tess.addVertexWithUV(bx,       yNW, bz,       minU, minV);
        } else {
            // Bottom surface (hangs downward) -- normal -Y -- CW from above: NW,NE,C per tri
            double yNW = by + (1 - nn), yNE = by + (1 - pn),
                   ySW = by + (1 - np), ySE = by + (1 - pp), yC = by + (1 - cy);
            // North tri (NW, NE, C) → normal -Y
            tess.addVertexWithUV(bx,       yNW, bz,       minU, minV);
            tess.addVertexWithUV(bx + 1,   yNE, bz,       maxU, minV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            // East tri (NE, SE, C)
            tess.addVertexWithUV(bx + 1,   yNE, bz,       maxU, minV);
            tess.addVertexWithUV(bx + 1,   ySE, bz + 1,   maxU, maxV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            // South tri (SE, SW, C)
            tess.addVertexWithUV(bx + 1,   ySE, bz + 1,   maxU, maxV);
            tess.addVertexWithUV(bx,       ySW, bz + 1,   minU, maxV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            // West tri (SW, NW, C)
            tess.addVertexWithUV(bx,       ySW, bz + 1,   minU, maxV);
            tess.addVertexWithUV(bx,       yNW, bz,       minU, minV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
            tess.addVertexWithUV(bx + 0.5, yC,  bz + 0.5, midU, midV);
        }
    }
}
