package com.cuttableblocks.util;

import net.minecraft.util.Vec3;

/**
 * Discrete cut directions (18 classes) and rotation system.
 * 
 * This class provides:
 * - 18 base direction vectors (integer representations)
 * - 24 rotation matrices (cube rotations)
 * - Direction approximation from look vector
 */
public class CutDirections {
    
    // ====================================================================================
    // BASE DIRECTIONS (18 canonical integer vectors)
    // These represent direction classes under cube rotations
    // ====================================================================================
    
    public static final int[][] BASE_DIRS_18 = new int[][] {
        {-1,  0,  0},    // 0:  -X axis (axis-aligned)
        {-1, -1,  0},    // 1:  diagonal XY
        {-1, -1, -1},    // 2:  corner
        
        {-2, -1,  0},    // 3:  shallow diagonal
        {-2, -1, -1},    // 4:  
        {-2, -2, -1},    // 5:  
        
        {-4, -1,  0},    // 6:  very shallow
        {-4, -1, -1},    // 7:  
        {-4, -2,  1},    // 8:  
        {-4, -2, -1},    // 9:  
        {-4, -4, -1},    // 10: 
        
        {-8, -1,  0},    // 11: almost flat
        {-8, -1, -1},    // 12: 
        {-8, -2,  1},    // 13: 
        {-8, -2, -1},    // 14: 
        {-8, -4,  1},    // 15: 
        {-8, -4, -1},    // 16: 
        {-8, -8, -1}     // 17: 
    };
    
    public static final int NUM_DIRECTIONS = 18;
    public static final int NUM_ROTATIONS = 24;
    
    // ====================================================================================
    // ROTATION SYSTEM (24 cube rotations)
    // Each rotation is stored as: perm[3] (axis permutation) and sign[3] (axis sign)
    // Rotation formula: out[i] = sign[i] * v[perm[i]]
    // ====================================================================================
    
    private static final int[][] ROT_PERM = new int[NUM_ROTATIONS][3];
    private static final int[][] ROT_SIGN = new int[NUM_ROTATIONS][3];
    
    static {
        generateRotations();
    }
    
    /**
     * Generate all 24 rotations of the cube (determinant = +1).
     */
    private static void generateRotations() {
        int rotIdx = 0;
        
        // All permutations of axes (6)
        int[][] perms = {
            {0, 1, 2}, {0, 2, 1}, {1, 0, 2},
            {1, 2, 0}, {2, 0, 1}, {2, 1, 0}
        };
        
        for (int[] perm : perms) {
            // All sign combinations (8)
            for (int sx = -1; sx <= 1; sx += 2) {
                for (int sy = -1; sy <= 1; sy += 2) {
                    for (int sz = -1; sz <= 1; sz += 2) {
                        int[] sign = {sx, sy, sz};
                        
                        // Calculate determinant (must be +1 for proper rotation)
                        // det = sign[0]*sign[1]*sign[2]*signum(perm)
                        int permSign = permutationSign(perm);
                        int totalSign = sx * sy * sz * permSign;
                        
                        if (totalSign == 1) {
                            ROT_PERM[rotIdx] = perm.clone();
                            ROT_SIGN[rotIdx] = sign.clone();
                            rotIdx++;
                        }
                    }
                }
            }
        }
        
        if (rotIdx != NUM_ROTATIONS) {
            throw new RuntimeException("Expected 24 rotations, got " + rotIdx);
        }
    }
    
    /**
     * Calculate sign of permutation (parity).
     * Returns +1 for even, -1 for odd permutation.
     */
    private static int permutationSign(int[] perm) {
        int inversions = 0;
        for (int i = 0; i < 3; i++) {
            for (int j = i + 1; j < 3; j++) {
                if (perm[i] > perm[j]) inversions++;
            }
        }
        return (inversions % 2 == 0) ? 1 : -1;
    }
    
    // ====================================================================================
    // ROTATION OPERATIONS
    // ====================================================================================
    
    /**
     * Apply rotation to a vector.
     * v_world = R(rotId) * v_local
     */
    public static Vec3 rotate(int rotId, Vec3 v) {
        int[] perm = ROT_PERM[rotId];
        int[] sign = ROT_SIGN[rotId];
        
        double[] in = {v.xCoord, v.yCoord, v.zCoord};
        double[] out = new double[3];
        
        for (int i = 0; i < 3; i++) {
            out[i] = sign[i] * in[perm[i]];
        }
        
        return Vec3.createVectorHelper(out[0], out[1], out[2]);
    }
    
    /**
     * Apply inverse rotation to a vector.
     * v_local = R(rotId)^{-1} * v_world
     */
    public static Vec3 inverseRotate(int rotId, Vec3 v) {
        int[] perm = ROT_PERM[rotId];
        int[] sign = ROT_SIGN[rotId];
        
        double[] in = {v.xCoord, v.yCoord, v.zCoord};
        double[] out = new double[3];
        
        // Inverse: perm' = perm^{-1}, sign' = sign(perm^{-1}(i)) * sign(i)
        // Simpler: apply transpose (inverse of rotation matrix)
        for (int i = 0; i < 3; i++) {
            // Find which input index maps to this output
            for (int j = 0; j < 3; j++) {
                if (perm[j] == i) {
                    out[i] = sign[j] * in[j];
                    break;
                }
            }
        }
        
        return Vec3.createVectorHelper(out[0], out[1], out[2]);
    }
    
    // ====================================================================================
    // NORMAL VECTOR OPERATIONS
    // ====================================================================================
    
    /**
     * Normalize integer direction to unit vector.
     */
    public static Vec3 normalizeIntDir(int a, int b, int c) {
        double len = Math.sqrt(a*a + b*b + c*c);
        return Vec3.createVectorHelper(a/len, b/len, c/len);
    }
    
    /**
     * Get base direction vector (local space) for given dirId.
     */
    public static Vec3 getBaseDir(int dirId) {
        int[] d = BASE_DIRS_18[dirId];
        return normalizeIntDir(d[0], d[1], d[2]);
    }
    
    /**
     * Get world-space direction for given (rotId, dirId).
     */
    public static Vec3 getWorldDir(int rotId, int dirId) {
        Vec3 local = getBaseDir(dirId);
        return rotate(rotId, local);
    }
    
    // ====================================================================================
    // DIRECTION APPROXIMATION
    // ====================================================================================
    
    /**
     * Find best matching direction for given look vector.
     * Returns dirId (0..17) of closest base direction.
     * 
     * @param lookVec World-space look vector (should be normalized)
     * @param rotId Block rotation (0..23)
     * @return Best matching direction ID (0..17)
     */
    public static int findBestDirection(Vec3 lookVec, int rotId) {
        // Transform to local space
        Vec3 local = inverseRotate(rotId, lookVec);
        
        int bestId = 0;
        double bestDot = -1e9;
        
        for (int i = 0; i < NUM_DIRECTIONS; i++) {
            Vec3 base = getBaseDir(i);
            double dot = local.xCoord * base.xCoord 
                       + local.yCoord * base.yCoord 
                       + local.zCoord * base.zCoord;
            
            if (dot > bestDot) {
                bestDot = dot;
                bestId = i;
            }
        }
        
        return bestId;
    }
    
    // ====================================================================================
    // RENDER MODE CLASSIFICATION (for half-block fixes)
    // ====================================================================================
    
    public enum RenderMode {
        AXIS_X,     // Axis-aligned along X
        AXIS_Y,     // Axis-aligned along Y  
        AXIS_Z,     // Axis-aligned along Z
        ADVANCED    // Diagonal/other
    }
    
    /**
     * Determine render mode for given direction.
     * This is deterministic based on dirId, not float thresholds.
     */
    public static RenderMode getRenderMode(int rotId, int dirId) {
        Vec3 worldDir = getWorldDir(rotId, dirId);
        
        double nx = Math.abs(worldDir.xCoord);
        double ny = Math.abs(worldDir.yCoord);
        double nz = Math.abs(worldDir.zCoord);
        
        // Check if exactly axis-aligned (one component is 1.0, others 0)
        double EPS = 1e-6;
        boolean isAxisX = (Math.abs(nx - 1.0) < EPS) && (ny < EPS) && (nz < EPS);
        boolean isAxisY = (Math.abs(ny - 1.0) < EPS) && (nx < EPS) && (nz < EPS);
        boolean isAxisZ = (Math.abs(nz - 1.0) < EPS) && (nx < EPS) && (ny < EPS);
        
        if (isAxisX) return RenderMode.AXIS_X;
        if (isAxisY) return RenderMode.AXIS_Y;
        if (isAxisZ) return RenderMode.AXIS_Z;
        
        return RenderMode.ADVANCED;
    }
    
    /**
     * Check if direction is exactly axis-aligned (for half-block logic).
     */
    public static boolean isAxisAligned(int dirId) {
        int[] d = BASE_DIRS_18[dirId];
        int nonZero = 0;
        if (d[0] != 0) nonZero++;
        if (d[1] != 0) nonZero++;
        if (d[2] != 0) nonZero++;
        return nonZero == 1;
    }
    
    /**
     * Get axis index for axis-aligned direction (0=X, 1=Y, 2=Z).
     * Returns -1 if not axis-aligned.
     */
    public static int getAxis(int dirId) {
        int[] d = BASE_DIRS_18[dirId];
        if (d[0] != 0 && d[1] == 0 && d[2] == 0) return 0;
        if (d[0] == 0 && d[1] != 0 && d[2] == 0) return 1;
        if (d[0] == 0 && d[1] == 0 && d[2] != 0) return 2;
        return -1;
    }
}
