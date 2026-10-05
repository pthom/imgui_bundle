-- The first points (loaded by demo_julia_points_dev into the local database, and once into the production one).
-- Both lie outside the Mandelbrot set: their Julia sets are dust. A second load adds nothing.
INSERT INTO points (name, c_re, c_im, view_width, max_iter, author, created)
SELECT 'Oscilloscope', -1.806, -0.024, 0.1, 80, 'Pascal', '2026-10-05T00:00:00Z'
WHERE NOT EXISTS (SELECT 1 FROM points WHERE name = 'Oscilloscope');

INSERT INTO points (name, c_re, c_im, view_width, max_iter, author, created)
SELECT 'Marupikatu Islands', -1.277, -0.860, 2.0, 80, 'Pascal', '2026-10-05T00:00:00Z'
WHERE NOT EXISTS (SELECT 1 FROM points WHERE name = 'Marupikatu Islands');
