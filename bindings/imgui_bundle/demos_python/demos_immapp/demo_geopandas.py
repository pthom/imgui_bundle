"""geopandas: the world as a table
=================================

[geopandas](https://geopandas.org) is pandas with shapes: each row of a table has a geometry. Here, the countries of
[Natural Earth](https://www.naturalearthdata.com), colored by the column you pick, in the projection you pick. Click a
country: its row shows.

<!--more-->

A few lines of geopandas do the work:

- `gpd.read_file(url)` reads the countries from a GeoJSON file on the web (a download of 820 KB at the start);
- `world.to_crs(...)` reprojects every shape: Equal Earth keeps the areas, Mercator inflates them toward the poles
  (compare Greenland with Africa), and the plain grid of longitudes and latitudes stretches them sideways;
- `world.to_crs(EQUAL_EARTH).area` measures the countries in square meters, for the density;
- `world.plot(column=...)` draws the map with Matplotlib, and `world[world.contains(point)]` finds the country under
  the mouse.

Needs geopandas: `pip install geopandas`.
"""
from dataclasses import dataclass

import geopandas as gpd
import matplotlib
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm, to_hex
from matplotlib.figure import Figure
from shapely.geometry import Point
from imgui_bundle import imgui, imgui_fig, immapp, hello_imgui, rich_md, ImVec2

# The countries of Natural Earth, through jsDelivr (its own site sends no CORS header: a browser could not read it)
COUNTRIES_URL = ("https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/"
                 "geojson/ne_110m_admin_0_countries.geojson")
MAP_MAX_WIDTH = 760.0  # the map's width at most, in points
EQUAL_EARTH = "EPSG:8857"
PROJECTIONS = {"Equal Earth": EQUAL_EARTH, "Mercator": "EPSG:3857", "Longitudes and latitudes": "EPSG:4326"}
# The columns to color by: their label, their name in the table, and whether a log scale suits them
COLUMNS = [("Population", "population", True), ("People per km²", "density", True),
           ("GDP per person (US$)", "gdp_per_person", True), ("Continent", "CONTINENT", False)]


def load_world() -> gpd.GeoDataFrame:
    """The countries, with a few columns computed from the others"""
    world = gpd.read_file(COUNTRIES_URL)
    # Antarctica leaves: nearly no one lives there (it would stretch the color scales), and Mercator cannot draw it
    world = world[world["NAME"] != "Antarctica"]
    world["population"] = world["POP_EST"]
    world["area_km2"] = world.to_crs(EQUAL_EARTH).area / 1e6  # true areas: in an equal area projection
    world["density"] = world["POP_EST"] / world["area_km2"]
    world["gdp_per_person"] = world["GDP_MD"] * 1e6 / world["POP_EST"]
    return world


def theme_text_color() -> str:
    """The color of the GUI's text, for the figure's labels: it follows the theme"""
    c = imgui.get_style_color_vec4(imgui.Col_.text)
    return to_hex((c.x, c.y, c.z))


def world_map(world: gpd.GeoDataFrame, column: int, crs: str, selected: str, width: float) -> tuple[Figure, Axes]:
    """The map, drawn by geopandas, on a transparent background. width: in points"""
    label, name, log = COLUMNS[column]
    projected = world.to_crs(crs)
    text = theme_text_color()
    with matplotlib.rc_context({"text.color": text, "axes.labelcolor": text, "xtick.color": text,
                                "ytick.color": text, "axes.edgecolor": text}):
        dpi = 100.0 * min(imgui.get_io().display_framebuffer_scale.x, 2.0)  # sharp on a high density screen
        fig = Figure(figsize=(width / 100.0, width * 0.62 / 100.0), dpi=dpi, layout="constrained")
        fig.patch.set_alpha(0.0)
        ax = fig.add_subplot()
        ax.set_axis_off()
        if log:
            values = projected[name][projected[name] > 0]
            projected.plot(column=name, ax=ax, cmap="viridis", norm=LogNorm(values.min(), values.max()),
                           edgecolor="white", linewidth=0.3, legend=True,
                           legend_kwds={"orientation": "horizontal", "shrink": 0.5, "label": label, "pad": 0.02})
        else:
            projected.plot(column=name, ax=ax, cmap="tab10", categorical=True, edgecolor="white", linewidth=0.3,
                           legend=True, legend_kwds={"loc": "upper center", "bbox_to_anchor": (0.5, 0.0), "ncols": 4,
                                                     "fontsize": 8, "frameon": False})
        # The selected country, outlined in the color of the text: it stands out on any fill
        projected[projected["NAME"] == selected].boundary.plot(ax=ax, color=text, linewidth=2.0)
    return fig, ax


@dataclass
class AppState:
    world: gpd.GeoDataFrame | None = None
    column: int = 0  # in COLUMNS
    projection: int = 0  # in PROJECTIONS
    selected: str = "France"  # the name of the selected country
    fig: Figure | None = None
    ax: Axes | None = None
    drawn: tuple[object, ...] = ()  # what the figure was drawn with
    drawn_width: float = 0.0


state = AppState()


def country_at(mouse: ImVec2, image_min: ImVec2, image_max: ImVec2) -> str | None:
    """The country under the mouse: from the screen to the figure's pixels (y up), to the map's coordinates"""
    assert state.world is not None and state.fig is not None and state.ax is not None
    px = (mouse.x - image_min.x) / (image_max.x - image_min.x) * state.fig.bbox.width
    py = (1.0 - (mouse.y - image_min.y) / (image_max.y - image_min.y)) * state.fig.bbox.height
    x, y = state.ax.transData.inverted().transform((px, py))
    projected = state.world.to_crs(list(PROJECTIONS.values())[state.projection])
    found = projected[projected.contains(Point(x, y))]
    return None if found.empty else str(found["NAME"].iloc[0])


def gui_country_row() -> None:
    """The row of the selected country"""
    assert state.world is not None
    row = state.world[state.world["NAME"] == state.selected].iloc[0]
    imgui.text(f"{row['NAME']} ({row['CONTINENT']})")
    imgui.text_disabled(
        f"Population {row['population']:,.0f}   ·   {row['area_km2']:,.0f} km²   ·   "
        f"{row['density']:,.0f} people per km²   ·   GDP per person {row['gdp_per_person']:,.0f} US$")


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    if state.world is None:
        state.world = load_world()
    imgui.set_next_item_width(hello_imgui.em_size(14))
    _, state.column = imgui.combo("color by", state.column, [label for label, _, _ in COLUMNS])
    imgui.set_next_item_width(hello_imgui.em_size(14))
    _, state.projection = imgui.combo("projection", state.projection, list(PROJECTIONS))

    # The map: geopandas redraws it when a choice or the theme changes, or when the window's width changes much
    width = min(MAP_MAX_WIDTH, imgui.get_content_region_avail().x)
    crs = list(PROJECTIONS.values())[state.projection]
    wanted = (state.column, crs, state.selected, theme_text_color())
    redraw = state.fig is None or wanted != state.drawn or abs(width - state.drawn_width) > hello_imgui.em_size(2)
    if redraw:
        state.fig, state.ax = world_map(state.world, state.column, crs, state.selected, width)
        state.drawn, state.drawn_width = wanted, width
    assert state.fig is not None
    height = state.drawn_width * state.fig.bbox.height / state.fig.bbox.width
    imgui_fig.fig("map", state.fig, size=ImVec2(state.drawn_width, height), refresh_image=redraw, resizable=False)
    image_min, image_max = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    if imgui.is_item_hovered() and imgui.is_mouse_clicked(imgui.MouseButton_.left):
        country = country_at(imgui.get_mouse_pos(), image_min, image_max)
        if country is not None:
            state.selected = country

    gui_country_row()
    touch = imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen
    imgui.text_disabled(("Tap" if touch else "Click") + " a country: its row shows.")


def main() -> None:
    immapp.run(gui, window_title="geopandas: the world as a table", window_size=(800, 820), with_markdown=True)


if __name__ == "__main__":
    main()
