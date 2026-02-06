package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Advanced renderer for cuttable blocks supporting arbitrary plane cuts.
 * Renders a block cut by a plane passing through its center.
 */
public class AdvancedCutRenderer {
    
    private static final Tessellator tess = Tessellator.instance;
    private static final double EPSILON = 1e-5;
    private static final double EPS_MERGE = 1e-5;
    
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
        
        // Deduplicate intersection points (Step 3)
        intersections = deduplicatePoints(intersections, EPSILON);
        
        if (intersections.size() < 3) {
            // Not enough points to form a polygon, fallback to simple cut
            return false;
        }
        
        // Render clipped cube faces (NEW: replaces renderVisibleFaces)
        renderClippedCubeFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive);
        
        // Render the cut face (the polygon created by the plane)
        renderCutFace(x, y, z, intersections, nx, ny, nz, keepPositive, originalBlock, meta);
        
        return true;
    }
    
    // ====================================================================================
    // PLANE HELPERS
    // ====================================================================================
    
    /**
     * Calculate signed distance from point to plane.
     * Plane: nx*x + ny*y + nz*z = d, where d = 0.5*(nx+ny+nz)
     */
    private static double planeDist(double px, double py, double pz, float nx, float ny, float nz) {
        double d = 0.5 * (nx + ny + nz);
        return nx * px + ny * py + nz * pz - d;
    }
    
    /**
     * Check if point should be kept based on its signed distance.
     */
    private static boolean keepSide(double dist, boolean keepPositive, double eps) {
        return keepPositive ? (dist >= -eps) : (dist <= eps);
    }
    
    // ====================================================================================
    // POLYGON CLIPPING (Sutherland-Hodgman)
    // ====================================================================================
    
    /**
     * Clip polygon by plane using Sutherland-Hodgman algorithm.
     * Returns polygon containing only points on the "keep" side.
     */
    private static List<Vec3> clipPolygonByPlane(List<Vec3> poly, float nx, float ny, float nz, 
                                                  boolean keepPositive) {
        if (poly.size() < 3) return poly;
        
        List<Vec3> output = new ArrayList<>();
        int n = poly.size();
        
        for (int i = 0; i < n; i++) {
            Vec3 A = poly.get(i);
            Vec3 B = poly.get((i + 1) % n);
            
            double dA = planeDist(A.xCoord, A.yCoord, A.zCoord, nx, ny, nz);
            double dB = planeDist(B.xCoord, B.yCoord, B.zCoord, nx, ny, nz);
            
            boolean inA = keepSide(dA, keepPositive, EPSILON);
            boolean inB = keepSide(dB, keepPositive, EPSILON);
            
            if (inA && inB) {
                // Both inside: keep B
                output.add(B);
            } else if (inA && !inB) {
                // A inside, B outside: keep intersection
                Vec3 intersect = intersectEdgeWithPlane(A, B, dA, dB);
                if (intersect != null) output.add(intersect);
            } else if (!inA && inB) {
                // A outside, B inside: keep intersection and B
                Vec3 intersect = intersectEdgeWithPlane(A, B, dA, dB);
                if (intersect != null) output.add(intersect);
                output.add(B);
            }
            // Both outside: keep nothing
        }
        
        return output;
    }
    
    /**
     * Find intersection of edge AB with plane.
     * dA, dB are signed distances of A and B from plane.
     */
    private static Vec3 intersectEdgeWithPlane(Vec3 A, Vec3 B, double dA, double dB) {
        double denom = dA - dB;
        if (Math.abs(denom) < 1e-10) return null; // Parallel
        
        double t = dA / denom;
        if (t < 0 || t > 1) return null; // Outside segment
        
        double ix = A.xCoord + t * (B.xCoord - A.xCoord);
        double iy = A.yCoord + t * (B.yCoord - A.yCoord);
        double iz = A.zCoord + t * (B.zCoord - A.zCoord);
        
        return Vec3.createVectorHelper(ix, iy, iz);
    }
    
    // ====================================================================================
    // FACE DEFINITIONS (6 cube faces in CCW order)
    // ====================================================================================
    
    /**
     * Get the 4 vertices of a cube face in CCW order (looking from outside).
     * Side indices: 0=Bottom, 1=Top, 2=North, 3=South, 4=West, 5=East
     */
    private static List<Vec3> getFacePolygon(int side) {
        List<Vec3> poly = new ArrayList<>(4);
        switch (side) {
            case 0: // BOTTOM (y=0)
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                break;
            case 1: // TOP (y=1)
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                break;
            case 2: // NORTH (z=0)
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                break;
            case 3: // SOUTH (z=1)
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                break;
            case 4: // WEST (x=0)
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                break;
            case 5: // EAST (x=1)
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                break;
        }
        return poly;
    }
    
    /**
     * Get expected normal for a cube face (for winding correction).
     */
    private static Vec3 getFaceNormal(int side) {
        switch (side) {
            case 0: return Vec3.createVectorHelper(0, -1, 0); // Bottom
            case 1: return Vec3.createVectorHelper(0, 1, 0);  // Top
            case 2: return Vec3.createVectorHelper(0, 0, -1); // North
            case 3: return Vec3.createVectorHelper(0, 0, 1);  // South
            case 4: return Vec3.createVectorHelper(-1, 0, 0); // West
            case 5: return Vec3.createVectorHelper(1, 0, 0);  // East
        }
        return Vec3.createVectorHelper(0, 1, 0);
    }
    
    // ====================================================================================
    // UV MAPPING
    // ====================================================================================
    
    /**
     * Calculate UV coordinates for a point on a given face.
     * Returns u,v in [0,1] range.
     */
    private static double[] getUVForPoint(Vec3 p, int side) {
        double u, v;
        switch (side) {
            case 0: // BOTTOM (y=0): u=x, v=z
                u = p.xCoord;
                v = p.zCoord;
                break;
            case 1: // TOP (y=1): u=x, v=z
                u = p.xCoord;
                v = p.zCoord;
                break;
            case 2: // NORTH (z=0): u=x, v=1-y
                u = p.xCoord;
                v = 1.0 - p.yCoord;
                break;
            case 3: // SOUTH (z=1): u=x, v=1-y
                u = p.xCoord;
                v = 1.0 - p.yCoord;
                break;
            case 4: // WEST (x=0): u=z, v=1-y
                u = p.zCoord;
                v = 1.0 - p.yCoord;
                break;
 case 5: // EAST (x=1): u=z, v=1-y
                u = p.zCoord;
                v = 1.0 - p.yCoord;
                break;
            default:
                u = p.xCoord;
                v = p.yCoord;
        }
        return new double[] { u, v };
    }
    
    // ====================================================================================
    // RENDERING CLIPPED FACES
    // ====================================================================================
    
    /**
     * Render all 6 cube faces with clipping.
     * Replaces the old renderVisibleFaces which used binary on/off decision.
     */
    private static void renderClippedCubeFaces(RenderBlocks renderer, Block originalBlock,
                                               int x, int y, int z, int meta,
                                               float nx, float ny, float nz, 
                                               boolean keepPositive) {
        
        // Get brightness and color
        int brightness = originalBlock.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
        float colorR = 1.0f;
        float colorG = 1.0f;
        float colorB = 1.0f;
        
        // Process each of 6 faces
        for (int side = 0; side < 6; side++) {
            // Get base polygon for this face
            List<Vec3> facePoly = getFacePolygon(side);
            
            // Clip against the cutting plane
            List<Vec3> clipped = clipPolygonByPlane(facePoly, nx, ny, nz, keepPositive);
            
            // Deduplicate points after clipping
            clipped = deduplicatePoints(clipped, EPS_MERGE);
            
            // Remove closing point if same as first
            if (clipped.size() > 1) {
                Vec3 first = clipped.get(0);
                Vec3 last = clipped.get(clipped.size() - 1);
                double dx = first.xCoord - last.xCoord;
                double dy = first.yCoord - last.yCoord;
                double dz = first.zCoord - last.zCoord;
                if (dx*dx + dy*dy + dz*dz < EPS_MERGE*EPS_MERGE) {
                    clipped.remove(clipped.size() - 1);
                }
            }
            
            // Skip if less than 3 vertices (no polygon to render)
            if (clipped.size() < 3) continue;
            
            // Ensure correct winding (CCW when looking from outside)
            Vec3 expectedNormal = getFaceNormal(side);
            clipped = ensureFaceWinding(clipped, expectedNormal);
            
            // Get icon for this side
            IIcon icon = originalBlock.getIcon(side, meta);
            
            // Render the clipped polygon
            renderClippedPolygon(clipped, side, icon, x, y, z, brightness, colorR, colorG, colorB);
        }
    }
    
    /**
     * Ensure polygon has correct winding order (CCW when looking from outside).
     */
    private static List<Vec3> ensureFaceWinding(List<Vec3> poly, Vec3 expectedNormal) {
        if (poly.size() < 3) return poly;
        
        // Calculate actual normal of first triangle
        Vec3 p0 = poly.get(0);
        Vec3 p1 = poly.get(1);
        Vec3 p2 = poly.get(2);
        
        Vec3 v1 = Vec3.createVectorHelper(p1.xCoord - p0.xCoord, p1.yCoord - p0.yCoord, p1.zCoord - p0.zCoord);
        Vec3 v2 = Vec3.createVectorHelper(p2.xCoord - p0.xCoord, p2.yCoord - p0.yCoord, p2.zCoord - p0.zCoord);
        
        Vec3 actualNormal = crossProduct(v1, v2);
        actualNormal = normalize(actualNormal);
        
        // Check if normals point in same direction
        double dot = actualNormal.xCoord * expectedNormal.xCoord + 
                     actualNormal.yCoord * expectedNormal.yCoord + 
                     actualNormal.zCoord * expectedNormal.zCoord;
        
        // If dot < 0, normals point in opposite directions - reverse winding
        if (dot < 0) {
            Collections.reverse(poly);
        }
        
        return poly;
    }
    
    /**
     * Render clipped polygon as degenerate quads (triangle fan).
     */
    private static void renderClippedPolygon(List<Vec3> poly, int side, IIcon icon,
                                              int x, int y, int z, int brightness,
                                              float r, float g, float b) {
        if (poly.size() < 3) return;
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(r, g, b);
        
        // Triangle fan from first vertex
        Vec3 pA = poly.get(0);
        double[] uvA = getUVForPoint(pA, side);
        
        for (int i = 1; i < poly.size() - 1; i++) {
            Vec3 pB = poly.get(i);
            Vec3 pC = poly.get(i + 1);
            
            double[] uvB = getUVForPoint(pB, side);
            double[] uvC = getUVForPoint(pC, side);
            
            // Degenerate quad: A, B, C, C
            addVertexWithUV(x + pA.xCoord, y + pA.yCoord, z + pA.zCoord, 
                           icon.getInterpolatedU(uvA[0] * 16.0), 
                           icon.getInterpolatedV(uvA[1] * 16.0));
            addVertexWithUV(x + pB.xCoord, y + pB.yCoord, z + pB.zCoord,
                           icon.getInterpolatedU(uvB[0] * 16.0),
                           icon.getInterpolatedV(uvB[1] * 16.0));
            addVertexWithUV(x + pC.xCoord, y + pC.yCoord, z + pC.zCoord,
                           icon.getInterpolatedU(uvC[0] * 16.0),
                           icon.getInterpolatedV(uvC[1] * 16.0));
            addVertexWithUV(x + pC.xCoord, y + pC.yCoord, z + pC.zCoord,
                           icon.getInterpolatedU(uvC[0] * 16.0),
                           icon.getInterpolatedV(uvC[1] * 16.0)); // Duplicate C for quad
        }
    }
    
    private static void addVertexWithUV(double x, double y, double z, double u, double v) {
        tess.addVertexWithUV(x, y, z, u, v);
    }
    
    // ====================================================================================
    // LEGACY METHODS (kept for reference but not used in renderAdvancedCut)
    // ====================================================================================
    
    /**
     * OLD METHOD - kept for reference but replaced by renderClippedCubeFaces.
     * Renders cube faces based on center point test (causes threshold behavior).
     */
    @Deprecated
    private static void renderVisibleFaces(RenderBlocks renderer, Block block,
                                           int x, int y, int z, int meta,
                                           float nx, float ny, float nz, 
                                           boolean keepPositive) {
        // Not used - replaced by renderClippedCubeFaces
    }
    
    // ====================================================================================
    // CUT FACE RENDERING (the diagonal face created by the cutting plane)
    // ====================================================================================
    
    /**
     * Render the cut face (polygon) with PADDED texture (clamp-to-edge).
     */
    private static void renderCutFace(int x, int y, int z, List<Vec3> points,
                                      float nx, float ny, float nz, boolean keepPositive,
                                      Block originalBlock, int meta) {
        
        if (points.size() < 3) return;
        
        // Get icon from original block
        IIcon icon = originalBlock.getIcon(0, meta);
        
        // Sort points to form a proper polygon using tangent/bitangent basis
        Vec3 center = calculateCentroid(points);
        List<Vec3> sortedPoints = sortPointsByAngle(points, center, nx, ny, nz);
        
        // Ensure correct winding order for visibility
        sortedPoints = ensureCorrectWinding(sortedPoints, nx, ny, nz, keepPositive);
        
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
        
        // Calculate lighting (use default brightness)
        int brightness = 15 << 20 | 15 << 4;
        
        float brightnessFactor = Math.abs(nx) * 0.6f + Math.abs(ny) * 1.0f + Math.abs(nz) * 0.8f;
        brightnessFactor = Math.max(0.4f, Math.min(1.0f, brightnessFactor));
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(brightnessFactor, brightnessFactor, brightnessFactor);
        
        // Choose UV mapping based on face type
        if (isDiagonal && (faceWidth > 16.0 || faceHeight > 16.0)) {
            // Use centered tiling for large diagonal faces
            for (int i = 1; i < sortedPoints.size() - 1; i++) {
                Vec3 a = sortedPoints.get(0);
                Vec3 b = sortedPoints.get(i);
                Vec3 c = sortedPoints.get(i + 1);
                
                addVertexWithTiledCenteredUV(x, y, z, a, icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithTiledCenteredUV(x, y, z, b, icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithTiledCenteredUV(x, y, z, c, icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithTiledCenteredUV(x, y, z, c, icon, nx, ny, nz,
                                      faceWidth, faceHeight, minX, minY, minZ, maxX, maxY, maxZ);
            }
        } else {
            // Use standard clipped mapping for axis-aligned faces
            for (int i = 1; i < sortedPoints.size() - 1; i++) {
                Vec3 a = sortedPoints.get(0);
                Vec3 b = sortedPoints.get(i);
                Vec3 c = sortedPoints.get(i + 1);
                
                addVertexWithClippedUV(x, y, z, a, icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithClippedUV(x, y, z, b, icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithClippedUV(x, y, z, c, icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
                addVertexWithClippedUV(x, y, z, c, icon, nx, ny, nz,
                                       minX, minY, minZ, maxX, maxY, maxZ);
            }
        }
    }
    
    // ====================================================================================
    // UTILITY METHODS
    // ====================================================================================
    
    /**
     * Deduplicate points that are within epsilon distance of each other.
     */
    private static List<Vec3> deduplicatePoints(List<Vec3> points, double eps) {
        List<Vec3> unique = new ArrayList<>();
        double epsSq = eps * eps;
        
        for (Vec3 p : points) {
            boolean isDuplicate = false;
            for (Vec3 u : unique) {
                double dx = p.xCoord - u.xCoord;
                double dy = p.yCoord - u.yCoord;
                double dz = p.zCoord - u.zCoord;
                double distSq = dx * dx + dy * dy + dz * dz;
                if (distSq < epsSq) {
                    isDuplicate = true;
                    break;
                }
            }
            if (!isDuplicate) {
                unique.add(p);
            }
        }
        return unique;
    }
    
    /**
     * Calculate intersection points of the plane with cube edges.
     */
    private static List<Vec3> calculateIntersections(float nx, float ny, float nz) {
        List<Vec3> points = new ArrayList<>();
        float d = 0.5f * (nx + ny + nz);
        
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
        if (Math.abs(nx) < 0.0001f) return;
        
        float t = (d - ny * y - nz * z) / nx;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(t, y, z));
        }
    }
    
    private static void checkEdgeY(List<Vec3> points, float nx, float ny, float nz,
                                    float d, int x, int z) {
        if (Math.abs(ny) < 0.0001f) return;
        
        float t = (d - nx * x - nz * z) / ny;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(x, t, z));
        }
    }
    
    private static void checkEdgeZ(List<Vec3> points, float nx, float ny, float nz,
                                    float d, int x, int y) {
        if (Math.abs(nz) < 0.0001f) return;
        
        float t = (d - nx * x - ny * y) / nz;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(Vec3.createVectorHelper(x, y, t));
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
     * Sort points by angle around the center on the plane surface.
     */
    private static List<Vec3> sortPointsByAngle(List<Vec3> points, Vec3 center, 
                                                 float nx, float ny, float nz) {
        Vec3 n = Vec3.createVectorHelper(nx, ny, nz);
        
        // Choose helper vector not parallel to normal
        Vec3 helper;
        if (Math.abs(ny) < 0.99) {
            helper = Vec3.createVectorHelper(0, 1, 0);
        } else {
            helper = Vec3.createVectorHelper(1, 0, 0);
        }
        
        // Calculate tangent and bitangent
        Vec3 tangent = crossProduct(helper, n);
        tangent = normalize(tangent);
        
        Vec3 bitangent = crossProduct(n, tangent);
        bitangent = normalize(bitangent);
        
        // Sort points by angle using the tangent/bitangent basis
        List<Vec3> sorted = new ArrayList<>(points);
        final Vec3 t = tangent;
        final Vec3 bit = bitangent;
        
        sorted.sort((p1, p2) -> {
            // Project onto tangent/bitangent plane
            double v1X = p1.xCoord - center.xCoord;
            double v1Y = p1.yCoord - center.yCoord;
            double v1Z = p1.zCoord - center.zCoord;
            
            double v2X = p2.xCoord - center.xCoord;
            double v2Y = p2.yCoord - center.yCoord;
            double v2Z = p2.zCoord - center.zCoord;
            
            double u1 = v1X * t.xCoord + v1Y * t.yCoord + v1Z * t.zCoord;
            double w1 = v1X * bit.xCoord + v1Y * bit.yCoord + v1Z * bit.zCoord;
            
            double u2 = v2X * t.xCoord + v2Y * t.yCoord + v2Z * t.zCoord;
            double w2 = v2X * bit.xCoord + v2Y * bit.yCoord + v2Z * bit.zCoord;
            
            double angle1 = Math.atan2(w1, u1);
            double angle2 = Math.atan2(w2, u2);
            
            return Double.compare(angle1, angle2);
        });
        
        return sorted;
    }
    
    /**
     * Ensure correct winding order so that the polygon normal points outward.
     */
    private static List<Vec3> ensureCorrectWinding(List<Vec3> points, float nx, float ny, float nz, boolean keepPositive) {
        if (points.size() < 3) return points;
        
        // Calculate polygon normal using first three points
        Vec3 p0 = points.get(0);
        Vec3 p1 = points.get(1);
        Vec3 p2 = points.get(2);
        
        Vec3 v1 = Vec3.createVectorHelper(p1.xCoord - p0.xCoord, p1.yCoord - p0.yCoord, p1.zCoord - p0.zCoord);
        Vec3 v2 = Vec3.createVectorHelper(p2.xCoord - p0.xCoord, p2.yCoord - p0.yCoord, p2.zCoord - p0.zCoord);
        
        Vec3 polyNormal = crossProduct(v1, v2);
        polyNormal = normalize(polyNormal);
        
        // Check if polygon normal aligns with plane normal
        double dot = polyNormal.xCoord * nx + polyNormal.yCoord * ny + polyNormal.zCoord * nz;
        
        // The cut face should face outward from the kept portion
        boolean shouldReverse;
        if (keepPositive) {
            // Cut face should point toward negative side
            shouldReverse = dot > 0;
        } else {
            // Cut face should point toward positive side
            shouldReverse = dot < 0;
        }
        
        if (shouldReverse) {
            Collections.reverse(points);
        }
        
        return points;
    }
    
    // ====================================================================================
    // VECTOR MATH HELPERS
    // ====================================================================================
    
    private static Vec3 crossProduct(Vec3 a, Vec3 b) {
        return Vec3.createVectorHelper(
            a.yCoord * b.zCoord - a.zCoord * b.yCoord,
            a.zCoord * b.xCoord - a.xCoord * b.zCoord,
            a.xCoord * b.yCoord - a.yCoord * b.xCoord
        );
    }
    
    private static Vec3 normalize(Vec3 v) {
        double len = Math.sqrt(v.xCoord * v.xCoord + v.yCoord * v.yCoord + v.zCoord * v.zCoord);
        if (len < 1e-10) {
            return Vec3.createVectorHelper(0, 0, 0);
        }
        return Vec3.createVectorHelper(v.xCoord / len, v.yCoord / len, v.zCoord / len);
    }
    
    // ====================================================================================
    // UV MAPPING FOR CUT FACE
    // ====================================================================================
    
    private static void addVertexWithTiledCenteredUV(int x, int y, int z, Vec3 point,
                                                      IIcon icon, float nx, float ny, float nz,
                                                      double faceWidth, double faceHeight,
                                                      double minX, double minY, double minZ,
                                                      double maxX, double maxY, double maxZ) {
        
        double cx = (minX + maxX) / 2.0;
        double cy = (minY + maxY) / 2.0;
        double cz = (minZ + maxZ) / 2.0;
        
        boolean isXFace = (maxX - minX) < 0.01;
        boolean isYFace = (maxY - minY) < 0.01;
        boolean isZFace = (maxZ - minZ) < 0.01;
        
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
        
        double uPixelOffset = uLocal * (faceWidth / 2.0);
        double vPixelOffset = vLocal * (faceHeight / 2.0);
        
        double uPixel = 8.0 + uPixelOffset;
        double vPixel = 8.0 + vPixelOffset;
        
        double uWrapped = ((uPixel % 16.0) + 16.0) % 16.0;
        double vWrapped = ((vPixel % 16.0) + 16.0) % 16.0;
        
        double uFinal = icon.getInterpolatedU(uWrapped);
        double vFinal = icon.getInterpolatedV(vWrapped);
        
        tess.addVertexWithUV(
            x + point.xCoord,
            y + point.yCoord,
            z + point.zCoord,
            uFinal, vFinal
        );
    }
    
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
}
