package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.world.IBlockAccess;

/**
 * Helper class for rendering cuttable blocks.
 * Based on rendering techniques from Carpenter's Blocks.
 * 
 * Implements 16x16 grid snapping for cut planes - planes are rounded to
 * points on block edges divided into 16 equal segments (matching Minecraft's
 * 16x16 texture pixels). This ensures consistent texture mapping and reduces
 * z-fighting artifacts.
 */
public class RenderHelper {
    
    public static final int GRID_SEGMENTS = 16;
    
    private static final Tessellator tessellator = Tessellator.instance;
    
    /**
     * Renders a cut block with the given plane parameters.
     * 
     * @param renderer The RenderBlocks instance
     * @param block The block being rendered (BlockCuttable)
     * @param x Block X position
     * @param y Block Y position  
     * @param z Block Z position
     * @param te The TileEntity containing cut data
     * @return true if rendered successfully
     */
    public static boolean renderCutBlock(RenderBlocks renderer, Block block, 
                                         int x, int y, int z, TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        if (originalBlock == null) {
            return false;
        }
        
        float nx = te.getNormalX();
        float ny = te.getNormalY();
        float nz = te.getNormalZ();
        
        // Check if cut is axis-aligned (simplified) or diagonal (advanced)
        float absNx = Math.abs(nx);
        float absNy = Math.abs(ny);
        float absNz = Math.abs(nz);
        
        boolean isAxisAligned = (absNx > 0.95f || absNy > 0.95f || absNz > 0.95f) ||
                                (absNx < 0.05f && absNy < 0.05f) ||
                                (absNx < 0.05f && absNz < 0.05f) ||
                                (absNy < 0.05f && absNz < 0.05f);
        
        if (isAxisAligned) {
            // Use simple rendering for axis-aligned cuts
            return renderAxisAlignedCut(renderer, block, x, y, z, te);
        } else {
            // Use advanced rendering for diagonal cuts
            return AdvancedCutRenderer.renderAdvancedCut(renderer, block, x, y, z, te);
        }
    }
    
    /**
     * Renders an axis-aligned cut (simpler and more efficient).
     */
    private static boolean renderAxisAlignedCut(RenderBlocks renderer, Block block,
                                                 int x, int y, int z, TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        int originalMeta = te.getOriginalMetadata();
        float nx = te.getNormalX();
        float ny = te.getNormalY();
        float nz = te.getNormalZ();
        boolean keepPositive = te.keepPositiveSide();
        
        float absNx = Math.abs(nx);
        float absNy = Math.abs(ny);
        float absNz = Math.abs(nz);
        
        // Save original block bounds
        double prevMinX = renderer.renderMinX;
        double prevMinY = renderer.renderMinY;
        double prevMinZ = renderer.renderMinZ;
        double prevMaxX = renderer.renderMaxX;
        double prevMaxY = renderer.renderMaxY;
        double prevMaxZ = renderer.renderMaxZ;
        
        // Render based on dominant normal direction
        if (absNy > absNx && absNy > absNz) {
            // Dominant Y - horizontal cut
            renderHorizontalCut(renderer, originalBlock, x, y, z, originalMeta, ny > 0 == keepPositive);
        } else if (absNx > absNz) {
            // Dominant X - vertical cut along X
            renderVerticalXCut(renderer, originalBlock, x, y, z, originalMeta, nx > 0 == keepPositive);
        } else {
            // Dominant Z - vertical cut along Z
            renderVerticalZCut(renderer, originalBlock, x, y, z, originalMeta, nz > 0 == keepPositive);
        }
        
        // Restore block bounds
        renderer.setRenderBounds(prevMinX, prevMinY, prevMinZ, prevMaxX, prevMaxY, prevMaxZ);
        
        return true;
    }
    
    /**
     * Renders a horizontal cut (top or bottom half) with proper texture mapping.
     * Textures are NOT stretched - we show only the appropriate portion.
     */
    private static void renderHorizontalCut(RenderBlocks renderer, Block block, 
                                            int x, int y, int z, int meta, boolean topHalf) {
        Tessellator tess = Tessellator.instance;
        
        // Get textures for all faces
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        IIcon iconSide = block.getIcon(2, meta); // North/South side
        
        double yMin = topHalf ? 0.5 : 0.0;
        double yMax = topHalf ? 1.0 : 0.5;
        
        // Top face (Y+) - full texture
        if (topHalf) {
            tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconTop.getMinU(), iconTop.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconTop.getMaxU(), iconTop.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconTop.getMaxU(), iconTop.getMinV());
            tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconTop.getMinU(), iconTop.getMinV());
        }
        
        // Bottom face (Y-) - full texture
        if (!topHalf) {
            tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconBottom.getMinU(), iconBottom.getMinV());
            tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconBottom.getMaxU(), iconBottom.getMinV());
            tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconBottom.getMaxU(), iconBottom.getMaxV());
            tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconBottom.getMinU(), iconBottom.getMaxV());
        }
        
        // Side faces - show only half of texture (clipped, not stretched!)
        double vMin = iconSide.getMinV();
        double vMax = iconSide.getMaxV();
        double vMid = iconSide.getInterpolatedV(topHalf ? 8.0 : 8.0); // Middle of texture
        
        double vTop = topHalf ? vMax : vMid;
        double vBottom = topHalf ? vMid : vMin;
        
        // North face (Z-)
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        
        // South face (Z+)
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconSide.getMinU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconSide.getMinU(), vBottom);
        
        // West face (X-)
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 0.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        
        // East face (X+)
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 0.0, iconSide.getMinU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMin, z + 1.0, iconSide.getMaxU(), vBottom);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 1.0, iconSide.getMaxU(), vTop);
        tess.addVertexWithUV(x + 1.0, y + yMax, z + 0.0, iconSide.getMinU(), vTop);
        
        // Cut face (horizontal plane at Y=0.5) - tile texture with padding
        if (true) { // Always render cut face
            IIcon cutIcon = block.getIcon(1, meta);
            // Use tiled texture for cut face
            double u0 = cutIcon.getMinU();
            double u1 = cutIcon.getMaxU();
            double v0 = cutIcon.getMinV();
            double v1 = cutIcon.getMaxV();
            
            tess.addVertexWithUV(x + 0.0, y + 0.5, z + 1.0, u0, v1);
            tess.addVertexWithUV(x + 1.0, y + 0.5, z + 1.0, u1, v1);
            tess.addVertexWithUV(x + 1.0, y + 0.5, z + 0.0, u1, v0);
            tess.addVertexWithUV(x + 0.0, y + 0.5, z + 0.0, u0, v0);
        }
    }
    
    /**
     * Renders a vertical cut along X axis (east or west half) with proper textures.
     */
    private static void renderVerticalXCut(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta, boolean eastHalf) {
        Tessellator tess = Tessellator.instance;
        
        IIcon iconSide = block.getIcon(2, meta);
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        
        double xMin = eastHalf ? 0.5 : 0.0;
        double xMax = eastHalf ? 1.0 : 0.5;
        
        // West/East face - full texture on the solid side
        if (!eastHalf) {
            // West face visible
            tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, iconSide.getMinU(), iconSide.getMinV());
        } else {
            // East face visible
            tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, iconSide.getMinU(), iconSide.getMinV());
        }
        
        // Top/Bottom - show half texture (clipped)
        double uMin = iconTop.getMinU();
        double uMax = iconTop.getMaxU();
        double uMid = iconTop.getInterpolatedU(eastHalf ? 8.0 : 8.0);
        
        double uLeft = eastHalf ? uMid : uMin;
        double uRight = eastHalf ? uMax : uMid;
        
        // Top face
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, uLeft, iconTop.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, uRight, iconTop.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, uRight, iconTop.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, uLeft, iconTop.getMinV());
        
        // Bottom face
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, uLeft, iconBottom.getMinV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, uRight, iconBottom.getMinV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, uRight, iconBottom.getMaxV());
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, uLeft, iconBottom.getMaxV());
        
        // North/South faces - half texture
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 0.0, uLeft, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 0.0, uRight, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 0.0, uRight, iconSide.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 0.0, uLeft, iconSide.getMinV());
        
        tess.addVertexWithUV(x + xMin, y + 0.0, z + 1.0, uLeft, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 0.0, z + 1.0, uRight, iconSide.getMaxV());
        tess.addVertexWithUV(x + xMax, y + 1.0, z + 1.0, uRight, iconSide.getMinV());
        tess.addVertexWithUV(x + xMin, y + 1.0, z + 1.0, uLeft, iconSide.getMinV());
        
        // Cut face at X=0.5 - tile texture
        IIcon cutIcon = block.getIcon(4, meta);
        tess.addVertexWithUV(x + 0.5, y + 0.0, z + 1.0, cutIcon.getMinU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.5, y + 1.0, z + 1.0, cutIcon.getMaxU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.5, y + 1.0, z + 0.0, cutIcon.getMaxU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 0.5, y + 0.0, z + 0.0, cutIcon.getMinU(), cutIcon.getMinV());
    }
    
    /**
     * Renders a vertical cut along Z axis (south or north half) with proper textures.
     */
    private static void renderVerticalZCut(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta, boolean southHalf) {
        Tessellator tess = Tessellator.instance;
        
        IIcon iconSide = block.getIcon(2, meta);
        IIcon iconTop = block.getIcon(1, meta);
        IIcon iconBottom = block.getIcon(0, meta);
        
        double zMin = southHalf ? 0.5 : 0.0;
        double zMax = southHalf ? 1.0 : 0.5;
        
        // North/South face - full texture
        if (!southHalf) {
            tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        } else {
            tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, iconSide.getMinU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
            tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
            tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, iconSide.getMinU(), iconSide.getMaxV());
        }
        
        // Top/Bottom - half texture
        double uMin = iconTop.getMinU();
        double uMax = iconTop.getMaxU();
        double uMid = iconTop.getInterpolatedU(8.0);
        double uLeft = southHalf ? uMid : uMin;
        double uRight = southHalf ? uMax : uMid;
        
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, uLeft, iconTop.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, uRight, iconTop.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, uRight, iconTop.getMinV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, uLeft, iconTop.getMinV());
        
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, uLeft, iconBottom.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, uRight, iconBottom.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, uRight, iconBottom.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, uLeft, iconBottom.getMaxV());
        
        // West/East faces - half texture
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMin, iconSide.getMinU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + zMax, iconSide.getMaxU(), iconSide.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMax, iconSide.getMaxU(), iconSide.getMaxV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + zMin, iconSide.getMinU(), iconSide.getMaxV());
        
        // Cut face at Z=0.5 - tile texture
        IIcon cutIcon = block.getIcon(2, meta);
        tess.addVertexWithUV(x + 0.0, y + 0.0, z + 0.5, cutIcon.getMinU(), cutIcon.getMaxV());
        tess.addVertexWithUV(x + 0.0, y + 1.0, z + 0.5, cutIcon.getMinU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 1.0, z + 0.5, cutIcon.getMaxU(), cutIcon.getMinV());
        tess.addVertexWithUV(x + 1.0, y + 0.0, z + 0.5, cutIcon.getMaxU(), cutIcon.getMaxV());
    }
    
    /**
     * Renders the "cut face" - the diagonal face created by the plane.
     * This is more complex and requires custom vertex drawing.
     */
    public static void renderCutFace(RenderBlocks renderer, Block block,
                                     int x, int y, int z, TileEntityCuttable te) {
        
        // Get the original block's icons
        IIcon icon = block.getIcon(0, 0);
        
        // Calculate intersection points of plane with cube edges
        // This would create a polygon that represents the cut surface
        
        // For simplified version, we skip the diagonal face rendering
        // In full implementation, this would draw a polygon with proper UV mapping
    }
}
