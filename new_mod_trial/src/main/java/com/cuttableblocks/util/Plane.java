package com.cuttableblocks.util;

import net.minecraft.util.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Utility class for plane-block intersection calculations.
 */
public class Plane {
    
    /**
     * Represents an intersection point with UV coordinates.
     */
    public static class IntersectionPoint {
        public final double x, y, z;
        
        public IntersectionPoint(double x, double y, double z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }
        
        public Vec3 toVec3() {
            return Vec3.createVectorHelper(x, y, z);
        }
    }
    
    /**
     * Calculates intersection points between a plane and the unit cube [0,1]x[0,1]x[0,1].
     * 
     * Plane equation: nx*(x-0.5) + ny*(y-0.5) + nz*(z-0.5) = 0
     * Which simplifies to: nx*x + ny*y + nz*z = 0.5*(nx+ny+nz)
     * 
     * @param nx X component of plane normal (should be normalized)
     * @param ny Y component of plane normal
     * @param nz Z component of plane normal
     * @return List of intersection points on cube edges
     */
    public static List<IntersectionPoint> getIntersectionsWithUnitCube(float nx, float ny, float nz) {
        List<IntersectionPoint> points = new ArrayList<>();
        float d = 0.5f * (nx + ny + nz);
        
        // Check edges parallel to X axis (4 edges)
        checkEdgeParallelX(points, nx, ny, nz, d, 0, 0);
        checkEdgeParallelX(points, nx, ny, nz, d, 0, 1);
        checkEdgeParallelX(points, nx, ny, nz, d, 1, 0);
        checkEdgeParallelX(points, nx, ny, nz, d, 1, 1);
        
        // Check edges parallel to Y axis (4 edges)
        checkEdgeParallelY(points, nx, ny, nz, d, 0, 0);
        checkEdgeParallelY(points, nx, ny, nz, d, 0, 1);
        checkEdgeParallelY(points, nx, ny, nz, d, 1, 0);
        checkEdgeParallelY(points, nx, ny, nz, d, 1, 1);
        
        // Check edges parallel to Z axis (4 edges)
        checkEdgeParallelZ(points, nx, ny, nz, d, 0, 0);
        checkEdgeParallelZ(points, nx, ny, nz, d, 0, 1);
        checkEdgeParallelZ(points, nx, ny, nz, d, 1, 0);
        checkEdgeParallelZ(points, nx, ny, nz, d, 1, 1);
        
        return points;
    }
    
    private static void checkEdgeParallelX(List<IntersectionPoint> points, 
                                            float nx, float ny, float nz, float d,
                                            int y, int z) {
        // Edge: (t, y, z) where t in [0, 1]
        // Equation: nx*t + ny*y + nz*z = d
        if (Math.abs(nx) < 0.0001f) {
            return; // Parallel to plane
        }
        
        float t = (d - ny * y - nz * z) / nx;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(new IntersectionPoint(t, y, z));
        }
    }
    
    private static void checkEdgeParallelY(List<IntersectionPoint> points, 
                                            float nx, float ny, float nz, float d,
                                            int x, int z) {
        // Edge: (x, t, z) where t in [0, 1]
        if (Math.abs(ny) < 0.0001f) {
            return;
        }
        
        float t = (d - nx * x - nz * z) / ny;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(new IntersectionPoint(x, t, z));
        }
    }
    
    private static void checkEdgeParallelZ(List<IntersectionPoint> points, 
                                            float nx, float ny, float nz, float d,
                                            int x, int y) {
        // Edge: (x, y, t) where t in [0, 1]
        if (Math.abs(nz) < 0.0001f) {
            return;
        }
        
        float t = (d - nx * x - ny * y) / nz;
        if (t >= 0.0f && t <= 1.0f) {
            points.add(new IntersectionPoint(x, y, t));
        }
    }
    
    /**
     * Determines which side of the plane a point is on.
     * @return Positive if on positive side, negative if on negative side, 0 if on plane
     */
    public static double pointPlaneDistance(double px, double py, double pz,
                                             float nx, float ny, float nz) {
        float d = 0.5f * (nx + ny + nz);
        return nx * px + ny * py + nz * pz - d;
    }
    
    /**
     * Checks if a point is on the "keep" side of the plane.
     */
    public static boolean isPointOnKeepSide(double px, double py, double pz,
                                             float nx, float ny, float nz, 
                                             boolean keepPositive) {
        double dist = pointPlaneDistance(px, py, pz, nx, ny, nz);
        return keepPositive ? dist > 0 : dist < 0;
    }
}
