package com.cuttableblocks.client.render;

import com.cuttableblocks.tileentities.TileEntityCuttable;
import com.cuttableblocks.util.CutDirections;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.util.Vec3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Advanced renderer for cuttable blocks with discrete 18 directions.
 * Fixed: consistent keepPositive (Definition A), stable UV, anti z-fighting, EPS comparisons.
 */
public class AdvancedCutRenderer {
    
    private static final Tessellator tess = Tessellator.instance;
    private static final double EPSILON = 1e-6;
    private static final double EPS_MERGE = 1e-6;
    private static final double Z_FIGHT_OFFSET = 1e-4;
    private static final Vec3 CENTER = Vec3.createVectorHelper(0.5, 0.5, 0.5);
    
    /**
     * Main entry point for rendering.
     */
    public static boolean renderAdvancedCut(RenderBlocks renderer, Block block, 
                                            int x, int y, int z, TileEntityCuttable te) {
        
        Block originalBlock = te.getOriginalBlock();
        if (originalBlock == null) {
            return false;
        }
        
        int rotId = te.getRotId();
        int dirId = te.getDirId();
        boolean keepPositive = te.keepPositiveSide();
        int meta = te.getOriginalMetadata();
        
        // Get world-space normal (deterministically from rotId/dirId)
        Vec3 nWorld = CutDirections.getWorldDir(rotId, dirId);
        float nx = (float) nWorld.xCoord;
        float ny = (float) nWorld.yCoord;
        float nz = (float) nWorld.zCoord;
        
        // Calculate planeD through center (plane always passes through block center)
        double planeD = 0.5 * (nx + ny + nz);
        
        // Deterministic render mode selection based on reconstructed normal
        // Check if exactly axis-aligned (one component == 1.0, others == 0)
        double absNx = Math.abs(nx);
        double absNy = Math.abs(ny);
        double absNz = Math.abs(nz);
        
        boolean isAxisX = absNx > 0.999999 && absNy < 0.000001 && absNz < 0.000001;
        boolean isAxisY = absNy > 0.999999 && absNx < 0.000001 && absNz < 0.000001;
        boolean isAxisZ = absNz > 0.999999 && absNx < 0.000001 && absNy < 0.000001;
        
        if (isAxisY) {
            // Definition A: keepPositive means keep dist >= 0 side
            // For horizontal cut: ny > 0 means normal points up
            // keepPositive=true -> keep upper half (dist >= 0)
            // keepPositive=false -> keep lower half (dist < 0)
            boolean keepTop = (ny > 0) == keepPositive;
            RenderHelper.renderHorizontalCut(renderer, originalBlock, x, y, z, meta, keepTop);
            return true;
        } else if (isAxisX) {
            boolean keepEast = (nx > 0) == keepPositive;
            RenderHelper.renderVerticalXCut(renderer, originalBlock, x, y, z, meta, keepEast);
            return true;
        } else if (isAxisZ) {
            boolean keepSouth = (nz > 0) == keepPositive;
            RenderHelper.renderVerticalZCut(renderer, originalBlock, x, y, z, meta, keepSouth);
            return true;
        } else {
            return renderDiagonalCut(renderer, originalBlock, x, y, z, meta, 
                                    nx, ny, nz, keepPositive, planeD);
        }
    }
    
    private static boolean renderDiagonalCut(RenderBlocks renderer, Block originalBlock,
                                              int x, int y, int z, int meta,
                                              float nx, float ny, float nz, 
                                              boolean keepPositive, double planeD) {
        
        List<Vec3> intersections = calculateIntersections(nx, ny, nz, planeD);
        intersections = deduplicatePoints(intersections, EPS_MERGE);
        
        if (intersections.size() < 3) {
            return false;
        }
        
        renderClippedCubeFaces(renderer, originalBlock, x, y, z, meta, nx, ny, nz, keepPositive, planeD);
        renderCutFace(x, y, z, intersections, nx, ny, nz, keepPositive, originalBlock, meta);
        
        return true;
    }
    
    private static double planeDist(double px, double py, double pz, float nx, float ny, float nz, double planeD) {
        return nx * px + ny * py + nz * pz - planeD;
    }
    
    private static boolean keepSide(double dist, boolean keepPositive, double eps) {
        // Definition A: keepPositive means keep dist >= 0 side
        // Use EPS to avoid points exactly on plane falling through cracks
        return keepPositive ? (dist >= -eps) : (dist <= eps);
    }
    
    private static double wrap16(double px) {
        double w = px % 16.0;
        if (w < 0) w += 16.0;
        return w;
    }
    
    private static List<Vec3> clipPolygonByPlane(List<Vec3> poly, float nx, float ny, float nz, 
                                                  boolean keepPositive, double planeD) {
        if (poly.size() < 3) return poly;
        
        List<Vec3> output = new ArrayList<>();
        int n = poly.size();
        
        for (int i = 0; i < n; i++) {
            Vec3 A = poly.get(i);
            Vec3 B = poly.get((i + 1) % n);
            
            double dA = planeDist(A.xCoord, A.yCoord, A.zCoord, nx, ny, nz, planeD);
            double dB = planeDist(B.xCoord, B.yCoord, B.zCoord, nx, ny, nz, planeD);
            
            // Use EPS for stable comparisons
            boolean inA = keepSide(dA, keepPositive, EPSILON);
            boolean inB = keepSide(dB, keepPositive, EPSILON);
            
            if (inA && inB) {
                output.add(B);
            } else if (inA && !inB) {
                Vec3 intersect = intersectEdgeWithPlane(A, B, dA, dB);
                if (intersect != null) output.add(intersect);
            } else if (!inA && inB) {
                Vec3 intersect = intersectEdgeWithPlane(A, B, dA, dB);
                if (intersect != null) output.add(intersect);
                output.add(B);
            }
        }
        
        return output;
    }
    
    private static Vec3 intersectEdgeWithPlane(Vec3 A, Vec3 B, double dA, double dB) {
        double denom = dA - dB;
        if (Math.abs(denom) < EPSILON) return null;
        
        double t = dA / denom;
        if (t < 0 || t > 1) return null;
        
        double ix = A.xCoord + t * (B.xCoord - A.xCoord);
        double iy = A.yCoord + t * (B.yCoord - A.yCoord);
        double iz = A.zCoord + t * (B.zCoord - A.zCoord);
        
        return Vec3.createVectorHelper(ix, iy, iz);
    }
    
    private static List<Vec3> getFacePolygon(int side) {
        List<Vec3> poly = new ArrayList<>(4);
        switch (side) {
            case 0: // BOTTOM
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                break;
            case 1: // TOP
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                break;
            case 2: // NORTH
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                break;
            case 3: // SOUTH
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                break;
            case 4: // WEST
                poly.add(Vec3.createVectorHelper(0, 0, 0));
                poly.add(Vec3.createVectorHelper(0, 0, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 1));
                poly.add(Vec3.createVectorHelper(0, 1, 0));
                break;
            case 5: // EAST
                poly.add(Vec3.createVectorHelper(1, 0, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 0));
                poly.add(Vec3.createVectorHelper(1, 1, 1));
                poly.add(Vec3.createVectorHelper(1, 0, 1));
                break;
        }
        return poly;
    }
    
    private static Vec3 getFaceNormal(int side) {
        switch (side) {
            case 0: return Vec3.createVectorHelper(0, -1, 0);
            case 1: return Vec3.createVectorHelper(0, 1, 0);
            case 2: return Vec3.createVectorHelper(0, 0, -1);
            case 3: return Vec3.createVectorHelper(0, 0, 1);
            case 4: return Vec3.createVectorHelper(-1, 0, 0);
            case 5: return Vec3.createVectorHelper(1, 0, 0);
        }
        return Vec3.createVectorHelper(0, 1, 0);
    }
    
    /**
     * Get UV for a point on a face using WORLD-SPACE coordinates.
     * This ensures consistent texture scale regardless of clipping.
     */
    private static double[] getUVForPoint(Vec3 p, int side) {
        double u, v;
        switch (side) {
            case 0: case 1: // BOTTOM/TOP
                u = p.xCoord;
                v = p.zCoord;
                break;
            case 2: case 3: // NORTH/SOUTH
                u = p.xCoord;
                v = p.yCoord;  // Use world Y directly (0-1 range)
                break;
            case 4: case 5: // WEST/EAST
                u = p.zCoord;
                v = p.yCoord;  // Use world Y directly
                break;
            default:
                u = p.xCoord;
                v = p.yCoord;
        }
        return new double[] { u, v };
    }
    
    private static void renderClippedCubeFaces(RenderBlocks renderer, Block originalBlock,
                                               int x, int y, int z, int meta,
                                               float nx, float ny, float nz, 
                                               boolean keepPositive, double planeD) {
        
        for (int side = 0; side < 6; side++) {
            List<Vec3> facePoly = getFacePolygon(side);
            List<Vec3> clipped = clipPolygonByPlane(facePoly, nx, ny, nz, keepPositive, planeD);
            clipped = deduplicatePoints(clipped, EPS_MERGE);
            
            if (clipped.size() > 1) {
                Vec3 first = clipped.get(0);
                Vec3 last = clipped.get(clipped.size() - 1);
                if (distanceSq(first, last) < EPS_MERGE*EPS_MERGE) {
                    clipped.remove(clipped.size() - 1);
                }
            }
            
            if (clipped.size() < 3) continue;
            
            Vec3 expectedNormal = getFaceNormal(side);
            clipped = ensureFaceWinding(clipped, expectedNormal);
            
            IIcon icon = originalBlock.getIcon(side, meta);
            int brightness = originalBlock.getMixedBrightnessForBlock(renderer.blockAccess, x, y, z);
            
            renderClippedPolygon(clipped, side, icon, x, y, z, brightness);
        }
    }
    
    private static double distanceSq(Vec3 a, Vec3 b) {
        double dx = a.xCoord - b.xCoord;
        double dy = a.yCoord - b.yCoord;
        double dz = a.zCoord - b.zCoord;
        return dx*dx + dy*dy + dz*dz;
    }
    
    private static List<Vec3> ensureFaceWinding(List<Vec3> poly, Vec3 expectedNormal) {
        if (poly.size() < 3) return poly;
        
        Vec3 p0 = poly.get(0);
        Vec3 p1 = poly.get(1);
        Vec3 p2 = poly.get(2);
        
        Vec3 v1 = Vec3.createVectorHelper(p1.xCoord - p0.xCoord, p1.yCoord - p0.yCoord, p1.zCoord - p0.zCoord);
        Vec3 v2 = Vec3.createVectorHelper(p2.xCoord - p0.xCoord, p2.yCoord - p0.yCoord, p2.zCoord - p0.zCoord);
        
        Vec3 actualNormal = crossProduct(v1, v2);
        actualNormal = normalize(actualNormal);
        
        double dot = actualNormal.xCoord * expectedNormal.xCoord + 
                     actualNormal.yCoord * expectedNormal.yCoord + 
                     actualNormal.zCoord * expectedNormal.zCoord;
        
        if (dot < 0) {
            Collections.reverse(poly);
        }
        
        return poly;
    }
    
    /**
     * Render clipped polygon using GL_TRIANGLES (proper triangles, not fake quads).
     */
    private static void renderClippedPolygon(List<Vec3> poly, int side, IIcon icon,
                                              int x, int y, int z, int brightness) {
        if (poly.size() < 3) return;
        
        tess.setBrightness(brightness);
        tess.setColorOpaque_F(1.0f, 1.0f, 1.0f);
        
        Vec3 pA = poly.get(0);
        double[] uvA = getUVForPoint(pA, side);
        
        // Convert to texture coordinates (0-16 range)
        double uA = icon.getInterpolatedU(uvA[0] * 16.0);
        double vA = icon.getInterpolatedV(uvA[1] * 16.0);
        
        for (int i = 1; i < poly.size() - 1; i++) {
            Vec3 pB = poly.get(i);
            Vec3 pC = poly.get(i + 1);
            
            double[] uvB = getUVForPoint(pB, side);
            double[] uvC = getUVForPoint(pC, side);
            
            double uB = icon.getInterpolatedU(uvB[0] * 16.0);
            double vB = icon.getInterpolatedV(uvB[1] * 16.0);
            double uC = icon.getInterpolatedU(uvC[0] * 16.0);
            double vC = icon.getInterpolatedV(uvC[1] * 16.0);
            
            // Render as proper triangle fan (GL_TRIANGLES in 1.7.10 is default)
            // First triangle
            tess.addVertexWithUV(x + pA.xCoord, y + pA.yCoord, z + pA.zCoord, uA, vA);
            tess.addVertexWithUV(x + pB.xCoord, y + pB.yCoord, z + pB.zCoord, uB, vB);
            tess.addVertexWithUV(x + pC.xCoord, y + pC.yCoord, z + pC.zCoord, uC, vC);
        }
    }
    
    /**
     * Render cut face with STABLE UV (origin at block center, world-space basis).
     * UV scale is constant regardless of cut plane orientation.
     */
    private static void renderCutFace(int x, int y, int z, List<Vec3> points,
                                      float nx, float ny, float nz, boolean keepPositive,
                                      Block originalBlock, int meta) {
        
        if (points.size() < 3) return;
        
        // Use icon from top face for cut face texture
        IIcon icon = originalBlock.getIcon(1, meta);
        
        Vec3 center = calculateCentroid(points);
        List<Vec3> sortedPoints = sortPointsByAngle(points, center, nx, ny, nz);
        sortedPoints = ensureCorrectWinding(sortedPoints, nx, ny, nz, keepPositive);
        
        // Build world-space tangent/bitangent basis on the cut plane
        Vec3 n = normalize(Vec3.createVectorHelper(nx, ny, nz));
        
        // Choose helper vector - prefer world Y if possible, else world X
        Vec3 helper;
        if (Math.abs(n.yCoord) < 0.9) {
            helper = Vec3.createVectorHelper(0, 1, 0);
        } else {
            helper = Vec3.createVectorHelper(1, 0, 0);
        }
        
        Vec3 tangent = normalize(crossProduct(helper, n));
        Vec3 bitangent = crossProduct(n, tangent);
        bitangent = normalize(bitangent);
        
        // UV origin is always block center (for stable, repeatable patterns)
        Vec3 origin = CENTER;
        
        // Get brightness
        int brightness = 15 << 20 | 15 << 4;
        tess.setBrightness(brightness);
        float brightnessFactor = Math.abs(nx) * 0.6f + Math.abs(ny) * 1.0f + Math.abs(nz) * 0.8f;
        brightnessFactor = Math.max(0.4f, Math.min(1.0f, brightnessFactor));
        tess.setColorOpaque_F(brightnessFactor, brightnessFactor, brightnessFactor);
        
        // Anti z-fighting offset
        Vec3 offset = Vec3.createVectorHelper(n.xCoord * Z_FIGHT_OFFSET, 
                                               n.yCoord * Z_FIGHT_OFFSET, 
                                               n.zCoord * Z_FIGHT_OFFSET);
        
        Vec3 pA = sortedPoints.get(0);
        double[] uvA = getCutFaceUV(pA, origin, tangent, bitangent, icon);
        
        for (int i = 1; i < sortedPoints.size() - 1; i++) {
            Vec3 pB = sortedPoints.get(i);
            Vec3 pC = sortedPoints.get(i + 1);
            
            double[] uvB = getCutFaceUV(pB, origin, tangent, bitangent, icon);
            double[] uvC = getCutFaceUV(pC, origin, tangent, bitangent, icon);
            
            // Render as proper triangle (no degenerate quads)
            tess.addVertexWithUV(x + pA.xCoord + offset.xCoord, 
                                y + pA.yCoord + offset.yCoord, 
                                z + pA.zCoord + offset.zCoord,
                                uvA[0], uvA[1]);
            tess.addVertexWithUV(x + pB.xCoord + offset.xCoord, 
                                y + pB.yCoord + offset.yCoord, 
                                z + pB.zCoord + offset.zCoord,
                                uvB[0], uvB[1]);
            tess.addVertexWithUV(x + pC.xCoord + offset.xCoord, 
                                y + pC.yCoord + offset.yCoord, 
                                z + pC.zCoord + offset.zCoord,
                                uvC[0], uvC[1]);
        }
    }
    
    /**
     * STABLE UV: origin at block center, world-space tangent/bitangent basis.
     * Texture repeats (tiles) for larger faces.
     */
    private static double[] getCutFaceUV(Vec3 p, Vec3 origin, Vec3 tangent, Vec3 bitangent, IIcon icon) {
        // Vector from origin (block center) to point
        double vx = p.xCoord - origin.xCoord;
        double vy = p.yCoord - origin.yCoord;
        double vz = p.zCoord - origin.zCoord;
        
        // Project onto tangent/bitangent basis (world-space coordinates)
        double uBlocks = vx * tangent.xCoord + vy * tangent.yCoord + vz * tangent.zCoord;
        double vBlocks = vx * bitangent.xCoord + vy * bitangent.yCoord + vz * bitangent.zCoord;
        
        // Convert to pixel coordinates (16 pixels per block)
        double uPx = uBlocks * 16.0;
        double vPx = vBlocks * 16.0;
        
        // Wrap for tiling (texture repeats)
        double uTile = wrap16(uPx);
        double vTile = wrap16(vPx);
        
        // Apply small inset to avoid atlas bleeding (0.5 texel inset)
        uTile = Math.max(0.5, Math.min(15.5, uTile));
        vTile = Math.max(0.5, Math.min(15.5, vTile));
        
        // Convert to icon UV
        double uFinal = icon.getInterpolatedU(uTile);
        double vFinal = icon.getInterpolatedV(vTile);
        
        return new double[] { uFinal, vFinal };
    }
    
    private static List<Vec3> deduplicatePoints(List<Vec3> points, double eps) {
        List<Vec3> unique = new ArrayList<>();
        double epsSq = eps * eps;
        
        for (Vec3 p : points) {
            boolean isDuplicate = false;
            for (Vec3 u : unique) {
                double dx = p.xCoord - u.xCoord;
                double dy = p.yCoord - u.yCoord;
                double dz = p.zCoord - u.zCoord;
                if (dx*dx + dy*dy + dz*dz < epsSq) {
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
    
    private static List<Vec3> calculateIntersections(float nx, float ny, float nz, double planeD) {
        List<Vec3> points = new ArrayList<>();
        
        checkEdgeX(points, nx, ny, nz, planeD, 0, 0);
        checkEdgeX(points, nx, ny, nz, planeD, 0, 1);
        checkEdgeX(points, nx, ny, nz, planeD, 1, 0);
        checkEdgeX(points, nx, ny, nz, planeD, 1, 1);
        
        checkEdgeY(points, nx, ny, nz, planeD, 0, 0);
        checkEdgeY(points, nx, ny, nz, planeD, 0, 1);
        checkEdgeY(points, nx, ny, nz, planeD, 1, 0);
        checkEdgeY(points, nx, ny, nz, planeD, 1, 1);
        
        checkEdgeZ(points, nx, ny, nz, planeD, 0, 0);
        checkEdgeZ(points, nx, ny, nz, planeD, 0, 1);
        checkEdgeZ(points, nx, ny, nz, planeD, 1, 0);
        checkEdgeZ(points, nx, ny, nz, planeD, 1, 1);
        
        return points;
    }
    
    private static void checkEdgeX(List<Vec3> points, float nx, float ny, float nz, 
                                    double planeD, int y, int z) {
        if (Math.abs(nx) < EPSILON) return;
        
        double t = (planeD - ny * y - nz * z) / nx;
        if (t >= -EPSILON && t <= 1.0 + EPSILON) {
            points.add(Vec3.createVectorHelper(clamp01(t), y, z));
        }
    }
    
    private static void checkEdgeY(List<Vec3> points, float nx, float ny, float nz,
                                    double planeD, int x, int z) {
        if (Math.abs(ny) < EPSILON) return;
        
        double t = (planeD - nx * x - nz * z) / ny;
        if (t >= -EPSILON && t <= 1.0 + EPSILON) {
            points.add(Vec3.createVectorHelper(x, clamp01(t), z));
        }
    }
    
    private static void checkEdgeZ(List<Vec3> points, float nx, float ny, float nz,
                                    double planeD, int x, int y) {
        if (Math.abs(nz) < EPSILON) return;
        
        double t = (planeD - nx * x - ny * y) / nz;
        if (t >= -EPSILON && t <= 1.0 + EPSILON) {
            points.add(Vec3.createVectorHelper(x, y, clamp01(t)));
        }
    }
    
    private static double clamp01(double v) {
        return Math.max(0.0, Math.min(1.0, v));
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
        Vec3 n = normalize(Vec3.createVectorHelper(nx, ny, nz));
        
        // Deterministic helper choice
        Vec3 helper;
        if (Math.abs(n.yCoord) < 0.9) {
            helper = Vec3.createVectorHelper(0, 1, 0);
        } else {
            helper = Vec3.createVectorHelper(1, 0, 0);
        }
        
        Vec3 tangent = normalize(crossProduct(helper, n));
        Vec3 bitangent = normalize(crossProduct(n, tangent));
        
        List<Vec3> sorted = new ArrayList<>(points);
        final Vec3 t = tangent;
        final Vec3 bit = bitangent;
        
        sorted.sort((p1, p2) -> {
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
    
    private static List<Vec3> ensureCorrectWinding(List<Vec3> points, float nx, float ny, float nz, boolean keepPositive) {
        if (points.size() < 3) return points;
        
        Vec3 p0 = points.get(0);
        Vec3 p1 = points.get(1);
        Vec3 p2 = points.get(2);
        
        Vec3 v1 = Vec3.createVectorHelper(p1.xCoord - p0.xCoord, p1.yCoord - p0.yCoord, p1.zCoord - p0.zCoord);
        Vec3 v2 = Vec3.createVectorHelper(p2.xCoord - p0.xCoord, p2.yCoord - p0.yCoord, p2.zCoord - p0.zCoord);
        
        Vec3 polyNormal = crossProduct(v1, v2);
        polyNormal = normalize(polyNormal);
        
        double dot = polyNormal.xCoord * nx + polyNormal.yCoord * ny + polyNormal.zCoord * nz;
        
        // Definition A: keepPositive means keep dist >= 0 side
        // Cut face should point toward the DISCARDED side
        boolean shouldReverse = keepPositive ? (dot > 0) : (dot < 0);
        
        if (shouldReverse) {
            Collections.reverse(points);
        }
        
        return points;
    }
    
    private static Vec3 crossProduct(Vec3 a, Vec3 b) {
        return Vec3.createVectorHelper(
            a.yCoord * b.zCoord - a.zCoord * b.yCoord,
            a.zCoord * b.xCoord - a.xCoord * b.zCoord,
            a.xCoord * b.yCoord - a.yCoord * b.xCoord
        );
    }
    
    private static Vec3 normalize(Vec3 v) {
        double len = Math.sqrt(v.xCoord * v.xCoord + v.yCoord * v.yCoord + v.zCoord * v.zCoord);
        if (len < EPSILON) {
            return Vec3.createVectorHelper(0, 0, 0);
        }
        return Vec3.createVectorHelper(v.xCoord / len, v.yCoord / len, v.zCoord / len);
    }
}
