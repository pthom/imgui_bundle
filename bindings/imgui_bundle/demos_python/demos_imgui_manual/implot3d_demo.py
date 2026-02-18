# This file is an almost line by line transcription of implot3d_demo.cpp
# ( https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp )



from imgui_bundle import imgui, immapp, implot3d, imgui_ctx, ImVec4, ImVec2, IM_COL32
from imgui_bundle.demos_python.demos_imgui_manual.implot3d_meshes import make_cube_mesh, make_sphere_mesh, make_duck_mesh
from imgui_bundle.demos_python.demo_utils.api_demos import set_hello_imgui_demo_assets_folder

import numpy as np
from numpy.typing import NDArray

set_hello_imgui_demo_assets_folder()

def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the interactive manual. Maps sections to source code."""
    pass


#-----------------------------------------------------------------------------
# [SECTION] Demo Textures
#-----------------------------------------------------------------------------


def make_checkerboard_texture(size: int = 256, tile_size: int = 32) -> NDArray[np.uint8]:
    """Create a checkerboard RGBA texture as a numpy array."""
    img = np.zeros((size, size, 4), dtype=np.uint8)
    for y in range(size):
        for x in range(size):
            if ((x // tile_size) + (y // tile_size)) % 2 == 0:
                color = (255, 255, 255, 255)
            else:
                color = (64, 64, 64, 255)
            img[y, x] = color
    return img


def make_gradient_circle_texture(size: int = 256) -> NDArray[np.uint8]:
    """Create a circular gradient texture with transparency and a color tint."""
    img = np.zeros((size, size, 4), dtype=np.uint8)
    center = size / 2
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            dist = np.sqrt(dx * dx + dy * dy) / (size / 2)
            dist = np.clip(dist, 0.0, 1.0)
            alpha = int((1.0 - dist) * 255)
            img[y, x] = (30, 144, 255, alpha)  # DodgerBlue with radial alpha
    return img

#-----------------------------------------------------------------------------
# [SECTION] Helpers
#-----------------------------------------------------------------------------

def help_marker(desc: str):
    imgui.text_disabled("(?)")
    if imgui.begin_item_tooltip():
        imgui.push_text_wrap_pos(imgui.get_font_size() * 35.0)
        imgui.text_unformatted(desc)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()


def checkbox_flag(flags: int, flag: int, flag_name: str = None) -> tuple[bool, int]:
    """
    Helper function to create a checkbox that toggles a flag bit.
    Mimics C++ macro: CHECKBOX_FLAG(flags, flag)

    Args:
        flags: Current flags value
        flag: The flag bit to toggle
        flag_name: Optional name for the checkbox (if None, uses flag's string representation)

    Returns:
        Tuple of (changed, new_flags)
    """
    if flag_name is None:
        # Try to get the flag name from the enum
        flag_name = str(flag)

    changed, new_flags = imgui.checkbox_flags(flag_name, flags, flag)
    return changed, new_flags


class CircularBuffer:
    """A simple circular buffer using NumPy arrays, mimicking C++'s ScrollingBuffer."""

    def __init__(self, max_size=2000):
        self.max_size = max_size
        self.data = np.full(max_size, np.nan, dtype=np.float32)  # Start with NaN values
        self.offset = 0
        self.size = 0  # Tracks the number of valid points

    def add_point(self, value):
        self.data[self.offset] = value
        self.offset = (self.offset + 1) % self.max_size
        self.size = min(self.size + 1, self.max_size)

    def get_data(self):
        """Returns the data in the correct chronological order."""
        if self.size < self.max_size:
            return self.data[:self.size]
        return np.roll(self.data, -self.offset)


def demo_line_plots():
    IMGUI_DEMO_MARKER("Plots/Line Plots")
    static = demo_line_plots

    # Update static values every frame since they depend on `imgui.get_time()`
    static.xs1 = np.linspace(0, 1, 1001)
    static.ys1 = 0.5 + 0.5 * np.cos(50 * (static.xs1 + imgui.get_time() / 10))
    static.zs1 = 0.5 + 0.5 * np.sin(50 * (static.xs1 + imgui.get_time() / 10))

    static.xs2 = np.linspace(0, 1, 20)
    static.ys2 = static.xs2 ** 2
    static.zs2 = static.xs2 * static.ys2

    if implot3d.begin_plot("Line Plots"):
        implot3d.setup_axes("x", "y", "z")
        implot3d.plot_line("f(x)", static.xs1, static.ys1, static.zs1)
        implot3d.plot_line("g(x)", static.xs2, static.ys2, static.zs2,
                          spec=implot3d.Spec(marker=implot3d.Marker_.circle,
                                           flags=implot3d.LineFlags_.segments))
        implot3d.end_plot()


def demo_scatter_plots():
    IMGUI_DEMO_MARKER("Plots/Scatter Plots")
    static = demo_scatter_plots

    if not hasattr(static, "xs1"):  # Initialize static data only once
        np.random.seed(0)

        static.xs1 = np.linspace(0, 0.99, 100)
        static.ys1 = static.xs1 + 0.1 * np.random.rand(100)
        static.zs1 = static.xs1 + 0.1 * np.random.rand(100)

        static.xs2 = 0.25 + 0.2 * np.random.rand(50)
        static.ys2 = 0.50 + 0.2 * np.random.rand(50)
        static.zs2 = 0.75 + 0.2 * np.random.rand(50)

    if implot3d.begin_plot("Scatter Plots"):
        implot3d.plot_scatter("Data 1", static.xs1, static.ys1, static.zs1)

        implot3d.plot_scatter("Data 2", static.xs2, static.ys2, static.zs2,
                             spec=implot3d.Spec(
                                 marker=implot3d.Marker_.square,
                                 marker_size=6,
                                 marker_line_color=implot3d.get_colormap_color(1),
                                 marker_fill_color=implot3d.get_colormap_color(1),
                                 fill_alpha=0.25))

        implot3d.end_plot()


def demo_triangle_plots():
    IMGUI_DEMO_MARKER("Plots/Triangle Plots")
    static = demo_triangle_plots

    if not hasattr(static, "xs"):  # Initialize static data only once
        # Pyramid coordinates
        ax, ay, az = 0.0, 0.0, 1.0  # Apex
        cx = [-0.5, 0.5, 0.5, -0.5]  # Base corners (x-coordinates)
        cy = [-0.5, -0.5, 0.5, 0.5]  # Base corners (y-coordinates)
        cz = [0.0, 0.0, 0.0, 0.0]  # Base corners (z-coordinates)

        # Collect all vertices in separate lists
        xs, ys, zs = [], [], []

        def add_vertex(x, y, z):
            xs.append(x)
            ys.append(y)
            zs.append(z)

        # Side triangles
        add_vertex(ax, ay, az), add_vertex(cx[0], cy[0], cz[0]), add_vertex(cx[1], cy[1], cz[1])
        add_vertex(ax, ay, az), add_vertex(cx[1], cy[1], cz[1]), add_vertex(cx[2], cy[2], cz[2])
        add_vertex(ax, ay, az), add_vertex(cx[2], cy[2], cz[2]), add_vertex(cx[3], cy[3], cz[3])
        add_vertex(ax, ay, az), add_vertex(cx[3], cy[3], cz[3]), add_vertex(cx[0], cy[0], cz[0])

        # Base triangles
        add_vertex(cx[0], cy[0], cz[0]), add_vertex(cx[1], cy[1], cz[1]), add_vertex(cx[2], cy[2], cz[2])
        add_vertex(cx[0], cy[0], cz[0]), add_vertex(cx[2], cy[2], cz[2]), add_vertex(cx[3], cy[3], cz[3])

        # Convert lists to contiguous NumPy arrays
        static.xs = np.array(xs, dtype=np.float32)
        static.ys = np.array(ys, dtype=np.float32)
        static.zs = np.array(zs, dtype=np.float32)
        # Initialize triangle flags
        static.flags = implot3d.TriangleFlags_.none.value

    # Triangle flags UI
    _, static.flags = checkbox_flag(static.flags, implot3d.TriangleFlags_.no_lines.value, "NoLines")
    _, static.flags = checkbox_flag(static.flags, implot3d.TriangleFlags_.no_fill.value, "NoFill")
    _, static.flags = checkbox_flag(static.flags, implot3d.TriangleFlags_.no_markers.value, "NoMarkers")

    if implot3d.begin_plot("Triangle Plots"):
        implot3d.setup_axes_limits(-1, 1, -1, 1, -0.5, 1.5)

        # Setup pyramid colors and flags using Spec
        spec = implot3d.Spec(
            fill_color=implot3d.get_colormap_color(0),
            line_color=implot3d.get_colormap_color(1),
            marker=implot3d.Marker_.square,
            marker_size=3,
            flags=static.flags
        )

        # Plot pyramid (6 triangles, 3 vertices each = 18 total vertices)
        implot3d.plot_triangle("Pyramid", static.xs, static.ys, static.zs, spec=spec)
        implot3d.end_plot()


def demo_quad_plots():
    IMGUI_DEMO_MARKER("Plots/Quad Plots")
    static = demo_quad_plots

    if not hasattr(static, "xs"):  # Initialize static data only once
        # Cube vertex coordinates for +x, -x, +y, -y, +z, -z faces
        static.xs = np.array([
            # +x face
            1, 1, 1, 1,
            # -x face
            -1, -1, -1, -1,
            # +y face
            -1, 1, 1, -1,
            # -y face
            -1, 1, 1, -1,
            # +z face
            -1, 1, 1, -1,
            # -z face
            -1, 1, 1, -1
        ], dtype=np.float32)

        static.ys = np.array([
            # +x face
            -1, 1, 1, -1,
            # -x face
            -1, 1, 1, -1,
            # +y face
            1, 1, 1, 1,
            # -y face
            -1, -1, -1, -1,
            # +z face
            -1, -1, 1, 1,
            # -z face
            -1, -1, 1, 1
        ], dtype=np.float32)

        static.zs = np.array([
            # +x face
            -1, -1, 1, 1,
            # -x face
            -1, -1, 1, 1,
            # +y face
            -1, -1, 1, 1,
            # -y face
            -1, -1, 1, 1,
            # +z face
            1, 1, 1, 1,
            # -z face
            -1, -1, -1, -1
        ], dtype=np.float32)

        static.flags = implot3d.QuadFlags_.none.value

    _, static.flags = checkbox_flag(static.flags, implot3d.QuadFlags_.no_lines.value, "NoLines")
    _, static.flags = checkbox_flag(static.flags, implot3d.QuadFlags_.no_fill.value, "NoFill")
    _, static.flags = checkbox_flag(static.flags, implot3d.QuadFlags_.no_markers.value, "NoMarkers")

    if implot3d.begin_plot("Quad Plots"):
        implot3d.setup_axes_limits(-1.5, 1.5, -1.5, 1.5, -1.5, 1.5)

        # Define face colors
        colors = {
            "X": (0.8, 0.2, 0.2, 0.8),  # Red
            "Y": (0.2, 0.8, 0.2, 0.8),  # Green
            "Z": (0.2, 0.2, 0.8, 0.8)   # Blue
        }

        # Render +x and -x faces
        color_x = colors["X"]
        implot3d.plot_quad("X", static.xs[0:8], static.ys[0:8], static.zs[0:8],
                            spec=implot3d.Spec(
                                fill_color=color_x,
                                line_color=color_x,
                                marker=implot3d.Marker_.square,
                                marker_size=3,
                                marker_line_color=color_x,
                                marker_fill_color=color_x,
                                flags=static.flags))

        # Render +y and -y faces
        color_y = colors["Y"]
        implot3d.plot_quad("Y", static.xs[8:16], static.ys[8:16], static.zs[8:16],
                            spec=implot3d.Spec(
                                fill_color=color_y,
                                line_color=color_y,
                                marker=implot3d.Marker_.square,
                                marker_size=3,
                                marker_line_color=color_y,
                                marker_fill_color=color_y,
                                flags=static.flags))

        # Render +z and -z faces
        color_z = colors["Z"]
        implot3d.plot_quad("Z", static.xs[16:24], static.ys[16:24], static.zs[16:24],
                            spec=implot3d.Spec(
                                fill_color=color_z,
                                line_color=color_z,
                                marker=implot3d.Marker_.square,
                                marker_size=3,
                                marker_line_color=color_z,
                                marker_fill_color=color_z,
                                flags=static.flags))

        implot3d.end_plot()


def demo_surface_plots():
    IMGUI_DEMO_MARKER("Plots/Surface Plots")
    static = demo_surface_plots

    # Constants
    n = 20
    min_val, max_val = -1.0, 1.0
    # step = (max_val - min_val) / (N - 1)

    # Initialize static variables
    if not hasattr(static, "xs"):
        # Meshgrid for X and Y values
        xs, ys = np.meshgrid(np.linspace(min_val, max_val, n), np.linspace(min_val, max_val, n))

        static.xs = xs.flatten()
        static.ys = ys.flatten()
        static.zs = np.zeros_like(static.xs)  # Placeholder for dynamic updates

        # UI state variables
        static.t = 0.0
        static.selected_fill = 1  # Default: Colormap
        static.solid_color = [0.8, 0.8, 0.2, 0.6]
        static.colormaps = ["Viridis", "Plasma", "Hot", "Cool", "Pink", "Jet",
                            "Twilight", "RdBu", "BrBG", "PiYG", "Spectral", "Greys"]
        static.sel_colormap = 5  # Default: Jet
        static.custom_range = False
        static.range_min = -1.0
        static.range_max = 1.0
        static.flags = implot3d.SurfaceFlags_.none.value

    _, static.flags = checkbox_flag(static.flags, implot3d.SurfaceFlags_.no_lines.value, "NoLines")
    _, static.flags = checkbox_flag(static.flags, implot3d.SurfaceFlags_.no_fill.value, "NoFill")
    _, static.flags = checkbox_flag(static.flags, implot3d.SurfaceFlags_.no_markers.value, "NoMarkers")

    # Update time-dependent Z values
    static.t += imgui.get_io().delta_time
    static.zs[:] = np.sin(2 * static.t + np.sqrt(static.xs ** 2 + static.ys ** 2))

    # UI: Choose fill color
    imgui.text("Fill color")
    imgui.indent()

    # Solid color selection
    if imgui.radio_button("Solid", static.selected_fill == 0):
        static.selected_fill = 0
    if static.selected_fill == 0:
        imgui.same_line()
        _, static.solid_color = imgui.color_edit4("##SurfaceSolidColor", static.solid_color)

    # Colormap selection
    if imgui.radio_button("Colormap", static.selected_fill == 1):
        static.selected_fill = 1
    if static.selected_fill == 1:
        imgui.same_line()
        _, static.sel_colormap = imgui.combo("##SurfaceColormap", static.sel_colormap, static.colormaps)

    imgui.unindent()

    # UI: Custom range selection
    _, static.custom_range = imgui.checkbox("Custom range", static.custom_range)
    imgui.indent()
    if not static.custom_range:
        imgui.begin_disabled()

    _, static.range_min = imgui.slider_float("Range min", static.range_min, -1.0, static.range_max - 0.01)
    _, static.range_max = imgui.slider_float("Range max", static.range_max, static.range_min + 0.01, 1.0)

    if not static.custom_range:
        imgui.end_disabled()
    imgui.unindent()

    # Begin plot
    if static.selected_fill == 1:
        implot3d.push_colormap(static.colormaps[static.sel_colormap])

    if implot3d.begin_plot("Surface Plots", size=(-1, 400), flags=implot3d.Flags_.no_clip):
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1.5, 1.5)
        implot3d.push_style_var(implot3d.StyleVar_.fill_alpha, 0.8)

        spec = implot3d.Spec(line_color=implot3d.get_colormap_color(1), flags=static.flags)

        if static.selected_fill == 0:
            spec.fill_color = ImVec4(*static.solid_color)

        # Plot the surface
        if static.custom_range:
            implot3d.plot_surface("Wave Surface", static.xs, static.ys, static.zs, n, n,
                                  scale_min=float(static.range_min), scale_max=float(static.range_max),
                                    spec=spec)
        else:
            implot3d.plot_surface("Wave Surface", static.xs, static.ys, static.zs, n, n, spec=spec)

        implot3d.pop_style_var()
        implot3d.end_plot()

    if static.selected_fill == 1:
        implot3d.pop_colormap()


def demo_mesh_plots():
    IMGUI_DEMO_MARKER("Plots/Mesh Plots")
    static = demo_mesh_plots

    # Initialize static variables only once
    if not hasattr(static, "mesh_id"):
        static.mesh_id = 0
        static.set_fill_color = True
        static.fill_color = [0.8, 0.8, 0.2, 0.6]
        static.set_line_color = True
        static.line_color = [0.2, 0.2, 0.2, 0.8]
        static.set_marker_color = False
        static.marker_color = [0.2, 0.2, 0.2, 0.8]
        static.mesh_options = ["Duck", "Sphere", "Cube"]

        static.cube_mesh = make_cube_mesh()
        static.sphere_mesh = make_sphere_mesh()
        static.duck_mesh = make_duck_mesh()

    # Mesh selection dropdown
    _, static.mesh_id = imgui.combo("Mesh", static.mesh_id, static.mesh_options)

    # UI: Fill Color
    _, static.set_fill_color = imgui.checkbox("Fill Color", static.set_fill_color)
    if static.set_fill_color:
        imgui.same_line()
        _, static.fill_color = imgui.color_edit4("##MeshFillColor", static.fill_color)

    # UI: Line Color
    _, static.set_line_color = imgui.checkbox("Line Color", static.set_line_color)
    if static.set_line_color:
        imgui.same_line()
        _, static.line_color = imgui.color_edit4("##MeshLineColor", static.line_color)

    # UI: Marker Color
    _, static.set_marker_color = imgui.checkbox("Marker Color", static.set_marker_color)
    if static.set_marker_color:
        imgui.same_line()
        _, static.marker_color = imgui.color_edit4("##MeshMarkerColor", static.marker_color)

    # Begin plot
    if implot3d.begin_plot("Mesh Plots"):
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1, 1)

        spec = implot3d.Spec()

        # Set colors
        if static.set_fill_color:
            spec.fill_color = ImVec4(*static.fill_color)
        else:
            spec.fill_color = ImVec4(0.0, 0.0, 0.0, 0.0)  # Transparent

        if static.set_line_color:
            spec.line_color = ImVec4(*static.line_color)

        if static.set_marker_color:
            # implot3d.set_next_marker_style(
            #     implot3d.Marker_.square, 3, static.marker_color, implot3d.AUTO, static.marker_color
            # )
            spec.marker = implot3d.Marker_.square
            spec.marker_size = 3
            spec.marker_line_color = ImVec4(*static.marker_color)
            spec.marker_fill_color = ImVec4(*static.marker_color)

        # Plot the selected mesh
        if static.mesh_id == 0:
            implot3d.plot_mesh("Duck", static.duck_mesh, spec=spec)
        elif static.mesh_id == 1:
            implot3d.plot_mesh("Sphere", static.sphere_mesh, spec=spec)
        elif static.mesh_id == 2:
            implot3d.plot_mesh("Cube", static.cube_mesh, spec=spec)

        implot3d.end_plot()


def slider_implot3d_point(
        label: str, v: implot3d.Point,
        v_min: float, v_max: float, format: str = "%.3",
        flags: int = 0
) -> tuple[bool, implot3d.Point]:
    as_floats = [v.x, v.y, v.z]
    changed, as_floats = imgui.slider_float3(label, as_floats, v_min, v_max, format, flags)
    return changed, implot3d.Point(as_floats[0], as_floats[1], as_floats[2])


def demo_image_plots():
    IMGUI_DEMO_MARKER("Plots/Image Plots")
    static = demo_image_plots

     # imgui.bullet_text("Below we are displaying the font texture, which is the only texture we have\naccess to in this demo.")
    imgui.bullet_text("Use the 'ImTextureID' type as storage to pass pointers or identifiers to your\nown texture data.")
    imgui.bullet_text("See ImGui Wiki page 'Image Loading and Displaying Examples'.")

    if not hasattr(static, "initialized"):
        static.tint1 = ImVec4(1.0, 1.0, 1.0, 1.0)
        static.tint2 = ImVec4(1.0, 1.0, 1.0, 1.0)

        static.center1 = implot3d.Point(0.0, 0.0, 1.0)
        static.axis_u1 = implot3d.Point(1.0, 0.0, 0.0)
        static.axis_v1 = implot3d.Point(0.0, 1.0, 0.0)
        static.uv0_1 = ImVec2(0.0, 0.0)
        static.uv1_1 = ImVec2(1.0, 1.0)

        static.p0 = implot3d.Point(-1.0, -1.0, 0.0)
        static.p1 = implot3d.Point(1.0, -1.0, 0.0)
        static.p2 = implot3d.Point(1.0, 1.0, 0.0)
        static.p3 = implot3d.Point(-1.0, 1.0, 0.0)

        static.uv0 = ImVec2(0.0, 0.0)
        static.uv1 = ImVec2(1.0, 0.0)
        static.uv2 = ImVec2(1.0, 1.0)
        static.uv3 = ImVec2(0.0, 1.0)

        # Create textures
        # Step 1: create them as numpy arrays
        checker_img = make_checkerboard_texture()
        circle_img = make_gradient_circle_texture()
        # Step 2: convert them to OpenGL textures (using imgui_bundle's immvision)
        from imgui_bundle import immvision
        static.tex_checker = immvision.GlTexture(checker_img)
        static.tex_circle = immvision.GlTexture(circle_img)
        # Step 3: create ImTextureRef from the OpenGL texture id
        static.tex_id_checker = imgui.ImTextureRef(static.tex_checker.texture_id)
        static.tex_id_circle = imgui.ImTextureRef(static.tex_circle.texture_id)

        static.initialized = True

    imgui.dummy((0, 10))  # vertical spacing

    # Image 1 Controls
    if imgui.tree_node_ex("Image 1 Controls: Center + Axes"):
        _, static.center1 = slider_implot3d_point("Center", static.center1, -2.0, 2.0, "%.1f")
        _, static.axis_u1 = slider_implot3d_point("Axis U", static.axis_u1, -2.0, 2.0, "%.1f")
        _, static.axis_v1 = slider_implot3d_point("Axis V", static.axis_v1, -2.0, 2.0, "%.1f")
        _, static.uv0_1 = imgui.slider_float2("UV0", static.uv0_1, 0.0, 1.0, "%.2f")
        _, static.uv1_1 = imgui.slider_float2("UV1", static.uv1_1, 0.0, 1.0, "%.2f")
        _, static.tint1 = imgui.color_edit4("Tint", static.tint1)
        imgui.tree_pop()

    # Image 2 Controls
    if imgui.tree_node_ex("Image 2 Controls: Full Quad"):
        _, static.p0 = slider_implot3d_point("P0", static.p0, -2.0, 2.0, "%.1f")
        _, static.p1 = slider_implot3d_point("P1", static.p1, -2.0, 2.0, "%.1f")
        _, static.p2 = slider_implot3d_point("P2", static.p2, -2.0, 2.0, "%.1f")
        _, static.p3 = slider_implot3d_point("P3", static.p3, -2.0, 2.0, "%.1f")

        _, static.uv0 = imgui.slider_float2("UV0", static.uv0, 0.0, 1.0, "%.2f")
        _, static.uv1 = imgui.slider_float2("UV1", static.uv1, 0.0, 1.0, "%.2f")
        _, static.uv2 = imgui.slider_float2("UV2", static.uv2, 0.0, 1.0, "%.2f")
        _, static.uv3 = imgui.slider_float2("UV3", static.uv3, 0.0, 1.0, "%.2f")

        _, static.tint2 = imgui.color_edit4("Tint##2", static.tint2)
        imgui.tree_pop()

    # tex_id = imgui.ImTextureRef(imgui.get_io().fonts.python_get_texture_id())

    if implot3d.begin_plot("Image Plot", size=(-1, 0), flags=implot3d.Flags_.no_clip):
        implot3d.plot_image("Image 1", static.tex_id_checker,
                            center=static.center1,
                            axis_u=static.axis_u1,
                            axis_v=static.axis_v1,
                            uv0=static.uv0_1,
                            uv1=static.uv1_1,
                            tint_col=static.tint1)

        implot3d.plot_image("Image 2", static.tex_id_circle,
                            p0=static.p0, p1=static.p1, p2=static.p2, p3=static.p3,
                            uv0=static.uv0, uv1=static.uv1, uv2=static.uv2, uv3=static.uv3,
                            tint_col=static.tint2)
        implot3d.end_plot()


def demo_realtime_plots():
    IMGUI_DEMO_MARKER("Plots/Realtime Plots")
    static = demo_realtime_plots

    if not hasattr(static, "t"):
        static.t = 0.0
        static.last_t = -1.0
        static.data_x = CircularBuffer(max_size=2000)
        static.data_y = CircularBuffer(max_size=2000)
        static.data_z = CircularBuffer(max_size=2000)

    imgui.bullet_text("Move your mouse to change the data!")

    if implot3d.begin_plot("Scrolling Plot", size=(-1, 400)):
        static.t += imgui.get_io().delta_time

        # Poll mouse data every 10 ms
        if static.t - static.last_t > 0.01:
            static.last_t = static.t
            mouse_x, mouse_y = imgui.get_mouse_pos()

            if abs(mouse_x) < 1e4 and abs(mouse_y) < 1e4:
                frame_pos = implot3d.internal.get_frame_pos()
                frame_size = implot3d.internal.get_frame_size()
                plot_center_x = frame_pos.x + frame_size.x / 2
                plot_center_y = frame_pos.y + frame_size.y / 2

                static.data_x.add_point(static.t)
                static.data_y.add_point(mouse_x - plot_center_x)
                static.data_z.add_point(mouse_y - plot_center_y)

        implot3d.setup_axes("Time", "Mouse X", "Mouse Y",
                            implot3d.AxisFlags_.no_tick_labels,
                            implot3d.AxisFlags_.no_tick_labels,
                            implot3d.AxisFlags_.no_tick_labels)

        implot3d.setup_axis_limits(implot3d.ImAxis3D_.x, static.t - 10.0, static.t, implot3d.Cond_.always)
        implot3d.setup_axis_limits(implot3d.ImAxis3D_.y, -400, 400, implot3d.Cond_.once)
        implot3d.setup_axis_limits(implot3d.ImAxis3D_.z, -400, 400, implot3d.Cond_.once)

        # Get the valid data to plot
        x_data = static.data_x.get_data()
        y_data = static.data_y.get_data()
        z_data = static.data_z.get_data()

        if len(x_data) > 0:
            implot3d.plot_line("Mouse", x_data, y_data, z_data)

        implot3d.end_plot()


def demo_plot_flags():
    IMGUI_DEMO_MARKER("Plots/Plot Flags")
    static = demo_plot_flags

    if not hasattr(static, "flags"):
        static.flags = implot3d.Flags_.none.value

    flag_info = [
        (implot3d.Flags_.no_title, "Hide plot title"),
        (implot3d.Flags_.no_legend, "Hide plot legend"),
        (implot3d.Flags_.no_mouse_text, "Hide mouse position in plot coordinates"),
        (implot3d.Flags_.no_clip, "Disable 3D box clipping"),
        (implot3d.Flags_.no_menus, "The user will not be able to open context menus"),
        (implot3d.Flags_.equal, "X, Y, and Z axes will be constrained to have the same units/pixel"),
        (implot3d.Flags_.no_rotate, "Lock rotation interaction"),
        (implot3d.Flags_.no_pan, "Lock panning/translation interaction"),
        (implot3d.Flags_.no_zoom, "Lock zooming interaction"),
        (implot3d.Flags_.no_inputs, "Disable all user inputs"),
    ]

    for flag, tooltip in flag_info:
        _, static.flags = imgui.checkbox_flags(str(flag.name), static.flags, flag.value)
        imgui.same_line()
        help_marker(tooltip)

    if implot3d.begin_plot("Plot Flags Demo", size=(-1, 0), flags=static.flags):
        implot3d.setup_axes("X-axis", "Y-axis", "Z-axis")
        implot3d.setup_axes_limits(-10, 10, -10, 10, -5, 5)

        if not hasattr(static, "helix_x"):
            static.helix_x = np.zeros(100, dtype=np.float32)
            static.helix_y = np.zeros(100, dtype=np.float32)
            static.helix_z = np.zeros(100, dtype=np.float32)
            for i in range(100):
                t = i * 0.1
                static.helix_x[i] = 3.0 * np.cos(t)
                static.helix_y[i] = 3.0 * np.sin(t)
                static.helix_z[i] = t - 5.0

        implot3d.plot_line("Helix", static.helix_x, static.helix_y, static.helix_z)

        scatter_x = np.array([-10, 10, -10, 10, -10, 10, -10, 10], dtype=np.float32)
        scatter_y = np.array([-10, -10, 10, 10, -10, -10, 10, 10], dtype=np.float32)
        scatter_z = np.array([-5, -5, -5, -5, 5, 5, 5, 5], dtype=np.float32)
        implot3d.plot_scatter("Cube corners", scatter_x, scatter_y, scatter_z)

        implot3d.end_plot()


def demo_offset_and_stride():
    IMGUI_DEMO_MARKER("Plots/Offset and Stride")
    static = demo_offset_and_stride

    k_spirals = 11
    k_points_per = 50

    if not hasattr(static, "offset"):
        static.offset = 0
        # Build interleaved data once: [s0.x0 s0.y0 s0.z0 ... sn.x0 sn.y0 sn.z0 s0.x1 ...]
        static.interleaved = np.zeros(3 * k_points_per * k_spirals, dtype=np.float64)
        for p in range(k_points_per):
            for s in range(k_spirals):
                r = s / (k_spirals - 1) * 0.2 + 0.2
                theta = p / k_points_per * 6.28
                static.interleaved[p * 3 * k_spirals + 3 * s + 0] = 0.5 + r * np.cos(theta)
                static.interleaved[p * 3 * k_spirals + 3 * s + 1] = 0.5 + r * np.sin(theta)
                static.interleaved[p * 3 * k_spirals + 3 * s + 2] = 0.5 + 0.5 * np.sin(2.0 * theta)

    imgui.bullet_text("Offsetting is useful for realtime plots (see above) and circular buffers.")
    imgui.bullet_text("Striding is useful for interleaved data (e.g. audio) or plotting structs.")
    imgui.bullet_text("Here, all spiral data is stored in a single interleaved buffer:")
    imgui.bullet_text("[s0.x0 s0.y0 s0.z0 ... sn.x0 sn.y0 sn.z0 s0.x1 s0.y1 s0.z1 ... sn.x1 sn.y1 sn.z1 ... sn.xm sn.ym sn.zm]")
    imgui.bullet_text("The offset value indicates which spiral point index is considered the first.")
    imgui.bullet_text("Offsets can be negative and/or larger than the actual data count.")
    _, static.offset = imgui.slider_int("Offset", static.offset, -2 * k_points_per, 2 * k_points_per)

    if implot3d.begin_plot("##strideoffset", size=(-1, 0)):
        implot3d.push_colormap(implot3d.Colormap_.jet)
        for s in range(k_spirals):
            label = f"Spiral {s}"
            # Extract x, y, z for this spiral from the interleaved buffer
            # Note: Python bindings require contiguous arrays, so we extract slices with .copy()
            # In C++, spec.Stride would be used: 3 * k_spirals * sizeof(double)
            stride_elements = 3 * k_spirals
            xs = static.interleaved[s * 3 + 0 :: stride_elements][:k_points_per].copy()
            ys = static.interleaved[s * 3 + 1 :: stride_elements][:k_points_per].copy()
            zs = static.interleaved[s * 3 + 2 :: stride_elements][:k_points_per].copy()

            spec = implot3d.Spec(offset=static.offset)
            # spec.stride is not used here because we pass contiguous arrays (extracted via slicing)
            # The C++ version would set spec.Stride = 3 * k_spirals * sizeof(double)

            implot3d.plot_line(label, xs, ys, zs, spec=spec)
        implot3d.end_plot()
        implot3d.pop_colormap()


def demo_legend_options():
    IMGUI_DEMO_MARKER("Plots/Legend Options")
    static = demo_legend_options

    if not hasattr(static, "loc"):
        static.loc = implot3d.Location_.east.value
        static.flags = 0

    _, static.loc = imgui.checkbox_flags("North", static.loc, implot3d.Location_.north.value)
    imgui.same_line()
    _, static.loc = imgui.checkbox_flags("South", static.loc, implot3d.Location_.south.value)
    imgui.same_line()
    _, static.loc = imgui.checkbox_flags("West", static.loc, implot3d.Location_.west.value)
    imgui.same_line()
    _, static.loc = imgui.checkbox_flags("East", static.loc, implot3d.Location_.east.value)

    _, static.flags = imgui.checkbox_flags("ImPlot3DLegendFlags_Horizontal", static.flags, implot3d.LegendFlags_.horizontal.value)
    imgui.same_line()
    help_marker("Legend entries will be displayed horizontally")

    _, static.flags = imgui.checkbox_flags("ImPlot3DLegendFlags_NoButtons", static.flags, implot3d.LegendFlags_.no_buttons.value)
    imgui.same_line()
    help_marker("Legend icons will not function as hide/show buttons")

    _, static.flags = imgui.checkbox_flags("ImPlot3DLegendFlags_NoHighlightItem", static.flags, implot3d.LegendFlags_.no_highlight_item.value)
    imgui.same_line()
    help_marker("Plot items will not be highlighted when their legend entry is hovered")

    style = implot3d.get_style()
    changed, val = imgui.slider_float2("LegendPadding", style.legend_padding, 0.0, 20.0, "%.0f")
    if changed:
        style.legend_padding = ImVec2(val[0], val[1])
    changed, val = imgui.slider_float2("LegendInnerPadding", style.legend_inner_padding, 0.0, 10.0, "%.0f")
    if changed:
        style.legend_inner_padding = ImVec2(val[0], val[1])
    changed, val = imgui.slider_float2("LegendSpacing", style.legend_spacing, 0.0, 5.0, "%.0f")
    if changed:
        style.legend_spacing = ImVec2(val[0], val[1])

    if implot3d.begin_plot("Legend Options Demo", size=(-1, 0)):
        implot3d.setup_axes("X-Axis", "Y-Axis", "Z-Axis")
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1, 1)
        implot3d.setup_legend(static.loc, static.flags)

        t = imgui.get_time() * 0.5
        count = 50
        xs1 = np.zeros(count, dtype=np.float32)
        ys1 = np.zeros(count, dtype=np.float32)
        zs1 = np.zeros(count, dtype=np.float32)
        xs2 = np.zeros(count, dtype=np.float32)
        ys2 = np.zeros(count, dtype=np.float32)
        zs2 = np.zeros(count, dtype=np.float32)
        xs3 = np.zeros(count, dtype=np.float32)
        ys3 = np.zeros(count, dtype=np.float32)
        zs3 = np.zeros(count, dtype=np.float32)

        for i in range(count):
            phase = i * 0.1 + t
            xs1[i] = 0.8 * np.cos(phase)
            ys1[i] = 0.8 * np.sin(phase)
            zs1[i] = 0.5 * np.sin(phase * 2)
            xs2[i] = 0.6 * np.cos(phase + 1.0)
            ys2[i] = 0.6 * np.sin(phase + 1.0)
            zs2[i] = -0.3 * np.cos(phase * 1.5)
            xs3[i] = 0.4 * np.sin(phase)
            ys3[i] = 0.4 * np.cos(phase)
            zs3[i] = 0.7 * np.cos(phase * 0.8)

        implot3d.plot_line("Helix A", xs1, ys1, zs1)
        implot3d.plot_line("Helix B##IDText", xs2, ys2, zs2)
        implot3d.plot_line("##NotListed", xs3, ys3, zs3)

        implot3d.end_plot()


def demo_markers_and_text():
    IMGUI_DEMO_MARKER("Plots/Markers and Text")
    static = demo_markers_and_text

    # Initialize static variables only once
    if not hasattr(static, "mk_size"):
        static.mk_size = implot3d.get_style().marker_size
        static.mk_weight = implot3d.get_style().line_weight

    # UI Controls for marker size and weight
    _, static.mk_size = imgui.drag_float("Marker Size", static.mk_size, 0.1, 2.0, 10.0, "%.2f px")
    _, static.mk_weight = imgui.drag_float("Marker Weight", static.mk_weight, 0.05, 0.5, 3.0, "%.2f px")

    if implot3d.begin_plot("##MarkerStyles", size=(-1, 0), flags=implot3d.Flags_.canvas_only):
        implot3d.setup_axes("", "", "",
                            implot3d.AxisFlags_.no_decorations,
                            implot3d.AxisFlags_.no_decorations,
                            implot3d.AxisFlags_.no_decorations)

        implot3d.setup_axes_limits(-0.5, 1.5, -0.5, 1.5, 0, float(implot3d.Marker_.count) + 1)

        xs = np.zeros(2, dtype=np.float32)
        ys = np.zeros(2, dtype=np.float32)
        zs = np.array([implot3d.Marker_.count, implot3d.Marker_.count + 1], dtype=np.float32)

        # Filled markers
        for m in range(implot3d.Marker_.count):
            angle = (zs[0] / float(implot3d.Marker_.count)) * 2 * np.pi
            xs[1] = xs[0] + np.cos(angle) * 0.5
            ys[1] = ys[0] + np.sin(angle) * 0.5

            with imgui_ctx.push_id(str(m)):
                implot3d.plot_line("##Filled", xs, ys, zs,
                                   spec=implot3d.Spec(
                                        marker=m,
                                        marker_size=static.mk_size,
                                        line_weight=static.mk_weight
                                       )
                                   )

            zs -= 1  # Move markers down in Z axis

        xs[0], ys[0] = 1, 1
        zs[:] = [implot3d.Marker_.count, implot3d.Marker_.count + 1]

        # Open markers
        for m in range(implot3d.Marker_.count):
            angle = (zs[0] / float(implot3d.Marker_.count)) * 2 * np.pi
            xs[1] = xs[0] + np.cos(angle) * 0.5
            ys[1] = ys[0] - np.sin(angle) * 0.5

            with imgui_ctx.push_id(str(m)):
                implot3d.plot_line("##Open", xs, ys, zs,
                                   spec=implot3d.Spec(
                                        marker=m,
                                        marker_size=static.mk_size,
                                        line_weight=static.mk_weight,
                                        marker_fill_color=ImVec4(0, 0, 0, 0)
                                       )
                                   )

            zs -= 1  # Move markers down in Z axis

        # Add plot text
        implot3d.plot_text("Filled Markers", 0.0, 0.0, 6.0)
        implot3d.plot_text("Open Markers", 1.0, 1.0, 6.0)

        # Inlay text with color
        implot3d.push_style_color(implot3d.Col_.inlay_text, [1, 0, 1, 1])
        implot3d.plot_text("Rotated Text", 0.5, 0.5, 6.0, np.pi / 4, (0, 0))
        implot3d.pop_style_color()

        implot3d.end_plot()


def demo_nan_values():
    IMGUI_DEMO_MARKER("Plots/NaN Values")
    static = demo_nan_values

    # Initialize static variables only once
    if not hasattr(static, "include_nan"):
        static.include_nan = True
        static.flags = 0

    # Data arrays (initialized fresh each frame to handle NaN updates)
    data1 = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)
    data2 = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)
    data3 = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)

    if static.include_nan:
        data1[2] = np.nan  # Insert NaN at index 2

    # UI: Controls for NaN handling
    _, static.include_nan = imgui.checkbox("Include NaN", static.include_nan)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("Skip NaN", static.flags, implot3d.LineFlags_.skip_nan)

    # Begin plot
    if implot3d.begin_plot("##NaNValues"):
        # implot3d.set_next_marker_style(implot3d.Marker_.square)
        implot3d.plot_line("Line", data1, data2, data3, spec=implot3d.Spec(
            flags=static.flags, marker=implot3d.Marker_.square))
        implot3d.end_plot()


#-----------------------------------------------------------------------------
# [SECTION] Axes
#-----------------------------------------------------------------------------

def demo_box_scale():
    IMGUI_DEMO_MARKER("Axes/Box Scale")
    static = demo_box_scale

    # Constants
    n = 100

    # Generate curve data
    t = np.linspace(0, 1, n, dtype=np.float32)
    xs = np.sin(t * 2.0 * np.pi)
    ys = np.cos(t * 4.0 * np.pi)
    zs = t * 2.0 - 1.0

    # Initialize scale factors
    if not hasattr(static, "scale"):
        static.scale = [1.0, 1.0, 1.0]

    # UI: Adjust box scale
    _, static.scale = imgui.slider_float3("Box Scale", static.scale, 0.1, 2.0, "%.2f")

    if implot3d.begin_plot("##BoxScale"):
        implot3d.setup_box_scale(*static.scale)
        implot3d.plot_line("3D Curve", xs, ys, zs)
        implot3d.end_plot()


def demo_box_rotation():
    IMGUI_DEMO_MARKER("Axes/Box Rotation")
    static = demo_box_rotation

    # Initialize state variables
    if not hasattr(static, "elevation"):
        static.elevation = 45.0
        static.azimuth = -135.0
        static.animate = False
        static.init_elevation = 45.0
        static.init_azimuth = -135.0

    # UI: Rotation Controls
    imgui.text("Rotation")
    changed = False

    _, static.elevation = imgui.slider_float("Elevation", static.elevation, -90.0, 90.0, "%.1f degrees")
    _, static.azimuth = imgui.slider_float("Azimuth", static.azimuth, -180.0, 180.0, "%.1f degrees")
    _, static.animate = imgui.checkbox("Animate", static.animate)

    if imgui.is_item_edited():
        changed = True

    imgui.text("Initial Rotation")
    imgui.same_line()
    help_marker("The rotation will be reset to the initial rotation when you double right-click")

    _, static.init_elevation = imgui.slider_float("Initial Elevation", static.init_elevation, -90.0, 90.0, "%.1f degrees")
    _, static.init_azimuth = imgui.slider_float("Initial Azimuth", static.init_azimuth, -180.0, 180.0, "%.1f degrees")

    if implot3d.begin_plot("##BoxRotation"):
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1, 1, implot3d.Cond_.always)

        # Set initial rotation
        implot3d.setup_box_initial_rotation(static.init_elevation, static.init_azimuth)

        # Set the rotation using the specified elevation and azimuth
        if changed:
            implot3d.setup_box_rotation(static.elevation, static.azimuth, static.animate, implot3d.Cond_.always)

        # Define axes lines
        origin = np.array([0.0, 0.0], dtype=np.float32)
        x_axis = np.array([0.0, 1.0], dtype=np.float32)

        # Plot axis lines
        spec = implot3d.Spec(line_color=ImVec4(0.8, 0.2, 0.2, 1))
        implot3d.plot_line("X-Axis", x_axis, origin, origin, spec=spec)
        implot3d.plot_line("Y-Axis", origin, x_axis, origin, spec=spec)
        implot3d.plot_line("Z-Axis", origin, origin, x_axis, spec=spec)

        implot3d.end_plot()


def demo_log_scale():
    IMGUI_DEMO_MARKER("Axes/Log Scale")
    xs = np.arange(1001) * 0.1
    ys1 = np.sin(xs) + 1
    ys2 = np.log(np.maximum(xs, 1e-10))  # avoid log(0)
    ys3 = np.power(10.0, xs)
    zs = np.zeros(1001, dtype=np.float64)

    if implot3d.begin_plot("Log Plot 3D", size=(-1, 0)):
        implot3d.setup_axis_scale(implot3d.ImAxis3D_.x, implot3d.Scale_.log10)
        implot3d.setup_axes_limits(0.1, 100, 0, 10, -1, 1)
        implot3d.plot_line("f(x) = x", xs, xs, zs)
        implot3d.plot_line("f(x) = sin(x)+1", xs, ys1, zs)
        implot3d.plot_line("f(x) = log(x)", xs, ys2, zs)
        implot3d.plot_line("f(x) = 10^x", xs[:21], ys3[:21], zs[:21])
        implot3d.end_plot()


def demo_symmetric_log_scale():
    IMGUI_DEMO_MARKER("Axes/Symmetric Log Scale")
    xs = np.arange(1001) * 0.1 - 50
    ys1 = np.sin(xs)
    ys2 = np.arange(1001) * 0.002 - 1
    zs = np.zeros(1001, dtype=np.float64)

    if implot3d.begin_plot("SymLog Plot", size=(-1, 0)):
        implot3d.setup_axis_scale(implot3d.ImAxis3D_.x, implot3d.Scale_.sym_log)
        implot3d.plot_line("f(x) = a*x+b", xs, ys2, zs)
        implot3d.plot_line("f(x) = sin(x)", xs, ys1, zs)
        implot3d.end_plot()


def demo_tick_labels():
    IMGUI_DEMO_MARKER("Axes/Tick Labels")
    static = demo_tick_labels
    if not hasattr(static, "custom_ticks"):
        static.custom_ticks = True
        static.custom_labels = True

    _, static.custom_ticks = imgui.checkbox("Show Custom Ticks", static.custom_ticks)
    if static.custom_ticks:
        imgui.same_line()
        _, static.custom_labels = imgui.checkbox("Show Custom Labels", static.custom_labels)

    pi_list = [3.14]
    pi_str_list = ["PI"]
    letters_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    letters_labels = ["A", "B", "C", "D", "E", "F"]

    if implot3d.begin_plot("##Ticks"):
        implot3d.setup_axes_limits(2, 5, 0, 1, 0, 1)
        if static.custom_ticks:
            implot3d.setup_axis_ticks(axis = implot3d.ImAxis3D_.x, values=pi_list, labels = pi_str_list if static.custom_labels else [], keep_default=True)
            implot3d.setup_axis_ticks(axis = implot3d.ImAxis3D_.y, values=letters_ticks, labels = letters_labels if static.custom_labels else [], keep_default=False)
            implot3d.setup_axis_ticks(axis = implot3d.ImAxis3D_.z, v_min=0, v_max=1, n_ticks=6, labels = letters_labels if static.custom_labels else [], keep_default=False)
        implot3d.end_plot()


def demo_axis_constraints():
    IMGUI_DEMO_MARKER("Axes/Axis Constraints")
    static = demo_axis_constraints

    if not hasattr(static, "limit_constraints"):
        static.limit_constraints = [-10.0, 10.0]
        static.zoom_constraints = [1.0, 20.0]
        static.flags = 0

    changed, val = imgui.drag_float2("Limits Constraints", static.limit_constraints, 0.01)
    if changed:
        static.limit_constraints = [val[0], val[1]]
    changed, val = imgui.drag_float2("Zoom Constraints", static.zoom_constraints, 0.01)
    if changed:
        static.zoom_constraints = [val[0], val[1]]
    _, static.flags = imgui.checkbox_flags("ImPlot3DAxisFlags_PanStretch", static.flags, implot3d.AxisFlags_.pan_stretch.value)

    if implot3d.begin_plot("##AxisConstraints", size=(-1, 0)):
        implot3d.setup_axes("X", "Y", "Z", static.flags, static.flags, static.flags)
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1, 1)
        for axis in [implot3d.ImAxis3D_.x, implot3d.ImAxis3D_.y, implot3d.ImAxis3D_.z]:
            implot3d.setup_axis_limits_constraints(axis, static.limit_constraints[0], static.limit_constraints[1])
            implot3d.setup_axis_zoom_constraints(axis, static.zoom_constraints[0], static.zoom_constraints[1])
        implot3d.end_plot()


def demo_equal_axes():
    IMGUI_DEMO_MARKER("Axes/Equal Axes")
    static = demo_equal_axes

    imgui.bullet_text("Equal constraint applies to all three axes (X, Y, Z)")
    imgui.bullet_text("When enabled, the axes maintain the same units/pixel ratio")

    if not hasattr(static, "circle_xs"):
        angles = np.linspace(0, 2 * np.pi, 360)
        static.circle_xs = np.cos(angles)
        static.circle_ys = np.sin(angles)
        static.circle_zs = np.zeros(360, dtype=np.float64)
        static.helix_xs = 0.5 * np.cos(angles)
        static.helix_ys = 0.5 * np.sin(angles)
        static.helix_zs = np.linspace(-1, 1, 360)
        static.flags = implot3d.Flags_.equal.value

    square_xs = np.array([-0.5, 0.5, 0.5, -0.5, -0.5], dtype=np.float32)
    square_ys = np.array([-0.5, -0.5, 0.5, 0.5, -0.5], dtype=np.float32)
    square_zs = np.array([-0.5, -0.5, -0.5, -0.5, -0.5], dtype=np.float32)

    _, static.flags = imgui.checkbox_flags("ImPlot3DFlags_Equal", static.flags, implot3d.Flags_.equal.value)

    if implot3d.begin_plot("##EqualAxes", size=(-1, 0), flags=static.flags):
        implot3d.setup_axes("X-Axis", "Y-Axis", "Z-Axis")
        implot3d.plot_line("Circle", static.circle_xs, static.circle_ys, static.circle_zs)
        implot3d.plot_line("Helix", static.helix_xs, static.helix_ys, static.helix_zs)
        implot3d.plot_line("Square", square_xs, square_ys, square_zs)
        implot3d.end_plot()


def demo_auto_fitting_data():
    IMGUI_DEMO_MARKER("Axes/Auto-Fitting Data")
    static = demo_auto_fitting_data

    imgui.bullet_text("Axes can be configured to auto-fit to data extents.")
    imgui.bullet_text("Try panning and zooming to see the axes adjust.")
    imgui.bullet_text("Disable AutoFit on an axis to fix its range.")

    if not hasattr(static, "xflags"):
        static.xflags = implot3d.AxisFlags_.none.value
        static.yflags = implot3d.AxisFlags_.none.value
        static.zflags = implot3d.AxisFlags_.auto_fit.value
        static.data_x = np.arange(101) * 0.1
        static.data_y = np.arange(101) * 0.1
        static.data_z = 1 + np.sin(np.arange(101) / 10.0)

    imgui.text_unformatted("X: ")
    imgui.same_line()
    _, static.xflags = imgui.checkbox_flags("ImPlot3DAxisFlags_AutoFit##X", static.xflags, implot3d.AxisFlags_.auto_fit.value)

    imgui.text_unformatted("Y: ")
    imgui.same_line()
    _, static.yflags = imgui.checkbox_flags("ImPlot3DAxisFlags_AutoFit##Y", static.yflags, implot3d.AxisFlags_.auto_fit.value)

    imgui.text_unformatted("Z: ")
    imgui.same_line()
    _, static.zflags = imgui.checkbox_flags("ImPlot3DAxisFlags_AutoFit##Z", static.zflags, implot3d.AxisFlags_.auto_fit.value)

    if implot3d.begin_plot("##AutoFitting"):
        implot3d.setup_axes("X-Axis", "Y-Axis", "Z-Axis", static.xflags, static.yflags, static.zflags)
        implot3d.plot_line("Wave", static.data_x, static.data_y, static.data_z)
        implot3d.end_plot()


#-----------------------------------------------------------------------------
# [SECTION] Tools
#-----------------------------------------------------------------------------

def demo_mouse_picking():
    IMGUI_DEMO_MARKER("Tools/Mouse Picking")
    static = demo_mouse_picking

    if not hasattr(static, "points"):
        static.points: list[implot3d.Point] = []
        static.rays: list[implot3d.Ray] = []
        static.selected_plane = implot3d.ImPlane3D_.xy.value
        static.mask_plane = True

    imgui.bullet_text("Click anywhere in the plot to place points/rays.")

    _, static.selected_plane = imgui.radio_button("XY-Plane", static.selected_plane, implot3d.ImPlane3D_.xy.value)
    imgui.same_line()
    _, static.selected_plane = imgui.radio_button("XZ-Plane", static.selected_plane, implot3d.ImPlane3D_.xz.value)
    imgui.same_line()
    _, static.selected_plane = imgui.radio_button("YZ-Plane", static.selected_plane, implot3d.ImPlane3D_.yz.value)

    _, static.mask_plane = imgui.checkbox("Mask Plane", static.mask_plane)
    if imgui.button("Clear"):
        static.points.clear()
        static.rays.clear()

    if implot3d.begin_plot("Mouse Picking", size=(-1, 0), flags=implot3d.Flags_.no_clip.value):
        implot3d.setup_axes("X-Axis", "Y-Axis", "Z-Axis")
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1, 1)

        mouse_pos = imgui.get_mouse_pos()
        ray = implot3d.pixels_to_plot_ray(mouse_pos)
        plane = implot3d.ImPlane3D_(static.selected_plane)
        point = implot3d.pixels_to_plot_plane(mouse_pos, plane, static.mask_plane)

        # Show intersection point
        if imgui.is_item_hovered() and not point.is_nan():
            spec = implot3d.Spec(marker=implot3d.Marker_.circle, marker_size=5, marker_fill_color=ImVec4(1, 1, 0, 1))
            px = np.array([point.x], dtype=np.float64)
            py = np.array([point.y], dtype=np.float64)
            pz = np.array([point.z], dtype=np.float64)
            implot3d.plot_scatter("##Intersection", px, py, pz, spec=spec)

        # Add point/ray on click
        if imgui.is_item_hovered() and imgui.is_mouse_clicked(0) and not point.is_nan():
            static.points.append(point)
            static.rays.append(ray)

        # Draw all placed points
        if len(static.points) > 0:
            pts_x = np.array([p.x for p in static.points], dtype=np.float64)
            pts_y = np.array([p.y for p in static.points], dtype=np.float64)
            pts_z = np.array([p.z for p in static.points], dtype=np.float64)

            spec = implot3d.Spec(marker=implot3d.Marker_.circle, marker_size=3)
            implot3d.plot_scatter("Placed Points", pts_x, pts_y, pts_z, spec=spec)

        # Draw all placed rays
        if len(static.rays) > 0:
            ray_xs = []
            ray_ys = []
            ray_zs = []
            for i in range(len(static.rays)):
                p1 = static.points[i]
                p2 = static.points[i] - static.rays[i].direction
                ray_xs.extend([p1.x, p2.x])
                ray_ys.extend([p1.y, p2.y])
                ray_zs.extend([p1.z, p2.z])
            implot3d.plot_line("Placed Rays",
                               np.array(ray_xs, dtype=np.float64),
                               np.array(ray_ys, dtype=np.float64),
                               np.array(ray_zs, dtype=np.float64),
                               spec = implot3d.Spec(flags=implot3d.LineFlags_.segments),
                               )

        implot3d.end_plot()


#-----------------------------------------------------------------------------
# [SECTION] Custom
#-----------------------------------------------------------------------------

def demo_custom_styles():
    IMGUI_DEMO_MARKER("Custom/Custom Styles")
    # Apply Seaborn style
    import copy
    implot3d.push_colormap(implot3d.Colormap_.deep)
    backup_style = copy.copy(implot3d.get_style())
    style_seaborn()

    if implot3d.begin_plot("Seaborn Style"):
        implot3d.setup_axes("X-axis", "Y-axis", "Z-axis")
        implot3d.setup_axes_limits(-0.5, 9.5, -0.5, 0.5, 0, 10)

        # Define data points
        xs = np.linspace(0, 9, 10, dtype=np.uint)
        ys = np.zeros(10, dtype=np.uint)
        lin = np.array([8, 8, 9, 7, 8, 8, 8, 9, 7, 8], dtype=np.uint)
        dot = np.array([7, 6, 6, 7, 8, 5, 6, 5, 8, 7], dtype=np.uint)

        # Skip first colormap color (blue)
        implot3d.next_colormap_color()
        implot3d.plot_line("Line", xs, ys, lin)

        # Skip second colormap color (green)
        implot3d.next_colormap_color()
        implot3d.plot_scatter("Scatter", xs, ys, dot)

        implot3d.end_plot()

    # Restore previous style
    implot3d.set_style(backup_style)
    implot3d.pop_colormap()


def demo_custom_rendering():

    IMGUI_DEMO_MARKER("Custom/Custom Rendering")
    if implot3d.begin_plot("##CustomRend"):
        implot3d.setup_axes_limits(-0.1, 1.1, -0.1, 1.1, -0.1, 1.1)

        # Draw circle
        center = implot3d.plot_to_pixels(implot3d.Point(0.5, 0.5, 0.5))
        draw_list = implot3d.get_plot_draw_list()
        draw_list.add_circle_filled(center, 20, IM_COL32(255, 255, 0, 255), 20)

        # Define box corners
        corners = [
            implot3d.Point(0, 0, 0), implot3d.Point(1, 0, 0),
            implot3d.Point(1, 1, 0), implot3d.Point(0, 1, 0),
            implot3d.Point(0, 0, 1), implot3d.Point(1, 0, 1),
            implot3d.Point(1, 1, 1), implot3d.Point(0, 1, 1)
        ]
        corners_px = [implot3d.plot_to_pixels(c) for c in corners]

        col = IM_COL32(128, 0, 255, 255)
        for i in range(4):
            draw_list.add_line(corners_px[i], corners_px[(i + 1) % 4], col)
            draw_list.add_line(corners_px[i + 4], corners_px[(i + 1) % 4 + 4], col)
            draw_list.add_line(corners_px[i], corners_px[i + 4], col)

        implot3d.end_plot()

#-----------------------------------------------------------------------------
# [SECTION] User Namespace Implementation
#-----------------------------------------------------------------------------

def style_seaborn():
    style = implot3d.get_style()
    style.set_color(implot3d.Col_.frame_bg, ImVec4(1.00, 1.00, 1.00, 1.00))
    style.set_color(implot3d.Col_.plot_bg, ImVec4(0.92, 0.92, 0.95, 1.00))
    style.set_color(implot3d.Col_.plot_border, ImVec4(0.00, 0.00, 0.00, 0.00))
    style.set_color(implot3d.Col_.legend_bg, ImVec4(0.92, 0.92, 0.95, 1.00))
    style.set_color(implot3d.Col_.legend_border, ImVec4(0.80, 0.81, 0.85, 1.00))
    style.set_color(implot3d.Col_.legend_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color(implot3d.Col_.title_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color(implot3d.Col_.inlay_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color(implot3d.Col_.axis_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color(implot3d.Col_.axis_grid, ImVec4(1.00, 1.00, 1.00, 1.00))

    style.line_weight = 1.5
    style.marker = implot3d.Marker_.none
    style.marker_size = 4
    style.fill_alpha = 1.0
    style.plot_padding = ImVec2(12, 12)
    style.label_padding = ImVec2(5, 5)
    style.legend_padding = ImVec2(5, 5)
    style.plot_min_size = ImVec2(300, 225)


def demo_custom_overlay():
    IMGUI_DEMO_MARKER("Custom/Custom Overlay")
    static = demo_custom_overlay

    imgui.bullet_text("Demonstrates custom 2D overlays using GetPlotRectPos/GetPlotRectSize.")
    imgui.bullet_text("Shows mouse tooltip, line to closest point.")

    if not hasattr(static, "xs"):
        np.random.seed(0)
        static.xs = np.random.rand(50).astype(np.float32)
        static.ys = np.random.rand(50).astype(np.float32)
        static.zs = np.random.rand(50).astype(np.float32)

    if implot3d.begin_plot("##CustomOverlay", size=(-1, 0)):
        implot3d.setup_axes("X-Axis", "Y-Axis", "Z-Axis")
        implot3d.setup_axes_limits(0, 1, 0, 1, 0, 1)
        implot3d.plot_scatter("Data", static.xs, static.ys, static.zs)

        draw_list = implot3d.get_plot_draw_list()
        mouse_pos = imgui.get_mouse_pos()
        is_hovered = imgui.is_item_hovered()

        if is_hovered:
            # Find closest point to mouse in screen space
            closest_idx = -1
            min_dist_sq = 1e10
            closest_px = ImVec2(0, 0)

            for i in range(50):
                point_px = implot3d.plot_to_pixels(float(static.xs[i]), float(static.ys[i]), float(static.zs[i]))
                dx = point_px.x - mouse_pos.x
                dy = point_px.y - mouse_pos.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_idx = i
                    closest_px = point_px

            # Draw line to closest point
            if closest_idx >= 0:
                draw_list.add_line(mouse_pos, closest_px, IM_COL32(255, 255, 0, 255), 2.0)

                imgui.begin_tooltip()
                imgui.text(f"Mouse: ({mouse_pos.x:.1f}, {mouse_pos.y:.1f})")
                imgui.text(f"Closest Point #{closest_idx}")
                imgui.text(f"Position: ({static.xs[closest_idx]:.3f}, {static.ys[closest_idx]:.3f}, {static.zs[closest_idx]:.3f})")
                imgui.text(f"Distance: {np.sqrt(min_dist_sq):.1f} px")
                imgui.end_tooltip()

        implot3d.end_plot()


def demo_custom_per_point_style():
    IMGUI_DEMO_MARKER("Custom/Custom Per-Point Style")
    static = demo_custom_per_point_style

    imgui.bullet_text("Demonstrates per-point coloring using colormap sampling.")
    imgui.bullet_text("Each point calls SetNextMarkerStyle with a sampled color.")
    imgui.bullet_text("All points share the same label for a single legend entry.")

    if not hasattr(static, "marker_size"):
        static.marker_size = 4.0
        static.cmap = implot3d.Colormap_.viridis.value

    _, static.marker_size = imgui.slider_float("Marker Size", static.marker_size, 2.0, 10.0)
    if imgui.begin_combo("Colormap", implot3d.get_colormap_name(static.cmap)):
        for i in range(implot3d.get_colormap_count()):
            if imgui.selectable(implot3d.get_colormap_name(i), static.cmap == i)[0]:
                static.cmap = i
        imgui.end_combo()

    # Generate three stacked toruses with different color patterns
    if not hasattr(static, "torus_data"):
        R = 0.6  # Major radius
        r = 0.2  # Minor radius
        u_samples = 20
        v_samples = 20
        static.torus_data = np.zeros((3, 400, 4), dtype=np.float32)

        for torus in range(3):
            z_offset = (2 - torus) * 0.6
            idx = 0
            for i in range(u_samples):
                u = i / u_samples * 2.0 * np.pi
                for j in range(v_samples):
                    v = j / v_samples * 2.0 * np.pi
                    x = (R + r * np.cos(v)) * np.cos(u)
                    y = (R + r * np.cos(v)) * np.sin(u)
                    z = r * np.sin(v) + z_offset

                    if torus == 0:
                        t = (z - (z_offset - r)) / (2.0 * r)
                    elif torus == 1:
                        t = (np.cos(v) + 1.0) / 2.0
                    else:
                        t = (np.cos(u) + 1.0) / 2.0

                    static.torus_data[torus, idx] = [x, y, z, t]
                    idx += 1

    if implot3d.begin_plot("##PerPointStyle", size=(-1, 0)):
        implot3d.setup_axes("X", "Y", "Z")
        implot3d.setup_axes_limits(-1, 1, -1, 1, -0.5, 1.5)

        labels = ["Height-colored", "Radial-colored", "Angular-colored"]
        legend_colors = [
            ImVec4(1.0, 0.0, 0.0, 1.0),
            ImVec4(0.0, 1.0, 0.0, 1.0),
            ImVec4(0.0, 0.0, 1.0, 1.0),
        ]

        for torus in range(3):
            point_count = 400
            for i in range(point_count):
                x = float(static.torus_data[torus, i, 0])
                y = float(static.torus_data[torus, i, 1])
                z = float(static.torus_data[torus, i, 2])
                t = float(static.torus_data[torus, i, 3])

                color = implot3d.sample_colormap(t, static.cmap)
                spec = implot3d.Spec(marker=implot3d.Marker_.circle, marker_size=static.marker_size, marker_fill_color=color)
                implot3d.plot_scatter(labels[torus],
                                      np.array([x], dtype=np.float32),
                                      np.array([y], dtype=np.float32),
                                      np.array([z], dtype=np.float32), spec=spec)
            # Override legend color with PlotDummy
            implot3d.plot_dummy(labels[torus], spec=implot3d.Spec(line_color=legend_colors[torus]))

        implot3d.end_plot()


#-----------------------------------------------------------------------------
# [SECTION] Config
#-----------------------------------------------------------------------------

def demo_config():
    IMGUI_DEMO_MARKER("Config")
    imgui.show_font_selector("Font")
    imgui.show_style_selector("ImGui Style")
    implot3d.show_style_selector("ImPlot3D Style")
    implot3d.show_colormap_selector("ImPlot3D Colormap")
    imgui.separator()

    if implot3d.begin_plot("Preview", size=(-1, 0)):
        static = demo_config
        if not hasattr(static, "xs"):
            static.xs = np.zeros((10, 50), dtype=np.float32)
            static.ys = np.zeros((10, 50), dtype=np.float32)
            static.zs = np.zeros((10, 50), dtype=np.float32)
            for i in range(10):
                for j in range(50):
                    t = j / 49.0
                    angle = t * 4.0 * np.pi
                    radius = 0.3 + i * 0.05
                    static.xs[i, j] = radius * np.cos(angle)
                    static.ys[i, j] = radius * np.sin(angle)
                    static.zs[i, j] = i / 9.0

        for i in range(10):
            imgui.push_id(i)
            implot3d.plot_line("##Spiral", static.xs[i], static.ys[i], static.zs[i])
            imgui.pop_id()

        implot3d.end_plot()


#-----------------------------------------------------------------------------
# [SECTION] Demo Window
#-----------------------------------------------------------------------------

def demo_help():
    IMGUI_DEMO_MARKER("Help")
    imgui.separator_text("ABOUT THIS DEMO:")
    imgui.bullet_text("The other tabs are demonstrating many aspects of the library.")

    imgui.separator_text("PROGRAMMER GUIDE:")
    imgui.bullet_text("See the show_demo_window() code in implot3d_demo.py. <- you are here!")
    imgui.bullet_text("See comments in implot3d_demo.py.")
    imgui.bullet_text("See example application in example/ folder.")

    imgui.separator_text("USER GUIDE:")

    imgui.bullet_text("Translation")
    imgui.indent()
    imgui.bullet_text("Left-click drag to translate.")
    imgui.bullet_text("If over axis, only that axis will translate.")
    imgui.bullet_text("If over plane, only that plane will translate.")
    imgui.bullet_text("If outside plot area, translate in the view plane.")
    imgui.unindent()

    imgui.bullet_text("Zoom")
    imgui.indent()
    imgui.bullet_text("Scroll or middle-click drag to zoom.")
    imgui.bullet_text("If over axis, only that axis will zoom.")
    imgui.bullet_text("If over plane, only that plane will zoom.")
    imgui.bullet_text("If outside plot area, zoom the entire plot.")
    imgui.unindent()

    imgui.bullet_text("Rotation")
    imgui.indent()
    imgui.bullet_text("Right-click drag to rotate.")
    imgui.bullet_text("To reset rotation, double right-click outside plot area.")
    imgui.bullet_text("To rotate to plane, double right-click when over the plane.")
    imgui.unindent()

    imgui.bullet_text("Fit data")
    imgui.indent()
    imgui.bullet_text("Double left-click to fit.")
    imgui.bullet_text("If over axis, fit data to axis.")
    imgui.bullet_text("If over plane, fit data to plane.")
    imgui.bullet_text("If outside plot area, fit data to plot.")
    imgui.unindent()

    imgui.bullet_text("Context Menus")
    imgui.indent()
    imgui.bullet_text("Right-click outside plot area to show full context menu.")
    imgui.bullet_text("Right-click over legend to show legend context menu.")
    imgui.bullet_text("Right-click over axis to show axis context menu.")
    imgui.bullet_text("Right-click over plane to show plane context menu.")
    imgui.unindent()

    imgui.bullet_text("Click legend label icons to show/hide plot items.")


def demo_header(label, demo_function):
    static = demo_header
    if not hasattr(static, "fn_snippets"):
        static.fn_snippets = {}

    fn_id = id(demo_function)
    if fn_id not in static.fn_snippets:
        import inspect
        source = inspect.getsource(demo_function)
        snippet_data = immapp.snippets.SnippetData(code=source)
        snippet_data.show_copy_button = True
        snippet_data.max_height_in_lines = 30
        static.fn_snippets[fn_id] = snippet_data

    if imgui.tree_node_ex(label):
        if imgui.tree_node_ex("Source code"):
            snippet_data = static.fn_snippets[fn_id]
            immapp.snippets.show_code_snippet(snippet_data)
            imgui.tree_pop()
        demo_function()
        imgui.tree_pop()


def show_all_demos():
    imgui.text(f"ImPlot3D says olá! ({implot3d.VERSION})")
    imgui.spacing()

    # Tab Bar
    if imgui.begin_tab_bar("ImPlot3DDemoTabs"):
        if imgui.begin_tab_item_simple("Plots"):
            # Plot Types
            imgui.separator_text("Plot Types")
            demo_header("Line Plots", demo_line_plots)
            demo_header("Scatter Plots", demo_scatter_plots)
            demo_header("Triangle Plots", demo_triangle_plots)
            demo_header("Quad Plots", demo_quad_plots)
            demo_header("Surface Plots", demo_surface_plots)
            demo_header("Mesh Plots", demo_mesh_plots)
            demo_header("Realtime Plots", demo_realtime_plots)
            demo_header("Image Plots", demo_image_plots)
            # Plot Options
            imgui.separator_text("Plot Options")
            demo_header("Plot Flags", demo_plot_flags)
            demo_header("Offset and Stride", demo_offset_and_stride)
            demo_header("Legend Options", demo_legend_options)
            demo_header("Markers and Text", demo_markers_and_text)
            demo_header("NaN Values", demo_nan_values)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Axes"):
            demo_header("Box Scale", demo_box_scale)
            demo_header("Box Rotation", demo_box_rotation)
            demo_header("Log Scale", demo_log_scale)
            demo_header("Symmetric Log Scale", demo_symmetric_log_scale)
            demo_header("Tick Labels", demo_tick_labels)
            demo_header("Axis Constraints", demo_axis_constraints)
            demo_header("Equal Axes", demo_equal_axes)
            demo_header("Auto-Fitting Data", demo_auto_fitting_data)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Tools"):
            demo_header("Mouse Picking", demo_mouse_picking)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Custom"):
            demo_header("Custom Styles", demo_custom_styles)
            demo_header("Custom Rendering", demo_custom_rendering)
            demo_header("Custom Overlay", demo_custom_overlay)
            demo_header("Custom Per-Point Style", demo_custom_per_point_style)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Config"):
            demo_config()
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Help"):
            demo_help()
            imgui.end_tab_item()

        imgui.end_tab_bar()

    IMGUI_DEMO_MARKER("end")


def show_demo_window():
    static = show_demo_window

    # Initialize static state variables
    if not hasattr(static, "show_implot3d_style_editor"):
        static.show_implot3d_style_editor = False
        static.show_imgui_metrics = False
        static.show_imgui_style_editor = False
        static.show_imgui_demo = False

    # Show tool windows if enabled
    if static.show_implot3d_style_editor:
        imgui.begin("Style Editor (ImPlot3D)")
        implot3d.show_style_editor()
        imgui.end()

    if static.show_imgui_style_editor:
        imgui.begin("Style Editor (ImGui)")
        imgui.show_style_editor()
        imgui.end()

    if static.show_imgui_metrics:
        imgui.show_metrics_window()

    if static.show_imgui_demo:
        imgui.show_demo_window()

    # Set window properties
    imgui.set_next_window_pos((100, 100), imgui.Cond_.first_use_ever)
    imgui.set_next_window_size((600, 750), imgui.Cond_.first_use_ever)
    imgui.begin("ImPlot3D Demo", None, imgui.WindowFlags_.menu_bar)
    if imgui.begin_menu_bar():
        if imgui.begin_menu("Tools"):
            _, static.show_implot3d_style_editor = imgui.menu_item("Style Editor", "", static.show_implot3d_style_editor)
            imgui.separator()
            _, static.show_imgui_metrics = imgui.menu_item("ImGui Metrics", "", static.show_imgui_metrics)
            _, static.show_imgui_style_editor = imgui.menu_item("ImGui Style Editor", "", static.show_imgui_style_editor)
            _, static.show_imgui_demo = imgui.menu_item("ImGui Demo", "", static.show_imgui_demo)
            imgui.end_menu()
        imgui.end_menu_bar()

    show_all_demos()

    imgui.end()


def demo_gui():
    show_demo_window()


def main():
    immapp.run(show_demo_window, with_implot3d=True, with_markdown=True)


if __name__ == "__main__":
    main()
