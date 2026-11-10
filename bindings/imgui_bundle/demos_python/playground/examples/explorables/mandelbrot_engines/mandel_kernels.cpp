// The hot loops of mandelbrot_engines.py: plain C++, no library, no Dear ImGui. Python calls them through ctypes.
// Each function fills the rows [row0, row1) of two images of w x h pixels:
//   count[i]: the number of iterations before |z| > 16 (max_iter when the point never escapes)
//   size2[i]: |z|^2 at that step (Python uses it to smooth the colors)
// Python calls them from several threads, one band of rows each.
// The ::code and ::endcode lines name the regions that the page shows beside each engine.
extern "C" {

const double ESCAPE2 = 256.0;  // |z| > 16

// ::code Double
// z <- z^2 + c in double precision. (x0, y0) is the center of the top left pixel; pixel is the size of a pixel.
void mandel_double(double x0, double y0, double pixel, int w, int h, int row0, int row1, int max_iter,
                   int* count, float* size2)
{
    for (int row = row0; row < row1; ++row)
        for (int col = 0; col < w; ++col)
        {
            double cx = x0 + col * pixel, cy = y0 - row * pixel;
            double x = 0, y = 0, x2 = 0, y2 = 0;
            int n = 0;
            while (n < max_iter && x2 + y2 <= ESCAPE2)
            {
                y = 2 * x * y + cy;
                x = x2 - y2 + cx;
                x2 = x * x;
                y2 = y * y;
                ++n;
            }
            count[row * w + col] = n;
            size2[row * w + col] = (float)(x2 + y2);
        }
}
// ::endcode Double

// ::code Perturbation
// Perturbation: the same picture, around a reference orbit Z computed once with many digits (by Python).
// A pixel at c = C + dc has the orbit z(n) = Z(n) + d(n), and only d is iterated here, in double precision:
//     d(n+1) = 2 * Z(n) * d(n) + d(n)^2 + dc
// ref holds Z(0) = 0, Z(1), ... Z(n_ref - 1) as (re, im) pairs. (dx0, dy0) is the offset of the top left pixel
// from C. Since d and dc are tiny, the pixel size can go far below the precision of a double (1e-16).
void mandel_perturbation(const double* ref, int n_ref, double dx0, double dy0, double pixel,
                         int w, int h, int row0, int row1, int max_iter, int* count, float* size2)
{
    for (int row = row0; row < row1; ++row)
        for (int col = 0; col < w; ++col)
        {
            double dcx = dx0 + col * pixel, dcy = dy0 - row * pixel;
            double dx = 0, dy = 0, zx = 0, zy = 0;
            int n = 0, m = 0;  // m: the index in the reference orbit
            while (n < max_iter)
            {
                double Zx = ref[2 * m], Zy = ref[2 * m + 1];
                double t = 2 * (Zx * dx - Zy * dy) + dx * dx - dy * dy + dcx;
                dy = 2 * (Zx * dy + Zy * dx) + 2 * dx * dy + dcy;
                dx = t;
                ++m, ++n;
                zx = ref[2 * m] + dx, zy = ref[2 * m + 1] + dy;
                double z2 = zx * zx + zy * zy;
                if (z2 > ESCAPE2)
                    break;
                // Rebasing: when z gets smaller than d, d has lost its digits. Restart from Z(0) = 0 with d = z.
                // Also when the reference orbit ends (it escaped before this pixel did).
                // It is rare, and [[unlikely]] says so: the compiler keeps a branch, and the loop runs twice faster.
                if (z2 < dx * dx + dy * dy || m == n_ref - 1) [[unlikely]]
                    dx = zx, dy = zy, m = 0;
            }
            count[row * w + col] = n;
            size2[row * w + col] = (float)(zx * zx + zy * zy);
        }
}
// ::endcode Perturbation

}  // extern "C"
