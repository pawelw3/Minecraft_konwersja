package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Advanced renderer for cuttable blocks supporting arbitrary plane cuts.
 * Renders a block cut by a plane passing through its center.
 */
public class AdvancedCutRenderer {
    
    private static final Tessellator tess = Tessellator.instance;
    
    /**
     * Renders a block cut by a plane with proper face culling.
     */
    public static boolean renderAdvancedCut(RenderBlocks renderer, Block block, 
                                            int x, int y, int z, TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        if (originalBlock == null) {
            return false;
        }
        
        float nx = te.getNormalX();
        float ny = te.getNormalY();
        float nz = te.getNormalZ();
        boolean keepPositive = te.keepPositiveSide();
        int meta = te.getOriginalMetadata();
        
        // Calculate plane intersection points with cube edges
        List<Vec3> intersections = calculateIntersections(nx, ny, nz);
        if (intersections.size() < 3) {
            // Not enough points to form a polygon, fallback to simple cut
            return false;
        }
        
        // Determine which cube faces are visible (not cut off)
        renderVisibleFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive);
        
        // Render the cut face (the polygon created by the plane)
        renderCutFace(x, y, z, intersections, nx, ny, nz, keepPositive, originalBlock, meta);
        
        return true;
    }
    
    /**
     * Calculate intersection points of the plane with cube edges.
     * Plane equation: nx*(x-0.5) + ny*(y-0.5) + nz*(z-0.5) = 0
     * Or: nx*x + ny*y + nz*z = 0.5*(nx + ny + nz)
     */
    private static List<Vec3> calculateIntersections(float nx, float ny, float nz) {
        List<Vec3> points = new ArrayList<>();
        float d = 0.5f * (nx + ny + nz);
        
        // Check all 12 edges of the unit cube [0,1]x[0,1]x[0,1]
        
        // Edges parallel to X axis (y=0/1, z=0/1)
        checkEdgeX(points, nx, ny, nz, d, 0, 0);
        checkEdgeX(points, nx, ny, nz, d, 0, 1);
        checkEdgeX(points, nx, ny, nz, d, 1, 0);
        checkEdgeX(points, nx, ny, nz, d, 1, 1);
        
        // Edges parallel to Y axis (x=0/1, z=0/1)
        checkEdgeY(points, nx, ny, nz, d, 0, 0);
        checkEdgeY(points, nx, ny, nz, d, 0, 1);
        checkEdgeY(points, nx, ny, nz, d, 1, 0);
        checkEdgeY(points, nx, ny, nz, d, 1, 1);
        
        // Edges parallel to Z axis (x=0/1, y=0/1)
        checkEdgeZ(points, nx, ny, nz, d, 0, 0);
        checkEdgeZ(points, nx, ny, nz, d, 0, 1);
        checkEdgeZ(points, nx, ny, nz, d, 1, 0);
        checkEdgeZ(points, nx, ny, nz, d, 1, 1);
        
        return points;
    }
    
    private static void checkEdgeX(List<Vec3> points, float nx, float ny, float nz, 
                                    float d, int y, int z) {
        // Edge from (0,y,z) to (1,y,z), parametric: (t, y, z), t in [0,1]
        // Plane equation: nx*t + ny*y + nz*z = d
        if (Math.abs(nx) < 0.0001f) return;
        
        float t = (d - ny * y - nz * z) / nx;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(t, y, z));
        }
    }
    
    private static void checkEdgeY(List<Vec3> points, float nx, float ny, float nz,
                                    float d, int x, int z) {
        // Edge from (x,0,z) to (x,1,z), parametric: (x, t, z), t in [0,1]
        if (Math.abs(ny) < 0.0001f) return;
        
        float t = (d - nx * x - nz * z) / ny;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(x, t, z));
        }
    }
    
    private static void checkEdgeZ(List<Vec3> points, float nx, float ny, float nz,
                                    float d, int x, int y) {
        // Edge from (x,y,0) to (x,y,1), parametric: (x, y, t), t in [0,1]
        if (Math.abs(nz) < 0.0001f) return;
        
        float t = (d - nx * x - ny * y) / nz;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(x, y, t));
        }
    }
    
    /**
     * Renders the visible portions of the original cube faces.
     */
    private static void renderVisibleFaces(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta,
                                           float nx, float ny, float nz, 
                                           boolean keepPositive) {
        
        // For each of the 6 cube faces, check if it should be rendered
        // A face is rendered if its center is on the "keep" side of the plane
        
        double checkDist = keepPositive ? 0.001 : -0.001;
        
        // Bottom face (Y=0), center at (0.5, 0, 0.5)
        if (isPointOnKeepSide(0.5, 0, 0.5, nx, ny, nz, keepPositive, checkDist)) {
            renderBottomFace(renderer, block, x, y, z);
        }
        
        // Top face (Y=1), center at (0.5, 1, 0.5)
        if (isPointOnKeepSide(0.5, 1, 0.5, nx, ny, nz, keepPositive, checkDist)) {
            renderTopFace(renderer, block, x, y, z);
        }
        
        // North face (Z=0), center at (0.5, 0.5, 0)
        if (isPointOnKeepSide(0.5, 0.5, 0, nx, ny, nz, keepPositive, checkDist)) {
            renderNorthFace(renderer, block, x, y, z);
        }
        
        // South face (Z=1), center at (0.5, 0.5, 1)
        if (isPointOnKeepSide(0.5, 0.5, 1, nx, ny, nz, keepPositive, checkDist)) {
            renderSouthFace(renderer, block, x, y, z);
        }
        
        // West face (X=0), center at (0, 0.5, 0.5)
        if (isPointOnKeepSide(0, 0.5, 0.5, nx, ny, nz, keepPositive, checkDist)) {
            renderWestFace(renderer, block, x, y, z);
        }
        
        // East face (X=1), center at (1, 0.5, 0.5)
        if (isPointOnKeepSide(1, 0.5, 0.5, nx, ny, nz, keepPositive, checkDist)) {
            renderEastFace(renderer, block, x, y, z);
        }
    }
    
    /**
     * Check if a point is on the "keep" side of the plane.
     */
    private static boolean isPointOnKeepSide(double px, double py, double pz,
                                              float nx, float ny, float nz,
                                              boolean keepPositive, double epsilon) {
        float d = 0.5f * (nx + ny + nz);
        double dist = nx * px + ny * py + nz * pz - d;
        return keepPositive ? (dist > -epsilon) : (dist < epsilon);
    }
    
    /**
     * Render the cut face (polygon) with PADDED texture (clamp-to-edge).
     * For diagonal cut faces larger than 1x1, we use padding to maintain
     * texture quality - the texture stays at 1:1 scale in the center,
     * and edge pixels repeat outward.
     */
    private static void renderCutFace(int x, int y, int z, List<Vec3> points,
                                      float nx, float ny, float nz, boolean keepPositive,
                                      Block originalBlock, int meta) {
        
        if (points.size() < 3) return;
        
        // Get icon from original block
        IIcon icon = originalBlock.getIcon(0, meta);
        
        // Sort points to form a proper polygon
        Vec3 center = calculateCentroid(points);
        List<Vec3> sortedPoints = sortPointsByAngle(points, center, nx, ny, nz);
        
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
        
        // Determine if this is an axis-aligned or diagonal face
        double dx = maxX - minX;
        double dy = maxY - minY;
        double dz = maxZ - minZ;
        boolean isXFace = dx < 0.01;
        boolean isYFace = dy < 0.01;
        boolean isZFace = dz < 0.01;
        boolean isDiagonal = !isXFace && !isYFace && !isZFace;
        
        // Calculate face size in texture units (16 = 1 full texture)
        double faceWidth, faceHeight;
        if (isXFace) {
            faceWidth = dy * 16.0;
            faceHeight = dz * 16.0;
        } else if (isYFace) {
            faceWidth = dx * 16.0;
            faceHeight = dz * 16.0;
        } else if (isZFace) {
            faceWidth = dx * 16.0;
            faceHeight = dy * 16.0;
        } else {
            // Diagonal face
            faceWidth = Math.sqrt(dx*dx + dy*dy + dz*dz) * 16.0;
            faceHeight = 16.0;
        }
        
        // Calculate lighting
        int brightness = originalBlock.getMixedBrightnessForBlock(
            originalBlock.getWorld(), x, y, z
        );
        
        float brightnessFactor = Math.abs(nx) * 0.6f + Math.abs(ny) * 1.0f + Math.abs(nz) * 0.8f;
        brightnessFactor = Math.max(0.4f, Math.min(1.0f, brightnessFactor));
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(brightnessFactor, brightnessFactor, brightnessFactor);
        
        // Choose UV mapping based on face type:
        // - Axis-aligned: use CLIPPED (show portion of texture)
        // - Diagonal: use TILED CENTERED (tiling centered on face)
        if (isDiagonal && (faceWidth > 16.0 || faceHeight > 16.0)) {
            // Use centered tiling for large diagonal faces
            for (int i = 1; i < sortedPoints.size() - 1; i++) {
                addVertexWithTiledCenteredUV(x, y, z, sortedPoints.get(0), icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithTiledCenteredUV(x, y, z, sortedPoints.get(i), icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithTiledCenteredUV(x, y, z, sortedPoints.get(i + 1), icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
            }
        } else {
            // Use standard clipped mapping for axis-aligned faces
            for (int i = 1; i < sortedPoints.size() - 1; i++) {
                addVertexWithClippedUV(x, y, z, sortedPoints.get(0), icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithClippedUV(x, y, z, sortedPoints.get(i), icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithClippedUV(x, y, z, sortedPoints.get(i + 1), icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
            }
        }
    }
    
    private static Vec3 calculateCentroid(List<Vec3> points) {
        double cx = 0, cy = 0, cz = 0;
        for (Vec3 p : points) {
            cx += p.xCoord;
            cy += p.yCoord;
            cz += p.zCoord;
        }
        return Vec3.createVectorHelper(cx / points.size(), cy / points.size(), cz / points.size());
    }
    
    private static List<Vec3> sortPointsByAngle(List<Vec3> points, Vec3 center, 
                                                 float nx, float ny, float nz) {
        // Project points onto plane and sort by angle around center
        // Simplified: sort by position for now
        List<Vec3> sorted = new ArrayList<>(points);
        
        // Sort based on cross product with reference vector
        // This ensures points are in correct order for triangle fan
        sorted.sort((a, b) -> {
            double angleA = Math.atan2(a.yCoord - center.yCoord, a.xCoord - center.xCoord);
            double angleB = Math.atan2(b.yCoord - center.yCoord, b.xCoord - center.xCoord);
            return Double.compare(angleA, angleB);
        });
        
        return sorted;
    }
    
    private static void addVertexWithTiledUV(int x, int y, int z, Vec3 point, 
                                              IIcon icon, float nx, float ny, float nz,
                                              double faceWidth, double faceHeight,
                                              double minX, double minY, double minZ,
                                              double maxX, double maxY, double maxZ) {
        // Calculate normalized position within the face bounds
        double uNorm, vNorm;
        
        boolean isXFace = (maxX - minX) < 0.01;
        boolean isYFace = (maxY - minY) < 0.01;
        boolean isZFace = (maxZ - minZ) < 0.01;
        
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
            // Diagonal - project onto dominant plane
            if (Math.abs(nx) > Math.abs(ny) && Math.abs(nx) > Math.abs(nz)) {
                uNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
                vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
            } else if (Math.abs(ny) > Math.abs(nz)) {
                uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
                vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
            } else {
                uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
                vNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
            }
        }
        
        // Scale by face size to get texture coordinates
        // This tiles the texture instead of stretching it
        double uScaled = uNorm * (faceWidth / 16.0);
        double vScaled = vNorm * (faceHeight / 16.0);
        
        // Wrap coordinates for tiling (0-1 range)
        double uWrapped = uScaled - Math.floor(uScaled);
        double vWrapped = vScaled - Math.floor(vScaled);
        
        // Get actual texture coordinates
        double uMin = icon.getMinU();
        double uMax = icon.getMaxU();
        double vMin = icon.getMinV();
        double vMax = icon.getMaxV();
        
        double uCoord = uMin + (uMax - uMin) * uWrapped;
        double vCoord = vMin + (vMax - vMin) * vWrapped;
        
        tess.addVertexWithUV(
            x + point.xCoord, 
            y + point.yCoord, 
            z + point.zCoord,
            uCoord, vCoord
        );
    }
    
    /**
     * Adds vertex with TILED UV coordinates centered on the face.
     * Creates a tiling pattern that covers the face area, but only
     * renders the fragment corresponding to the actual polygon.
     * The tiling is centered on the face center.
     * 
     * Example: face is 22.6px wide (1.41 * 16), texture is 16px
     * - We need 2 tiles (32px) to cover the face
     * - Tiling is centered: face center aligns with texture center
     * - UVs wrap around for seamless tiling
     */
    private static void addVertexWithTiledCenteredUV(int x, int y, int z, Vec3 point,
                                                      IIcon icon, float nx, float ny, float nz,
                                                      double faceWidth, double faceHeight,
                                                      double minX, double minY, double minZ,
                                                      double maxX, double maxY, double maxZ) {
        
        double cx = (minX + maxX) / 2.0;
        double cy = (minY + maxY) / 2.0;
        double cz = (minZ + maxZ) / 2.0;
        
        // Determine dominant axis for projection
        boolean isXFace = (maxX - minX) < 0.01;
        boolean isYFace = (maxY - minY) < 0.01;
        boolean isZFace = (maxZ - minZ) < 0.01;
        
        // Calculate local coordinates relative to face center (-0.5 to 0.5 range)
        double uLocal, vLocal;
        if (isXFace) {
            uLocal = (point.yCoord - cy) / Math.max(maxY - minY, 0.001);
            vLocal = (point.zCoord - cz) / Math.max(maxZ - minZ, 0.001);
        } else if (isYFace) {
            uLocal = (point.xCoord - cx) / Math.max(maxX - minX, 0.001);
            vLocal = (point.zCoord - cz) / Math.max(maxZ - minZ, 0.001);
        } else if (isZFace) {
            uLocal = (point.xCoord - cx) / Math.max(maxX - minX, 0.001);
            vLocal = (point.yCoord - cy) / Math.max(maxY - minY, 0.001);
        } else {
            // Diagonal face - project based on dominant normal component
            if (Math.abs(nx) > Math.abs(ny) && Math.abs(nx) > Math.abs(nz)) {
                uLocal = (point.yCoord - cy) / Math.max(maxY - minY, 0.001);
                vLocal = (point.zCoord - cz) / Math.max(maxZ - minZ, 0.001);
            } else if (Math.abs(ny) > Math.abs(nz)) {
                uLocal = (point.xCoord - cx) / Math.max(maxX - minX, 0.001);
                vLocal = (point.zCoord - cz) / Math.max(maxZ - minZ, 0.001);
            } else {
                uLocal = (point.xCoord - cx) / Math.max(maxX - minX, 0.001);
                vLocal = (point.yCoord - cy) / Math.max(maxY - minY, 0.001);
            }
        }
        
        // Convert to texture pixel coordinates
        // Face center (0) maps to texture center (8px = 0.5 in UV)
        // Face extends by faceWidth/2 pixels on each side
        double uPixelOffset = uLocal * (faceWidth / 2.0);
        double vPixelOffset = vLocal * (faceHeight / 2.0);
        
        // Convert to UV coordinates within a single texture tile
        // Center is at 8px, so we add 8 and wrap around 16
        double uPixel = 8.0 + uPixelOffset;
        double vPixel = 8.0 + vPixelOffset;
        
        // Wrap to 0-16 range for seamless tiling
        double uWrapped = ((uPixel % 16.0) + 16.0) % 16.0;
        double vWrapped = ((vPixel % 16.0) + 16.0) % 16.0;
        
        // Convert to actual UV coordinates
        double uFinal = icon.getInterpolatedU(uWrapped);
        double vFinal = icon.getInterpolatedV(vWrapped);
        
        tess.addVertexWithUV(
            x + point.xCoord,
            y + point.yCoord,
            z + point.zCoord,
            uFinal, vFinal
        );
    }
    
    /**
     * Adds vertex with CLIPPED UV coordinates.
     * Shows only the portion of texture corresponding to the face size.
     */
    private static void addVertexWithClippedUV(int x, int y, int z, Vec3 point,
                                                IIcon icon, float nx, float ny, float nz,
                                                double minX, double minY, double minZ,
                                                double maxX, double maxY, double maxZ) {
        
        boolean isXFace = (maxX - minX) < 0.01;
        boolean isYFace = (maxY - minY) < 0.01;
        boolean isZFace = (maxZ - minZ) < 0.01;
        
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
            // Diagonal - use simple projection
            if (Math.abs(nx) > Math.abs(ny) && Math.abs(nx) > Math.abs(nz)) {
                uNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
                vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
            } else if (Math.abs(ny) > Math.abs(nz)) {
                uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
                vNorm = (point.zCoord - minZ) / Math.max(maxZ - minZ, 0.001);
            } else {
                uNorm = (point.xCoord - minX) / Math.max(maxX - minX, 0.001);
                vNorm = (point.yCoord - minY) / Math.max(maxY - minY, 0.001);
            }
        }
        
        double uMin = icon.getMinU();
        double uMax = icon.getMaxU();
        double vMin = icon.getMinV();
        double vMax = icon.getMaxV();
        
        double uCoord = uMin + (uMax - uMin) * uNorm;
        double vCoord = vMin + (vMax - vMin) * vNorm;
        
        tess.addVertexWithUV(
            x + point.xCoord,
            y + point.yCoord,
            z + point.zCoord,
            uCoord, vCoord
        );
    }
    
    // Legacy method for simple UV mapping (used by other parts of the code)
    private static void addVertexWithUV(int x, int y, int z, Vec3 point, 
                                        IIcon icon, float nx, float ny, float nz) {
        // Map 3D point to 2D UV coordinates
        double u, v;
        
        if (Math.abs(ny) > Math.abs(nx) && Math.abs(ny) > Math.abs(nz)) {
            u = point.xCoord;
            v = point.zCoord;
        } else if (Math.abs(nx) > Math.abs(nz)) {
            u = point.zCoord;
            v = point.yCoord;
        } else {
            u = point.xCoord;
            v = point.yCoord;
        }
        
        double uMin = icon.getMinU();
        double uMax = icon.getMaxU();
        double vMin = icon.getMinV();
        double vMax = icon.getMaxV();
        
        double uCoord = uMin + (uMax - uMin) * u;
        double vCoord = vMin + (vMax - vMin) * v;
        
        tess.addVertexWithUV(
            x + point.xCoord, 
            y + point.yCoord, 
            z + point.zCoord,
            uCoord, vCoord
        );
    }
    
    // Face rendering methods using original block's icons
    private static void renderBottomFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(0, 0);
        rb.renderFaceYNeg(block, x, y, z, icon);
    }
    
    private static void renderTopFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(1, 0);
        rb.renderFaceYPos(block, x, y, z, icon);
    }
    
    private static void renderNorthFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(2, 0);
        rb.renderFaceZNeg(block, x, y, z, icon);
    }
    
    private static void renderSouthFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(3, 0);
        rb.renderFaceZPos(block, x, y, z, icon);
    }
    
    private static void renderWestFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(4, 0);
        rb.renderFaceXNeg(block, x, y, z, icon);
    }
    
    private static void renderEastFace(RenderBlocks rb, Block block, int x, int y, int z) {
        IIcon icon = block.getIcon(5, 0);
        rb.renderFaceXPos(block, x, y, z, icon);
    }
}
