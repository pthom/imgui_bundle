from imgui_bundle import imgui, immapp, implot3d

# Define cube vertices
cube_vertices = [
    implot3d.Point(-1.0, -1.0, -1.0),
    implot3d.Point( 1.0, -1.0, -1.0),
    implot3d.Point( 1.0,  1.0, -1.0),
    implot3d.Point(-1.0,  1.0, -1.0),
    implot3d.Point(-1.0, -1.0,  1.0),
    implot3d.Point( 1.0, -1.0,  1.0),
    implot3d.Point( 1.0,  1.0,  1.0),
    implot3d.Point(-1.0,  1.0,  1.0),
]

# Define cube indices
cube_indices = [
    0, 1, 2,  0, 2, 3,  # back face
    4, 5, 6,  4, 6, 7,  # front face
    0, 1, 5,  0, 5, 4,  # bottom face
    2, 3, 7,  2, 7, 6,  # top face
    1, 2, 6,  1, 6, 5,  # right face
    3, 0, 4,  3, 4, 7,  # left face
]

mesh = implot3d.Mesh(cube_vertices, cube_indices)

def gui():
    imgui.text("Cube Mesh with ImPlot3D")
    if implot3d.begin_plot("Cube Plot", (600, 400)):

        # Calling plot_mesh
        implot3d.plot_mesh("Cube", mesh)
        implot3d.end_plot()

if __name__ == "__main__":
    immapp.run(gui, with_implot3d=True, window_size=(800, 600))
