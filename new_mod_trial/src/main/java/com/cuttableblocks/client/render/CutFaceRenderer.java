package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;
import java.util.ArrayList;

import java.util.List;

/**
 * Renders cut faces with proper texture padding to avoid stretching.
 * 
 * The cut face may be larger than 1x1 block size (e.g., diagonal cut has size sqrt(2) x 1).
 * Instead of stretching the texture or tiling it, we use padding:
 * - The center 1x1 area shows the original texture
 * - The surrounding areas show repeated edge pixels (padding)
 * 
 * This preserves the pixel density of the texture across all faces.
 */
public class CutFaceRenderer {
    
    private static final Tessellator tess = Tessellator.instance;
    
    /**
     * Renders a cut face with padding to avoid texture stretching.
     * 
     * @param x Block X position
     * @param y Block Y position
     * @param z Block Z position
     * @param points Intersection points defining the cut face polygon
     * @param nx Normal X
     * @param ny Normal Y
     * @param nz Normal Z
     * @param originalBlock The original block for texture
     * @param meta Block metadata
     */
    public static void renderCutFaceWithPadding(int x, int y, int z, List<Vec3> points,
                                                 float nx, float ny, float nz,
                                                 Block originalBlock, int meta) {
        
        if (points.size() < 3) return;
        
        IIcon icon = originalBlock.getIcon(0, meta);
        
        // Calculate bounding box of the cut face
        double minX = Double.MAX_VALUE, minY = Double.MAX_VALUE, minZ = Double.MAX_VALUE;
        double maxX = -Double.MAX_VALUE, maxY = -Double.MAX_VALUE, maxZ = -Double.MAX_VALUE;
        
        for (Vec3 p : points) {
            minX = Math.min(minX, p.xCoord);
            minY = Math.min(minY, p.yCoord);
            minZ = Math.min(minZ, p.zCoord);
            maxX = Math.max(maxX, p.xCoord);
            maxY = Math.max(maxY, p.yCoord);
            maxZ = Math.max(maxZ, p.zCoord);
        }
        
        // Calculate face size in world units
        double faceWidth, faceHeight;
        boolean isXFace = (maxX - minX) < 0.01;
        boolean isYFace = (maxY - minY) < 0.01;
        boolean isZFace = (maxZ - minZ) < 0.01;
        
        if (isXFace) {
            faceWidth = maxY - minY;
            faceHeight = maxZ - minZ;
        } else if (isYFace) {
            faceWidth = maxX - minX;
            faceHeight = maxZ - minZ;
        } else if (isZFace) {
            faceWidth = maxX - minX;
            faceHeight = maxY - minY;
        } else {
            // Diagonal face - calculate actual size
            faceWidth = Math.sqrt((maxX-minX)*(maxX-minX) + (maxY-minY)*(maxY-minY));
            faceHeight = Math.sqrt((maxZ-minZ)*(maxZ-minZ));
        }
        
        // Sort points for rendering
        Vec3 center = calculateCentroid(points);
        List<Vec3> sortedPoints = sortPointsByAngle(points, center, nx, ny, nz);
        
        // Render the polygon with padded UV mapping
        for (int i = 1; i < sortedPoints.size() - 1; i++) {
            addVertexWithPaddedUV(x, y, z, sortedPoints.get(0), icon, 
                                   faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ,
                                   isXFace, isYFace, isZFace);
            addVertexWithPaddedUV(x, y, z, sortedPoints.get(i), icon,
                                   faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ,
                                   isXFace, isYFace, isZFace);
            addVertexWithPaddedUV(x, y, z, sortedPoints.get(i + 1), icon,
                                   faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ,
                                   isXFace, isYFace, isZFace);
        }
    }
    
    /**
     * Maps a vertex to UV coordinates with padding.
     * 
     * UV mapping:
     * - If the vertex is within the central 1x1 area: use normal UV (0-1)
     * - If outside: clamp UV to edges (padding with edge pixels)
     */
    private static void addVertexWithPaddedUV(int x, int y, int z, Vec3 point, IIcon icon,
                                               double faceWidth, double faceHeight,
                                               double minX, double minY, double minZ,
                                               double maxX, double maxY, double maxZ,
                                               boolean isXFace, boolean isYFace, boolean isZFace) {
        
        // Calculate normalized position within face bounds (0-1)
        double uNorm, vNorm;
        
        if (isXFace) {
            uNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
            vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
        } else if (isYFace) {
            uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
            vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
        } else if (isZFace) {
            uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
            vNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
        } else {
            // Diagonal - project to get UV
            if (Math.abs(maxX - minX) > Math.abs(maxY - minY)) {
                uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
            } else {
                uNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
            }
            if (Math.abs(maxZ - minZ) > 0.01) {
                vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
            } else {
                vNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
            }
        }
        
        // Convert to texture coordinates with PADDING
        // The face may be larger than 1x1, so we need to map:
        // - Center 1x1 area: normal texture (0-1)
        // - Outside areas: padding with edge pixels
        
        double texU, texV;
        
        // Scale UV based on face size relative to 1x1 block
        // If face is 1.5 wide, uNorm=0 is at -0.25, uNorm=1 is at 1.25 in texture space
        double uInTexSpace = (uNorm - 0.5) * faceWidth + 0.5;
        double vInTexSpace = (vNorm - 0.5) * faceHeight + 0.5;
        
        // Clamp to 0-1 range (this creates padding with edge pixels)
        texU = clamp(uInTexSpace, 0.0, 1.0);
        texV = clamp(vInTexSpace, 0.0, 1.0);
        
        // Get actual texture coordinates
        double uActual = icon.getInterpolatedU(texU * 16.0);
        double vActual = icon.getInterpolatedV(texV * 16.0);
        
        tess.addVertexWithUV(x + point.xCoord, y + point.yCoord, z + point.zCoord, uActual, vActual);
    }
    
    /**
     * Clamps a value between min and max.
     */
    private static double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }
    
    /**
     * Calculates centroid of a list of points.
     */
    private static Vec3 calculateCentroid(List<Vec3> points) {
        double cx = 0, cy = 0, cz = 0;
        for (Vec3 p : points) {
            cx += p.xCoord;
            cy += p.yCoord;
            cz += p.zCoord;
        }
        return Vec3.createVectorHelper(cx / points.size(), cy / points.size(), cz / points.size());
    }
    
    /**
     * Sorts points by angle around the center for proper polygon rendering.
     */
    private static List<Vec3> sortPointsByAngle(List<Vec3> points, Vec3 center, 
                                                 float nx, float ny, float nz) {
        List<Vec3> sorted = new ArrayList<>(points);
        
        // Sort based on angle around center
        sorted.sort((a, b) -> {
            double angleA, angleB;
            
            if (Math.abs(ny) > Math.abs(nx) && Math.abs(ny) > Math.abs(nz)) {
                // Project to XZ plane
                angleA = Math.atan2(a.zCoord - center.zCoord, a.xCoord - center.xCoord);
                angleB = Math.atan2(b.zCoord - center.zCoord, b.xCoord - center.xCoord);
            } else if (Math.abs(nx) > Math.abs(nz)) {
                // Project to YZ plane
                angleA = Math.atan2(a.zCoord - center.zCoord, a.yCoord - center.yCoord);
                angleB = Math.atan2(b.zCoord - center.zCoord, b.yCoord - center.yCoord);
            } else {
                // Project to XY plane
                angleA = Math.atan2(a.yCoord - center.yCoord, a.xCoord - center.xCoord);
                angleB = Math.atan2(b.yCoord - center.yCoord, b.xCoord - center.xCoord);
            }
            
            return Double.compare(angleA, angleB);
        });
        
        return sorted;
    }
}
