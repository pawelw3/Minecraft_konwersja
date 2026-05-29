package pl.pawel.cuttableblocks.client.render;

import com.mojang.math.Vector3f;
import net.minecraft.core.Direction;

import java.util.ArrayList;
import java.util.List;

/**
 * Generates the geometry for an arbitrary-plane cut through a unit cube [0,1]^3.
 *
 * Uses Sutherland-Hodgman clipping for each cube face, then triangulates.
 * Also generates the interior "cut face" so the block looks solid.
 */
public class CuttableGeometry {

    public static class Vertex {
        public final float x, y, z;
        public final float u, v;
        public final float nx, ny, nz;

        public Vertex(float x, float y, float z, float u, float v, float nx, float ny, float nz) {
            this.x = x; this.y = y; this.z = z;
            this.u = u; this.v = v;
            this.nx = nx; this.ny = ny; this.nz = nz;
        }
    }

    /**
     * Generate a list of triangles representing the half-cube kept after the cut.
     */
    public static List<Vertex[]> generateTriangles(int dirId, int rotId, boolean keepPositive) {
        Vector3f normal = computeNormal(dirId, rotId);
        float d = 0.5f * (normal.x() + normal.y() + normal.z());

        if (!keepPositive) {
            normal = new Vector3f(-normal.x(), -normal.y(), -normal.z());
            d = -d;
        }

        List<Vertex[]> triangles = new ArrayList<>();

        // Cube faces: 4 vertices each, UV axes, face normal
        Face[] faces = new Face[] {
            new Face(new float[][]{{0,0,0},{1,0,0},{1,0,1},{0,0,1}}, new int[]{0,2}, new float[]{0,-1,0}),
            new Face(new float[][]{{0,1,0},{0,1,1},{1,1,1},{1,1,0}}, new int[]{0,2}, new float[]{0, 1,0}),
            new Face(new float[][]{{0,0,0},{0,1,0},{1,1,0},{1,0,0}}, new int[]{0,1}, new float[]{0, 0,-1}),
            new Face(new float[][]{{0,0,1},{1,0,1},{1,1,1},{0,1,1}}, new int[]{0,1}, new float[]{0, 0, 1}),
            new Face(new float[][]{{0,0,0},{0,0,1},{0,1,1},{0,1,0}}, new int[]{2,1}, new float[]{-1,0,0}),
            new Face(new float[][]{{1,0,0},{1,1,0},{1,1,1},{1,0,1}}, new int[]{2,1}, new float[]{ 1,0,0})
        };

        // Clip each cube face
        for (Face face : faces) {
            List<Vertex> poly = new ArrayList<>();
            for (float[] p : face.verts) {
                poly.add(new Vertex(p[0], p[1], p[2], p[face.uvAxes[0]], p[face.uvAxes[1]],
                        face.normal[0], face.normal[1], face.normal[2]));
            }
            List<Vertex> clipped = clipPolygon(poly, normal, d);
            triangulate(clipped, triangles);
        }

        // Generate cut face
        List<Vertex> cutFace = generateCutFace(normal, d);
        List<Vertex> cutFaceWithNormal = new ArrayList<>();
        for (Vertex v : cutFace) {
            cutFaceWithNormal.add(new Vertex(v.x, v.y, v.z, v.u, v.v, normal.x(), normal.y(), normal.z()));
        }
        triangulate(cutFaceWithNormal, triangles);

        return triangles;
    }

    private static class Face {
        final float[][] verts;
        final int[] uvAxes;
        final float[] normal;
        Face(float[][] verts, int[] uvAxes, float[] normal) {
            this.verts = verts; this.uvAxes = uvAxes; this.normal = normal;
        }
    }

    private static Vector3f computeNormal(int dirId, int rotId) {
        Direction dir = Direction.from3DDataValue(dirId % 6);
        Vector3f normal = new Vector3f(dir.getStepX(), dir.getStepY(), dir.getStepZ());

        if (rotId > 0) {
            float angle = (rotId % 24) * ((float) Math.PI / 12f);
            Vector3f axis;
            if (dir.getAxis() == Direction.Axis.Y) {
                axis = new Vector3f(1, 0, 0);
            } else {
                axis = new Vector3f(0, 1, 0);
            }
            normal = rotateAroundAxis(normal, axis, angle);
        }

        return normal;
    }

    /** Rodrigues' rotation formula. */
    private static Vector3f rotateAroundAxis(Vector3f v, Vector3f axis, float angle) {
        float kx = axis.x(), ky = axis.y(), kz = axis.z();
        float vx = v.x(), vy = v.y(), vz = v.z();
        float c = (float) Math.cos(angle);
        float s = (float) Math.sin(angle);
        float dot = vx * kx + vy * ky + vz * kz;

        float rx = vx * c + (ky * vz - kz * vy) * s + kx * dot * (1 - c);
        float ry = vy * c + (kz * vx - kx * vz) * s + ky * dot * (1 - c);
        float rz = vz * c + (kx * vy - ky * vx) * s + kz * dot * (1 - c);

        return new Vector3f(rx, ry, rz);
    }

    private static float dist(Vertex v, Vector3f normal, float d) {
        return v.x * normal.x() + v.y * normal.y() + v.z * normal.z() - d;
    }

    private static Vertex interpolate(Vertex a, Vertex b, float da, float db) {
        float t = da / (da - db);
        return new Vertex(
                a.x + (b.x - a.x) * t,
                a.y + (b.y - a.y) * t,
                a.z + (b.z - a.z) * t,
                a.u + (b.u - a.u) * t,
                a.v + (b.v - a.v) * t,
                a.nx, a.ny, a.nz
        );
    }

    private static List<Vertex> clipPolygon(List<Vertex> poly, Vector3f normal, float d) {
        List<Vertex> output = new ArrayList<>();
        int n = poly.size();
        if (n == 0) return output;

        for (int i = 0; i < n; i++) {
            Vertex current = poly.get(i);
            Vertex next = poly.get((i + 1) % n);
            float dc = dist(current, normal, d);
            float dn = dist(next, normal, d);
            boolean inc = dc >= -1e-5f;
            boolean inn = dn >= -1e-5f;

            if (inc && inn) {
                output.add(next);
            } else if (inc && !inn) {
                output.add(interpolate(current, next, dc, dn));
            } else if (!inc && inn) {
                output.add(interpolate(current, next, dc, dn));
                output.add(next);
            }
        }
        return output;
    }

    private static void triangulate(List<Vertex> poly, List<Vertex[]> triangles) {
        int n = poly.size();
        if (n < 3) return;
        for (int i = 1; i < n - 1; i++) {
            triangles.add(new Vertex[]{poly.get(0), poly.get(i), poly.get(i + 1)});
        }
    }

    /** Find all intersection points of the plane with cube edges, sorted circularly. */
    private static List<Vertex> generateCutFace(Vector3f normal, float d) {
        List<Vertex> points = new ArrayList<>();

        Edge[] edges = new Edge[] {
            new Edge(new float[]{0,0,0}, new float[]{1,0,0}, new int[]{0,2}),
            new Edge(new float[]{1,0,0}, new float[]{1,0,1}, new int[]{0,2}),
            new Edge(new float[]{1,0,1}, new float[]{0,0,1}, new int[]{0,2}),
            new Edge(new float[]{0,0,1}, new float[]{0,0,0}, new int[]{0,2}),
            new Edge(new float[]{0,1,0}, new float[]{1,1,0}, new int[]{0,2}),
            new Edge(new float[]{1,1,0}, new float[]{1,1,1}, new int[]{0,2}),
            new Edge(new float[]{1,1,1}, new float[]{0,1,1}, new int[]{0,2}),
            new Edge(new float[]{0,1,1}, new float[]{0,1,0}, new int[]{0,2}),
            new Edge(new float[]{0,0,0}, new float[]{0,1,0}, new int[]{2,1}),
            new Edge(new float[]{1,0,0}, new float[]{1,1,0}, new int[]{2,1}),
            new Edge(new float[]{1,0,1}, new float[]{1,1,1}, new int[]{2,1}),
            new Edge(new float[]{0,0,1}, new float[]{0,1,1}, new int[]{2,1})
        };

        for (Edge edge : edges) {
            float[] p1 = edge.p1;
            float[] p2 = edge.p2;
            float d1 = p1[0] * normal.x() + p1[1] * normal.y() + p1[2] * normal.z() - d;
            float d2 = p2[0] * normal.x() + p2[1] * normal.y() + p2[2] * normal.z() - d;

            if ((d1 >= 0 && d2 < 0) || (d1 < 0 && d2 >= 0)) {
                float t = d1 / (d1 - d2);
                float x = p1[0] + (p2[0] - p1[0]) * t;
                float y = p1[1] + (p2[1] - p1[1]) * t;
                float z = p1[2] + (p2[2] - p1[2]) * t;
                float u, v;
                if (Math.abs(normal.y()) < 0.99f) {
                    u = x; v = z;
                } else {
                    u = x; v = y;
                }
                points.add(new Vertex(x, y, z, u, v, 0, 0, 0));
            }
        }

        // Sort circularly around the plane normal
        if (points.size() >= 3) {
            float sx = 0, sy = 0, sz = 0;
            for (Vertex v : points) { sx += v.x; sy += v.y; sz += v.z; }
            final float cx = sx / points.size();
            final float cy = sy / points.size();
            final float cz = sz / points.size();

            Vector3f n = new Vector3f(normal.x(), normal.y(), normal.z());
            Vector3f ref = (Math.abs(n.y()) < 0.99f) ? new Vector3f(0, 1, 0) : new Vector3f(1, 0, 0);
            Vector3f uAxis = cross(ref, n);
            if (uAxis.x() == 0 && uAxis.y() == 0 && uAxis.z() == 0) {
                uAxis = new Vector3f(1, 0, 0);
            }
            uAxis.normalize();
            Vector3f vAxis = cross(n, uAxis);
            vAxis.normalize();

            final Vector3f fuAxis = uAxis;
            final Vector3f fvAxis = vAxis;

            points.sort((a, b) -> {
                float ax = (a.x - cx) * fuAxis.x() + (a.y - cy) * fuAxis.y() + (a.z - cz) * fuAxis.z();
                float ay = (a.x - cx) * fvAxis.x() + (a.y - cy) * fvAxis.y() + (a.z - cz) * fvAxis.z();
                float bx = (b.x - cx) * fuAxis.x() + (b.y - cy) * fuAxis.y() + (b.z - cz) * fuAxis.z();
                float by = (b.x - cx) * fvAxis.x() + (b.y - cy) * fvAxis.y() + (b.z - cz) * fvAxis.z();
                float angleA = (float) Math.atan2(ay, ax);
                float angleB = (float) Math.atan2(by, bx);
                return Float.compare(angleA, angleB);
            });
        }

        return points;
    }

    private static class Edge {
        final float[] p1, p2;
        final int[] uvAxes;
        Edge(float[] p1, float[] p2, int[] uvAxes) { this.p1 = p1; this.p2 = p2; this.uvAxes = uvAxes; }
    }

    private static Vector3f cross(Vector3f a, Vector3f b) {
        return new Vector3f(
                a.y() * b.z() - a.z() * b.y(),
                a.z() * b.x() - a.x() * b.z(),
                a.x() * b.y() - a.y() * b.x()
        );
    }
}
