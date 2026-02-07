package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import com.cuttableblocks.util.CutDirections;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;

/**
 * Helper class for rendering cuttable blocks.
 * Fixed: deterministic axis detection, proper brightness, z-fighting offset, EPS comparisons.
 */
public class RenderHelper {
    
    private static final Tessellator tess = Tessellator.instance;
    private static final double Z_FIGHT_OFFSET = 1e-4;
    private static final double EPSILON = 1e-6;
    
    /**
     * Renders a cut block.
     * Deterministically chooses between axis-aligned and advanced rendering based on reconstructed normal.
     */
    public static boolean renderCutBlock(RenderBlocks renderer, Block block, 
                                         int x, int y, int z, TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        if (originalBlock == null) {
            return false;
        }
        
        // Get deterministic normal from rotId/dirId (ignore cached normalX/Y/Z)
        Vec3 nWorld = CutDirections.getWorldDir(te.getRotId(), te.getDirId());
        double nx = nWorld.xCoord;
        double ny = nWorld.yCoord;
        double nz = nWorld.zCoord;
        boolean keepPositive = te.keepPositiveSide();
        int meta = te.getOriginalMetadata();
        
        // Deterministic axis detection (exact axis check)
        double absNx = Math.abs(nx);
        double absNy = Math.abs(ny);
        double absNz = Math.abs(nz);
        
        boolean isAxisX = absNx > 0.999999 && absNy < EPSILON && absNz < EPSILON;
        boolean isAxisY = absNy > 0.999999 && absNx < EPSILON && absNz < EPSILON;
        boolean isAxisZ = absNz > 0.999999 && absNx < EPSILON && absNy < EPSILON;
        
        // Section 3: keepPositive means keep dist >= 0 side
        if (isAxisY) {
            // ny > 0 means normal points up
            // keepPositive=true -> keep upper half (dist >= 0)
            boolean keepTop = (ny > 0) == keepPositive;
            renderHorizontalCut(renderer, originalBlock, x, y, z, meta, keepTop);
            return true;
        } else if (isAxisX) {
            boolean keepEast = (nx > 0) == keepPositive;
            renderVerticalXCut(renderer, originalBlock, x, y, z, meta, keepEast);
            return true;
        } else if (isAxisZ) {
            boolean keepSouth = (nz > 0) == keepPositive;
            renderVerticalZCut(renderer, originalBlock, x, y, z, meta, keepSouth);
            return true;
        } else {
            // Not axis-aligned, use advanced renderer
            return AdvancedCutRenderer.renderAdvancedCut(renderer, block, x, y, z, te);
        }
    }
    
    /**
     * Renders a horizontal cut (top or bottom half).
     * Fixed: z-fighting offset, proper brightness/color for each face.
     */
    public static void renderHorizontalCut(RenderBlocks renderer, Block block, 
                                            int x, int y, int z, int meta, boolean topHalf) {
        
        // Get brightness for this block
        int brightness = block.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
        
        // Get textures
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        IIcon iconSide = block.getIcon(2, meta);
        
        double yMin = topHalf ? 0.5 : 0.0;
        double yMax = topHalf ? 1.0 : 0.5;
        
        // Anti z-fighting offset for cut-face
        double yOffset = topHalf ? Z_FIGHT_OFFSET : -Z_FIGHT_OFFSET;
        
        // Top face (Y+) - full texture
        if (topHalf) {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconTop.getMinU(), iconTop.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconTop.getMaxU(), iconTop.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconTop.getMaxU(), iconTop.getMinV());
            tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconTop.getMinU(), iconTop.getMinV());
        }
        
        // Bottom face (Y-) - full texture
        if (!topHalf) {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconBottom.getMinU(), iconBottom.getMinV());
            tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconBottom.getMaxU(), iconBottom.getMinV());
            tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconBottom.getMaxU(), iconBottom.getMaxV());
            tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconBottom.getMinU(), iconBottom.getMaxV());
        }
        
        // Side faces - half texture (clipped, not stretched)
        double vMin = iconSide.getMinV();
        double vMax = iconSide.getMaxV();
        double vMid = iconSide.getInterpolatedV(8.0);
        
        double vTop = topHalf ? vMax : vMid;
        double vBottom = topHalf ? vMid : vMin;
        
        // North face (Z-)
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        
        // South face (Z+)
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconSide.getMinU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconSide.getMinU(), vBottom);
        
        // West face (X-)
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        
        // East face (X+)
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        
        // Cut face (horizontal plane at Y=0.5) with offset and proper color
        IIcon cutIcon = block.getIcon(1, meta);
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + 0.5 + yOffset, z + 1.0, cutIcon.getMinU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 0.5 + yOffset, z + 1.0, cutIcon.getMaxU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 0.5 + yOffset, z + 0.0, cutIcon.getMaxU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 0.0, y + 0.5 + yOffset, z + 0.0, cutIcon.getMinU(), cutIcon.getMinV());
    }
    
    /**
     * Renders a vertical cut along X axis.
     */
    public static void renderVerticalXCut(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta, boolean eastHalf) {
        int brightness = block.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
        
        IIcon iconSide = block.getIcon(2, meta);
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        
        double xMin = eastHalf ? 0.5 : 0.0;
        double xMax = eastHalf ? 1.0 : 0.5;
        double xOffset = eastHalf ? Z_FIGHT_OFFSET : -Z_FIGHT_OFFSET;
        
        // West/East face
        if (!eastHalf) {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, iconSide.getMinU(), iconSide.getMinV());
        } else {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, iconSide.getMinU(), iconSide.getMinV());
        }
        
        // Top/Bottom - half texture (clipped, not stretched)
        double uMin = iconTop.getMinU();
        double uMax = iconTop.getMaxU();
        double uMid = iconTop.getInterpolatedU(8.0);
        
        double uLeft = eastHalf ? uMid : uMin;
        double uRight = eastHalf ? uMax : uMid;
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, uLeft, iconTop.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, uRight, iconTop.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, uRight, iconTop.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, uLeft, iconTop.getMinV());
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, uLeft, iconBottom.getMinV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, uRight, iconBottom.getMinV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, uRight, iconBottom.getMaxV());
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, uLeft, iconBottom.getMaxV());
        
        // North/South faces - half texture
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, uLeft, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, uRight, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, uRight, iconSide.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, uLeft, iconSide.getMinV());
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, uLeft, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, uRight, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, uRight, iconSide.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, uLeft, iconSide.getMinV());
        
        // Cut face at X=0.5 with offset
        IIcon cutIcon = block.getIcon(4, meta);
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.5 + xOffset, y + 0.0, z + 1.0, cutIcon.getMinU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.5 + xOffset, y + 1.0, z + 1.0, cutIcon.getMaxU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.5 + xOffset, y + 1.0, z + 0.0, cutIcon.getMaxU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 0.5 + xOffset, y + 0.0, z + 0.0, cutIcon.getMinU(), cutIcon.getMinV());
    }
    
    /**
     * Renders a vertical cut along Z axis.
     */
    public static void renderVerticalZCut(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta, boolean southHalf) {
        int brightness = block.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
        
        IIcon iconSide = block.getIcon(2, meta);
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        
        double zMin = southHalf ? 0.5 : 0.0;
        double zMax = southHalf ? 1.0 : 0.5;
        double zOffset = southHalf ? Z_FIGHT_OFFSET : -Z_FIGHT_OFFSET;
        
        // North/South face
        if (!southHalf) {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        } else {
            tess.setBrightness(brightness);
            tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
            tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, iconSide.getMinU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, iconSide.getMinU(), iconSide.getMaxV());
        }
        
        // Top/Bottom - half texture (clipped)
        double uMin = iconTop.getMinU();
        double uMax = iconTop.getMaxU();
        double uMid = iconTop.getInterpolatedU(8.0);
        double uLeft = southHalf ? uMid : uMin;
        double uRight = southHalf ? uMax : uMid;
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, uLeft, iconTop.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, uRight, iconTop.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, uRight, iconTop.getMinV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, uLeft, iconTop.getMinV());
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, uLeft, iconBottom.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, uRight, iconBottom.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, uRight, iconBottom.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, uLeft, iconBottom.getMaxV());
        
        // West/East faces
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
        
        // Cut face at Z=0.5 with offset
        IIcon cutIcon = block.getIcon(2, meta);
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + 0.5 + zOffset, cutIcon.getMinU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + 0.5 + zOffset, cutIcon.getMinU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + 0.5 + zOffset, cutIcon.getMaxU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + 0.5 + zOffset, cutIcon.getMaxU(), cutIcon.getMaxV());
    }
}
