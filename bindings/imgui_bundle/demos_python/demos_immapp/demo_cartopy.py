"""Cartopy: the shortest route around the globe
=============================================

[Cartopy](https://scitools.org.uk/cartopy) draws maps with Matplotlib, in many projections. Here, two routes between
two cities: the shortest one (in red, an arc of a great circle), and the straight line that a ruler draws on a flat
map (dashed). Pick the cities and the projection: on a flat map, the shortest route looks curved.

<!--more-->

The globe is an orthographic projection: the Earth seen from far away, which two sliders turn and tilt. Robinson and
Mollweide are world maps that keep the areas, or nearly. Mercator, the projection of the web maps, keeps the angles
but inflates the poles. The plain grid of longitudes and latitudes is the "flat map" of the dashed line.

Cartopy reprojects anything given a `transform`: the routes are lists of longitudes and latitudes
(`transform=ccrs.Geodetic()`), the background is its bundled image of the Earth (`ax.stock_img()`): no download.

Needs Cartopy: `pip install cartopy`.
"""
from dataclasses import dataclass

import cartopy.crs as ccrs
import numpy as np
from matplotlib.figure import Figure
from imgui_bundle import imgui, imgui_fig, immapp, hello_imgui, rich_md, ImVec2

MAP_MAX_SIDE = 560.0  # the map's side at most, in points (it is square)
EARTH_RADIUS_KM = 6371.0
ROUTE_COLOR = "#e15759"
CITIES = {  # longitude, latitude
    "New York": (-74.01, 40.71), "Tokyo": (139.69, 35.69), "Paris": (2.35, 48.86), "Sydney": (151.21, -33.87),
    "Rio de Janeiro": (-43.17, -22.91), "Cape Town": (18.42, -33.92), "Los Angeles": (-118.24, 34.05),
    "Singapore": (103.82, 1.35), "Reykjavik": (-21.94, 64.15), "Buenos Aires": (-58.38, -34.60),
    "Moscow": (37.62, 55.76), "Dubai": (55.27, 25.20),
}
CITY_NAMES = list(CITIES)
PROJECTIONS = ["Globe", "Robinson", "Mollweide", "Mercator", "Longitudes and latitudes"]


def to_xyz(lon: float, lat: float) -> np.ndarray:
    """A point of the sphere, from its longitude and latitude (in degrees)"""
    lon, lat = np.radians(lon), np.radians(lat)
    return np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def great_circle(a: tuple[float, float], b: tuple[float, float], count: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """The shortest route from a to b: longitudes and latitudes along the arc of a great circle"""
    p, q = to_xyz(*a), to_xyz(*b)
    angle = np.arccos(np.clip(np.dot(p, q), -1.0, 1.0))
    t = np.linspace(0.0, 1.0, count)[:, None]
    points = (np.sin((1.0 - t) * angle) * p + np.sin(t * angle) * q) / np.sin(angle)
    return np.degrees(np.arctan2(points[:, 1], points[:, 0])), np.degrees(np.arcsin(points[:, 2]))


def flat_line(a: tuple[float, float], b: tuple[float, float], count: int = 400) -> tuple[np.ndarray, np.ndarray]:
    """The straight line of the flat map from a to b: longitude and latitude change at a steady pace (the shorter way
    in longitude, across the date line if need be)"""
    lon_b = a[0] + (b[0] - a[0] + 180.0) % 360.0 - 180.0
    return np.linspace(a[0], lon_b, count), np.linspace(a[1], b[1], count)


def length_km(lons: np.ndarray, lats: np.ndarray) -> float:
    """The length of a route given by its points, along the sphere"""
    p = np.array([to_xyz(lon, lat) for lon, lat in zip(lons, lats, strict=True)])
    cosines = np.clip(np.sum(p[1:] * p[:-1], axis=1), -1.0, 1.0)
    return float(np.sum(np.arccos(cosines)) * EARTH_RADIUS_KM)


def projection(index: int, center: tuple[float, float]) -> ccrs.Projection:
    """The projection, centered on this longitude and latitude (a flat map: on the longitude only)"""
    if index == 0:
        return ccrs.Orthographic(*center)
    return [ccrs.Robinson, ccrs.Mollweide, ccrs.Mercator, ccrs.PlateCarree][index - 1](central_longitude=center[0])


def map_figure(a: str, b: str, index: int, center: tuple[float, float], side: float) -> Figure:
    """The map with the two routes, on a transparent background. side: in points"""
    dpi = 100.0 * min(imgui.get_io().display_framebuffer_scale.x, 2.0)  # sharp on a high density screen
    fig = Figure(figsize=(side / 100.0, side / 100.0), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes((0.02, 0.02, 0.96, 0.96), projection=projection(index, center))
    ax.set_global()
    ax.stock_img()
    ax.gridlines(color="white", alpha=0.4, linewidth=0.5)

    ax.plot(*flat_line(CITIES[a], CITIES[b]), "--", color="#333333", linewidth=1.5, transform=ccrs.PlateCarree())
    ax.plot(*great_circle(CITIES[a], CITIES[b]), color=ROUTE_COLOR, linewidth=2.5, transform=ccrs.Geodetic())
    for name in (a, b):
        lon, lat = CITIES[name]
        ax.plot(lon, lat, "o", color="white", markeredgecolor="black", markersize=6, transform=ccrs.PlateCarree())
        ax.text(lon, lat, "  " + name, fontsize=9, fontweight="bold", transform=ccrs.PlateCarree())
    return fig


@dataclass
class AppState:
    city_a: int = CITY_NAMES.index("New York")
    city_b: int = CITY_NAMES.index("Tokyo")
    projection: int = 0  # in PROJECTIONS
    center_lon: float = 0.0  # the center of the globe
    center_lat: float = 0.0
    fig: Figure | None = None
    drawn: tuple[object, ...] = ()  # what the figure was drawn with
    drawn_side: float = 0.0


state = AppState()


def center_on_route() -> None:
    """The globe turns to show the middle of the route"""
    lons, lats = great_circle(CITIES[CITY_NAMES[state.city_a]], CITIES[CITY_NAMES[state.city_b]], 3)
    state.center_lon, state.center_lat = float(lons[1]), float(lats[1])


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    if not state.drawn:
        center_on_route()
    width = hello_imgui.em_size(9)
    imgui.set_next_item_width(width)
    changed_a, state.city_a = imgui.combo("##from", state.city_a, CITY_NAMES)
    imgui.same_line()
    imgui.text("to")
    imgui.same_line()
    imgui.set_next_item_width(width)
    changed_b, state.city_b = imgui.combo("##to", state.city_b, CITY_NAMES)
    if changed_a or changed_b:
        center_on_route()
    imgui.set_next_item_width(hello_imgui.em_size(19) + imgui.calc_text_size("to").x)
    _, state.projection = imgui.combo("projection", state.projection, PROJECTIONS)
    sliding = False
    if state.projection == 0:
        imgui.set_next_item_width(hello_imgui.em_size(12))
        _, state.center_lon = imgui.slider_float("turn", state.center_lon, -180.0, 180.0, "%.0f°")
        sliding = imgui.is_item_active()
        imgui.set_next_item_width(hello_imgui.em_size(12))
        _, state.center_lat = imgui.slider_float("tilt", state.center_lat, -90.0, 90.0, "%.0f°")
        sliding = sliding or imgui.is_item_active()

    # The map: Cartopy redraws it when a parameter changes (once a slider is released), or when the window's width
    # changes much
    a, b = CITY_NAMES[state.city_a], CITY_NAMES[state.city_b]
    side = min(MAP_MAX_SIDE, imgui.get_content_region_avail().x)
    wanted = (a, b, state.projection, state.center_lon, state.center_lat, side)
    redraw = state.fig is None or (wanted != state.drawn and not sliding)
    if redraw:
        state.fig = map_figure(a, b, state.projection, (state.center_lon, state.center_lat), side)
        state.drawn, state.drawn_side = wanted, side
    assert state.fig is not None
    imgui_fig.fig("map", state.fig, size=ImVec2(state.drawn_side, state.drawn_side), refresh_image=redraw,
                  resizable=False)

    if a != b:
        shortest = length_km(*great_circle(CITIES[a], CITIES[b]))
        flat = length_km(*flat_line(CITIES[a], CITIES[b]))
        imgui.text(f"The shortest route: {shortest:,.0f} km.")
        imgui.text(f"The straight line of the flat map: {flat:,.0f} km ({100 * (flat / shortest - 1):.0f}% longer).")


def main() -> None:
    immapp.run(gui, window_title="Cartopy: the shortest route around the globe", window_size=(760, 960),
               with_markdown=True)


if __name__ == "__main__":
    main()
