package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;

import java.util.List;

/**
 * Handles proper texture mapping for cut blocks.
 * Ensures textures are not stretched but clipped/tiled appropriately.
 */
public class TextureMapper {
    
    private static final Tessellator tess = Tessellator.instance;
    
    /**
     * Renders a face with proper texture mapping - no stretching!
     * For rectangular faces: shows appropriate portion of texture
     * For cut faces: tiles texture or uses padding
     */
    public static void renderTexturedFace(RenderBlocks renderer, Block block, 
                                           List<Vec3> vertices, int faceIndex,
                                           int x, int y, int z, TileEntityCuttable te) {
        
        if (vertices.size() < 3) return;
        
        Block originalBlock = te.getOriginalBlock();
        int meta = te.getOriginalMetadata();
        
        if (originalBlock == null) return;
        
        // Get texture from original block
        IIcon icon = originalBlock.getIcon(faceIndex, meta);
        
        // Calculate bounding box of the face
        double minX = Double.MAX_VALUE, minY = Double.MAX_VALUE, minZ = Double.MAX_VALUE;
        double maxX = -Double.MAX_VALUE, maxY = -Double.MAX_VALUE, maxZ = -Double.MAX_VALUE;
        
        for (Vec3 v : vertices) {
            minX = Math.min(minX, v.xCoord);
            minY = Math.min(minY, v.yCoord);
            minZ = Math.min(minZ, v.zCoord);
            maxX = Math.max(maxX, v.xCoord);
            maxY = Math.max(maxY, v.yCoord);
            maxZ = Math.max(maxZ, v.zCoord);
        }
        
        double width = maxX - minX;
        double height = maxY - minY;
        double depth = maxZ - minZ;
        
        // Determine dominant axis for UV mapping
        boolean isXFace = width < 0.01;  // Face is perpendicular to X
        boolean isYFace = height < 0.01; // Face is perpendicular to Y  
        boolean isZFace = depth < 0.01;  // Face is perpendicular to Z
        
        // For each vertex, calculate proper UV coordinates
        for (int i = 0; i < vertices.size(); i++) {
            Vec3 v = vertices.get(i);
            double u, vCoord;
            
            if (isXFace) {
                // X face: map YZ to UV
                u = (v.yCoord - minY) / Math.max(height, 0.001);
                vCoord = (v.zCoord - minZ) / Math.max(depth, 0.001);
            } else if (isYFace) {
                // Y face: map XZ to UV
                u = (v.xCoord - minX) / Math.max(width, 0.001);
                vCoord = (v.zCoord - minZ) / Math.max(depth, 0.001);
            } else if (isZFace) {
                // Z face: map XY to UV
                u = (v.xCoord - minX) / Math.max(width, 0.001);
                vCoord = (v.yCoord - minY) / Math.max(height, 0.001);
            } else {
                // Diagonal face - use local coordinates
                u = getUForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ);
                vCoord = getVForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ);
            }
            
            // Apply texture coordinates
            double uActual = icon.getInterpolatedU(u * 16.0);
            double vActual = icon.getInterpolatedV(vCoord * 16.0);
            
            tess.addVertexWithUV(v.xCoord, v.yCoord, v.zCoord, uActual, vActual);
        }
    }
    
    /**
     * Renders a face with REPEATING texture (tiling) instead of stretching.
     * Used for large cut faces to avoid stretched textures.
     */
    public static void renderTiledFace(RenderBlocks renderer, Block block,
                                        List<Vec3> vertices, int faceIndex,
                                        int x, int y, int z, TileEntityCuttable te) {
        
        if (vertices.size() < 3) return;
        
        Block originalBlock = te.getOriginalBlock();
        int meta = te.getOriginalMetadata();
        
        if (originalBlock == null) return;
        
        IIcon icon = originalBlock.getIcon(faceIndex, meta);
        
        // Calculate bounding box
        double minX = Double.MAX_VALUE, minY = Double.MAX_VALUE, minZ = Double.MAX_VALUE;
        double maxX = -Double.MAX_VALUE, maxY = -Double.MAX_VALUE, maxZ = -Double.MAX_VALUE;
        
        for (Vec3 v : vertices) {
            minX = Math.min(minX, v.xCoord);
            minY = Math.min(minY, v.yCoord);
            minZ = Math.min(minZ, v.zCoord);
            maxX = Math.max(maxX, v.xCoord);
            maxY = Math.max(maxY, v.yCoord);
            maxZ = Math.max(maxZ, v.zCoord);
        }
        
        double width = maxX - minX;
        double height = maxY - minY;
        double depth = maxZ - minZ;
        
        // Determine face size in texture units (16 = 1 full texture)
        double faceSizeU, faceSizeV;
        boolean isXFace = width < 0.01;
        boolean isYFace = height < 0.01;
        boolean isZFace = depth < 0.01;
        
        if (isXFace) {
            faceSizeU = height * 16.0;
            faceSizeV = depth * 16.0;
        } else if (isYFace) {
            faceSizeU = width * 16.0;
            faceSizeV = depth * 16.0;
        } else if (isZFace) {
            faceSizeU = width * 16.0;
            faceSizeV = height * 16.0;
        } else {
            // Diagonal - estimate size
            faceSizeU = Math.sqrt(width*width + height*height + depth*depth) * 16.0;
            faceSizeV = 16.0;
        }
        
        // For each vertex, calculate UV with tiling
        for (Vec3 v : vertices) {
            double u, vCoord;
            
            if (isXFace) {
                u = (v.yCoord - minY) / Math.max(height, 0.001) * (faceSizeU / 16.0);
                vCoord = (v.zCoord - minZ) / Math.max(depth, 0.001) * (faceSizeV / 16.0);
            } else if (isYFace) {
                u = (v.xCoord - minX) / Math.max(width, 0.001) * (faceSizeU / 16.0);
                vCoord = (v.zCoord - minZ) / Math.max(depth, 0.001) * (faceSizeV / 16.0);
            } else if (isZFace) {
                u = (v.xCoord - minX) / Math.max(width, 0.001) * (faceSizeU / 16.0);
                vCoord = (v.yCoord - minY) / Math.max(height, 0.001) * (faceSizeV / 16.0);
            } else {
                u = getUForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ) * (faceSizeU / 16.0);
                vCoord = getVForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ) * (faceSizeV / 16.0);
            }
            
            // Wrap UV coordinates for tiling (modulo 1.0)
            double uWrapped = u - Math.floor(u);
            double vWrapped = vCoord - Math.floor(vCoord);
            
            double uActual = icon.getInterpolatedU(uWrapped * 16.0);
            double vActual = icon.getInterpolatedV(vWrapped * 16.0);
            
            tess.addVertexWithUV(v.xCoord, v.yCoord, v.zCoord, uActual, vActual);
        }
    }
    
    /**
     * Renders a face with CENTERED TILING for large cut faces.
     * Creates a tiling pattern centered on the face - the texture
     * repeats in a grid, and we sample only the fragment needed
     * for our polygon. The tiling is centered on the face center.
     * 
     * Example: face is 22.6px wide (1.41 * 16), texture is 16px
     * - We need 2 tiles (32px) to cover the face
     * - Tiling is centered: face center aligns with texture center (8px)
     * - UVs wrap around for seamless tiling
     * 
     * @param vertices List of vertices defining the polygon
     * @param faceIndex Face index (0-5) for texture selection
     * @param x,y,z Block position
     * @param te TileEntity with original block info
     */
    public static void renderTiledCenteredFace(RenderBlocks renderer, Block block,
                                                List<Vec3> vertices, int faceIndex,
                                                int x, int y, int z, TileEntityCuttable te) {
        
        if (vertices.size() < 3) return;
        
        Block originalBlock = te.getOriginalBlock();
        int meta = te.getOriginalMetadata();
        
        if (originalBlock == null) return;
        
        IIcon icon = originalBlock.getIcon(faceIndex, meta);
        
        // Calculate bounding box
        double minX = Double.MAX_VALUE, minY = Double.MAX_VALUE, minZ = Double.MAX_VALUE;
        double maxX = -Double.MAX_VALUE, maxY = -Double.MAX_VALUE, maxZ = -Double.MAX_VALUE;
        
        for (Vec3 v : vertices) {
            minX = Math.min(minX, v.xCoord);
            minY = Math.min(minY, v.yCoord);
            minZ = Math.min(minZ, v.zCoord);
            maxX = Math.max(maxX, v.xCoord);
            maxY = Math.max(maxY, v.yCoord);
            maxZ = Math.max(maxZ, v.zCoord);
        }
        
        double width = maxX - minX;
        double height = maxY - minY;
        double depth = maxZ - minZ;
        
        // Determine face dimensions for UV mapping
        boolean isXFace = width < 0.01;
        boolean isYFace = height < 0.01;
        boolean isZFace = depth < 0.01;
        
        double faceSizeU, faceSizeV;
        if (isXFace) {
            faceSizeU = height * 16.0;
            faceSizeV = depth * 16.0;
        } else if (isYFace) {
            faceSizeU = width * 16.0;
            faceSizeV = depth * 16.0;
        } else if (isZFace) {
            faceSizeU = width * 16.0;
            faceSizeV = height * 16.0;
        } else {
            // Diagonal face - use actual dimensions
            faceSizeU = Math.sqrt(width*width + height*height) * 16.0;
            faceSizeV = depth * 16.0;
        }
        
        // Face center for coordinate calculations
        double cx = (minX + maxX) / 2.0;
        double cy = (minY + maxY) / 2.0;
        double cz = (minZ + maxZ) / 2.0;
        
        // Render each vertex with centered tiling UVs
        for (Vec3 v : vertices) {
            // Calculate local coordinates relative to face center (-0.5 to 0.5 range)
            double uLocal, vLocal;
            
            if (isXFace) {
                uLocal = (v.yCoord - cy) / Math.max(height, 0.001);
                vLocal = (v.zCoord - cz) / Math.max(depth, 0.001);
            } else if (isYFace) {
                uLocal = (v.xCoord - cx) / Math.max(width, 0.001);
                vLocal = (v.zCoord - cz) / Math.max(depth, 0.001);
            } else if (isZFace) {
                uLocal = (v.xCoord - cx) / Math.max(width, 0.001);
                vLocal = (v.yCoord - cy) / Math.max(height, 0.001);
            } else {
                // Diagonal - project to local coordinates
                double uProj = getUForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ);
                double vProj = getVForDiagonal(v, minX, minY, minZ, maxX, maxY, maxZ);
                uLocal = uProj - 0.5;
                vLocal = vProj - 0.5;
            }
            
            // Convert to texture pixel coordinates
            // Face center (0) maps to texture center (8px)
            // Face extends by faceSize/2 pixels on each side
            double uPixelOffset = uLocal * (faceSizeU / 2.0);
            double vPixelOffset = vLocal * (faceSizeV / 2.0);
            
            // Center is at 8px, so we add 8 and wrap around 16
            double uPixel = 8.0 + uPixelOffset;
            double vPixel = 8.0 + vPixelOffset;
            
            // Wrap to 0-16 range for seamless tiling
            double uWrapped = ((uPixel % 16.0) + 16.0) % 16.0;
            double vWrapped = ((vPixel % 16.0) + 16.0) % 16.0;
            
            // Convert to actual UV coordinates
            double uFinal = icon.getInterpolatedU(uWrapped);
            double vFinal = icon.getInterpolatedV(vWrapped);
            
            tess.addVertexWithUV(v.xCoord, v.yCoord, v.zCoord, uFinal, vFinal);
        }
    }
    
    /**
     * Renders a partial face showing only a portion of the texture (no stretching).
     * For half-blocks etc.
     */
    public static void renderClippedFace(RenderBlocks renderer, Block block,
                                          double minX, double minY, double minZ,
                                          double maxX, double maxY, double maxZ,
                                          int faceIndex, int x, int y, int z, 
                                          TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        int meta = te.getOriginalMetadata();
        
        if (originalBlock == null) return;
        
        IIcon icon = originalBlock.getIcon(faceIndex, meta);
        
        // Calculate which portion of texture to show
        double uMin, uMax, vMin, vMax;
        
        // For a partial block, show corresponding portion of texture
        // e.g., top half of block = top half of texture
        uMin = (minX - x) * 16.0;
        uMax = (maxX - x) * 16.0;
        vMin = (minZ - z) * 16.0;
        vMax = (maxZ - z) * 16.0;
        
        // Use RenderBlocks to draw with clipped texture coordinates
        renderer.setRenderBounds(minX - x, minY - y, minZ - z, 
                                  maxX - x, maxY - y, maxZ - z);
        
        // Draw with custom UV mapping
        drawFaceWithCustomUV(renderer, block, x, y, z, icon, 
                             uMin, uMax, vMin, vMax, faceIndex);
    }
    
    private static void drawFaceWithCustomUV(RenderBlocks renderer, Block block,
                                              int x, int y, int z, IIcon icon,
                                              double uMin, double uMax, 
                                              double vMin, double vMax, int face) {
        
        double u1 = icon.getInterpolatedU(uMin);
        double u2 = icon.getInterpolatedU(uMax);
        double v1 = icon.getInterpolatedV(vMin);
        double v2 = icon.getInterpolatedV(vMax);
        
        // Use standard RenderBlocks methods but with custom bounds
        switch (face) {
            case 0: // Bottom (Y-)
                renderer.renderFaceYNeg(block, x, y, z, icon);
                break;
            case 1: // Top (Y+)
                renderer.renderFaceYPos(block, x, y, z, icon);
                break;
            case 2: // North (Z-)
                renderer.renderFaceZNeg(block, x, y, z, icon);
                break;
            case 3: // South (Z+)
                renderer.renderFaceZPos(block, x, y, z, icon);
                break;
            case 4: // West (X-)
                renderer.renderFaceXNeg(block, x, y, z, icon);
                break;
            case 5: // East (X+)
                renderer.renderFaceXPos(block, x, y, z, icon);
                break;
        }
    }
    
    private static double getUForDiagonal(Vec3 v, double minX, double minY, double minZ,
                                           double maxX, double maxY, double maxZ) {
        // Project onto plane and calculate local U coordinate
        double rangeX = maxX - minX;
        double rangeY = maxY - minY;
        double rangeZ = maxZ - minZ;
        
        if (rangeX > rangeY && rangeX > rangeZ) {
            return (v.xCoord - minX) / rangeX;
        } else if (rangeY > rangeZ) {
            return (v.yCoord - minY) / rangeY;
        } else {
            return (v.zCoord - minZ) / rangeZ;
        }
    }
    
    private static double getVForDiagonal(Vec3 v, double minX, double minY, double minZ,
                                           double maxX, double maxY, double maxZ) {
        // Second dimension for diagonal faces
        double rangeX = maxX - minX;
        double rangeY = maxY - minY;
        double rangeZ = maxZ - minZ;
        
        if (rangeX < rangeY && rangeX < rangeZ) {
            return (v.xCoord - minX) / Math.max(rangeX, 0.001);
        } else if (rangeY < rangeZ) {
            return (v.zCoord - minZ) / Math.max(rangeZ, 0.001);
        } else {
            return (v.yCoord - minY) / Math.max(rangeY, 0.001);
        }
    }
}
