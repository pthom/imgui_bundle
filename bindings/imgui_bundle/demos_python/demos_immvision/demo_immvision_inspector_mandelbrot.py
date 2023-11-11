import numpy as np
from numpy.typing import NDArray
from imgui_bundle import immvision, immapp, imgui
from imgui_bundle.demos_python import demo_utils

PreciseFloat = float  # np.float64
ColorType = np.float32

# NameError: name 'jit' is not defined
# =>
#     pip install numba
# @jit
def lerp(a, b, x):
    return a + (b - a) * x


# @njit(cache=True, nogil=True, parallel=True)
def mandelbrot(
    width: int,
    height: int,
    x_center: PreciseFloat,
    y_center: PreciseFloat,
    zoom: PreciseFloat,
    max_iterations: int,
) -> NDArray[np.float32]:
    result = np.zeros((height, width), ColorType)

    # Compute boundings
    x_width: PreciseFloat = 1.5
    y_height: PreciseFloat = 1.5 * height / width
    x_from = x_center - x_width / zoom
    x_to = x_center + x_width / zoom
    y_from = y_center - y_height / zoom
    y_to = y_center + y_height / zoom

    # for iy in numba.prange(height):  # parallel loop! (speedup by a factor of 7 on an 8 cores machines)
    for iy in range(height):
        ky: PreciseFloat = iy / height
        y0 = lerp(y_from, y_to, ky)
        for ix in range(width):
            kx: PreciseFloat = ix / width

            # start iteration
            x0 = lerp(x_from, x_to, kx)

            x: PreciseFloat = 0.0
            y: PreciseFloat = 0.0

            # perform Mandelbrot set iterations
            escaped = False
            for iteration in range(max_iterations):
                x_new = x * x - y * y + x0
                y = 2 * x * y + y0
                x = x_new

                # if escaped
                norm2 = x * x + y * y
                if norm2 > 4.0:
                    escaped = True
                    # color using pretty linear gradient
                    # color: ColorType = 1.0 - 0.01 * (iteration - np.log2(np.log2(norm2)))
                    color = iteration
                    break

            if not escaped:
                color = 0

            result[iy, ix] = color

    return result


locations = [
    {"coords": [-0.5, 0.0], "name": "Mandelbrot full", "zoom": 1.0},
    {
        "coords": [0.27668094779430163, 0.008101875630718678],
        "name": "Aliens",
        "zoom": 140210.64691527165,
    },
    {
        "coords": [-0.7961073900746515, -0.18324251614029363],
        "name": "Flowers",
        "zoom": 12297024368713.648,
    },
]


def fill_inspector():
    for location in locations:
        name = location["name"]
        print(f"Computing {name}")
        width = 400
        height = 300
        max_iterations = 300
        x = location["coords"][0]  # type: ignore
        y = location["coords"][1]  # type: ignore
        zoom: float = location["zoom"]  # type: ignore
        image = mandelbrot(width, height, x, y, zoom, max_iterations)
        immvision.inspector_add_image(
            image,
            legend=name,
        )


def demo_gui():
    if imgui.button("Fill inspector"):
        fill_inspector()
    immvision.inspector_show()


def main():
    demo_utils.set_hello_imgui_demo_assets_folder()
    immapp.run(demo_gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
