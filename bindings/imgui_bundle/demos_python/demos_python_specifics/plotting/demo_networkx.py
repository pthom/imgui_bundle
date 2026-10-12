"""networkx: a small world
========================

[networkx](https://networkx.org) builds and studies graphs, and draws them with Matplotlib. Here, a ring of people who
each know their nearest neighbors. A few random shortcuts make it a *small world*: any two people get close, while the
friends of each still know each other. Move the shortcuts' probability, and click two people: their shortest path
shows.

<!--more-->

This is the model of Watts and Strogatz (1998), which explained the "six degrees of separation". The curve beside the
graph tells it for 1000 people who each know 10 neighbors: the average path length L drops with very few shortcuts,
while the clustering C (how much the friends of a person know each other) stays high much longer.

networkx builds the graphs (`connected_watts_strogatz_graph`), measures them (`average_shortest_path_length`,
`average_clustering`, `shortest_path`) and draws them through Matplotlib, on a transparent background: the figure
follows the theme. ImPlot draws the curve.

Needs networkx: `pip install networkx` (and Matplotlib).
"""
import math
from dataclasses import dataclass, field

import networkx as nx
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from imgui_bundle import imgui, imgui_fig, implot, immapp, hello_imgui, rich_md, ImVec2

PEOPLE = 40  # the number of people on the ring
NEIGHBORS = 4  # each one knows this many neighbors on the ring
GRAPH_MAX_SIDE = 440.0  # the graph's side at most, in points
NODE_COLOR = "#4c8bf5"
SHORTCUT_COLOR = "#f28e2b"
PATH_COLOR = "#e15759"


def ring_distance(a: int, b: int) -> int:
    """The distance of two people along the ring"""
    d = abs(a - b)
    return min(d, PEOPLE - d)


def small_world(probability: float, seed: int) -> nx.Graph:
    """The ring, each link rewired to a random person with this probability"""
    return nx.connected_watts_strogatz_graph(PEOPLE, NEIGHBORS, probability, seed=seed)


def watts_strogatz_curve(people: int, neighbors: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """L(p) / L(0) and C(p) / C(0), averaged over two graphs per p: the curve of Watts and Strogatz"""
    ring = nx.watts_strogatz_graph(people, neighbors, 0.0)
    l0, c0 = nx.average_shortest_path_length(ring), nx.average_clustering(ring)
    probabilities = np.logspace(-4, 0, 13)
    lengths, clusterings = [], []
    for p in probabilities:
        graphs = [nx.connected_watts_strogatz_graph(people, neighbors, float(p), seed=seed) for seed in range(2)]
        lengths.append(np.mean([nx.average_shortest_path_length(g) for g in graphs]) / l0)
        clusterings.append(np.mean([nx.average_clustering(g) for g in graphs]) / c0)
    return probabilities, np.array(lengths), np.array(clusterings)


# The curve for 1000 people who know 10 neighbors each, as in the article: computed once with
# watts_strogatz_curve(1000, 10), which takes about 10 s (more in a browser). On the 40 people of the graph, the effect
# is too weak to show.
CURVE_1000 = (
    np.logspace(-4, 0, 13),
    np.array([1.0, 0.882, 0.695, 0.58, 0.41, 0.265, 0.178, 0.136, 0.105, 0.088, 0.076, 0.068, 0.065]),
    np.array([1.0, 1.0, 0.999, 0.998, 0.994, 0.987, 0.97, 0.939, 0.864, 0.739, 0.505, 0.167, 0.014]),
)


def graph_figure(graph: nx.Graph, path: list[int], side: float) -> tuple[Figure, Axes]:
    """The graph on its ring, drawn by networkx, on a transparent background. side: in points"""
    dpi = 100.0 * min(imgui.get_io().display_framebuffer_scale.x, 2.0)  # sharp on a high density screen
    fig = Figure(figsize=(side / 100.0, side / 100.0), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_axis_off()
    ax.set(xlim=(-1.12, 1.12), ylim=(-1.12, 1.12), aspect="equal")

    pos = nx.circular_layout(graph)
    ring = [e for e in graph.edges if ring_distance(*e) <= NEIGHBORS // 2]
    shortcuts = [e for e in graph.edges if ring_distance(*e) > NEIGHBORS // 2]
    nx.draw_networkx_edges(graph, pos, edgelist=ring, ax=ax, edge_color="#8c96a0", width=1.0)
    nx.draw_networkx_edges(graph, pos, edgelist=shortcuts, ax=ax, edge_color=SHORTCUT_COLOR, width=1.5)
    path_edges = list(zip(path, path[1:], strict=False))
    nx.draw_networkx_edges(graph, pos, edgelist=path_edges, ax=ax, edge_color=PATH_COLOR, width=4.0)
    colors = [PATH_COLOR if n in path else NODE_COLOR for n in graph.nodes]
    sizes = [110 if n in (path[:1] + path[-1:]) else 50 for n in graph.nodes]
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=colors, node_size=sizes)
    return fig, ax


RING = small_world(0.0, 0)
RING_LENGTH, RING_CLUSTERING = nx.average_shortest_path_length(RING), nx.average_clustering(RING)


@dataclass
class AppState:
    probability: float = 0.05  # the probability of a shortcut
    seed: int = 0  # "New graph" changes it
    graph: nx.Graph = field(default_factory=lambda: small_world(0.05, 0))
    clicked: list[int] = field(default_factory=list)  # the people clicked: the ends of the path
    fig: Figure | None = None
    ax: Axes | None = None
    drawn: tuple[object, ...] = ()  # what the figure was drawn with
    drawn_side: float = 0.0


state = AppState()


def path() -> list[int]:
    """The shortest path between the two people clicked (empty until there are two)"""
    if len(state.clicked) < 2:
        return []
    return list(nx.shortest_path(state.graph, state.clicked[0], state.clicked[1]))


def person_at(mouse: ImVec2, image_min: ImVec2, image_max: ImVec2) -> int | None:
    """The person under the mouse: from the screen to the figure's pixels (y up), then to the axes' coordinates"""
    assert state.fig is not None and state.ax is not None
    px = (mouse.x - image_min.x) / (image_max.x - image_min.x) * state.fig.bbox.width
    py = (1.0 - (mouse.y - image_min.y) / (image_max.y - image_min.y)) * state.fig.bbox.height
    x, y = state.ax.transData.inverted().transform((px, py))
    pos = nx.circular_layout(state.graph)
    nearest = min(pos, key=lambda n: math.dist(pos[n], (x, y)))
    return nearest if math.dist(pos[nearest], (x, y)) < 0.1 else None


def gui_curve(size: ImVec2) -> None:
    """The curve of Watts and Strogatz, with the current probability"""
    probabilities, lengths, clusterings = CURVE_1000
    if implot.begin_plot("1000 people: L and C against p", size):
        implot.setup_axes("probability of a shortcut p", "relative to the ring")
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.log10)
        implot.setup_axes_limits(0.0001, 1.0, 0.0, 1.05, imgui.Cond_.always)
        implot.plot_line("path length L / L(0)", probabilities, lengths)
        implot.plot_line("clustering C / C(0)", probabilities, clusterings)
        implot.plot_inf_lines("p", np.array([state.probability]))
        implot.end_plot()


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    imgui.set_next_item_width(hello_imgui.em_size(12))
    changed, state.probability = imgui.slider_float("shortcuts", state.probability, 0.0001, 1.0, "%.4f",
                                                    imgui.SliderFlags_.logarithmic)
    sliding = imgui.is_item_active()
    imgui.same_line()
    if imgui.button("New graph"):
        state.seed += 1
        changed = True
    if changed:
        state.graph = small_world(state.probability, state.seed)
        state.clicked = state.clicked[:1]

    # The graph: networkx draws it when it changes (once the slider is released), or when the window's width changes
    avail_width = imgui.get_content_region_avail().x
    side = min(GRAPH_MAX_SIDE, avail_width)
    wanted = (state.probability, state.seed, tuple(state.clicked), side)
    redraw = state.fig is None or (wanted != state.drawn and not sliding)
    if redraw:
        state.fig, state.ax = graph_figure(state.graph, path(), side)
        state.drawn, state.drawn_side = wanted, side
    assert state.fig is not None
    drawn_side = state.drawn_side

    imgui_fig.fig("graph", state.fig, size=ImVec2(drawn_side, drawn_side), refresh_image=redraw, resizable=False)
    image_min, image_max = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    if imgui.is_item_hovered() and imgui.is_mouse_clicked(imgui.MouseButton_.left):
        person = person_at(imgui.get_mouse_pos(), image_min, image_max)
        if person is not None:
            state.clicked = [person] if len(state.clicked) != 1 else state.clicked + [person]

    # The curve: beside the graph when there is room, else below it
    if avail_width >= drawn_side + hello_imgui.em_size(20):
        imgui.same_line()
        gui_curve(ImVec2(-1, drawn_side))
    else:
        gui_curve(ImVec2(-1, hello_imgui.em_size(14)))

    length, clustering = nx.average_shortest_path_length(state.graph), nx.average_clustering(state.graph)
    imgui.text(f"Average path length L = {length:.2f}, clustering C = {clustering:.2f}")
    imgui.same_line()
    imgui.text_disabled(f"(the ring alone: L = {RING_LENGTH:.2f}, C = {RING_CLUSTERING:.2f})")
    touch = imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen
    if len(state.clicked) < 2:
        verb = "Tap" if touch else "Click"
        imgui.text_disabled(f"{verb} two people (two dots): the shortest path between them shows.")
    else:
        steps = len(path()) - 1
        imgui.text(f"From person {state.clicked[0]} to person {state.clicked[1]}: {steps} steps")


def main() -> None:
    immapp.run(gui, window_title="networkx: a small world", window_size=(1000, 820), with_markdown=True,
               with_implot=True)


if __name__ == "__main__":
    main()
