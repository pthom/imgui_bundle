"""Mermaid spike: a native subset, registered as the renderer of ```mermaid blocks.
- flowcharts (graph TD/LR, rectangle/rounded/diamond nodes, labeled edges), laid out in layers;
- sequence diagrams (participants, the four arrow kinds, self-messages, notes, loop frames);
- class diagrams (compartments, <<annotations>>, namespaces, the UML relations with labels and cardinalities).
Question of the spike: is a native subset worth owning, or do we keep only the fenced-block seam?"""
import re
from dataclasses import dataclass, field

from imgui_bundle import imgui, immapp, imgui_md, ImVec2

# =============================================================================
# Parsing: a subset of Mermaid flowcharts
# =============================================================================


@dataclass
class Node:
    id: str
    label: str
    shape: str = "rect"  # rect, rounded, diamond, cylinder
    subgraph: str = ""   # the subgraph the node belongs to ("" for none)
    lines: list[list[str]] = field(default_factory=list)  # class diagrams: the compartments (name, attributes, methods)
    rank: int = 0
    order: int = 0
    pos: ImVec2 = field(default_factory=lambda: ImVec2(0, 0))
    size: ImVec2 = field(default_factory=lambda: ImVec2(0, 0))


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""
    arrow: bool = True
    style: str = "solid"  # solid, dotted, thick


@dataclass
class Graph:
    direction: str = "TD"
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    subgraphs: dict[str, str] = field(default_factory=dict)  # id -> title, in source order
    back_edges: set[tuple[str, str]] = field(default_factory=set)  # edges closing a cycle (filled by layout)
    boxes: dict[str, tuple[ImVec2, ImVec2]] = field(default_factory=dict)  # subgraph -> bounding box (filled by layout)
    lanes: int = 0  # edges routed past the graph: back edges and edges skipping a layer (filled by layout)


_NODE_RE = re.compile(r"^\s*(\w+)\s*(\[\(([^)]*)\)\]|\[([^\]]*)\]|\(([^)]*)\)|\{([^}]*)\})?\s*$")
# A --> B, A ---|label| B, A -. label .-> B, A -.-> B, A ==> B
_EDGE_RE = re.compile(r"^(.*?)\s*(-->|---|-\.\s*([^.]*?)\s*\.->|-\.->|==>)\s*(?:\|([^|]*)\|\s*)?(.*)$")


def _node(graph: Graph, text: str, subgraph: str) -> str:
    m = _NODE_RE.match(text)
    if not m:
        raise ValueError(f"cannot parse node: {text!r}")
    node_id = m.group(1)
    if node_id not in graph.nodes:
        graph.nodes[node_id] = Node(node_id, node_id, subgraph=subgraph)
    node = graph.nodes[node_id]
    if subgraph and not node.subgraph:
        node.subgraph = subgraph
    shapes = {3: "cylinder", 4: "rect", 5: "rounded", 6: "diamond"}
    for group, shape in shapes.items():
        if m.group(group) is not None:
            node.label, node.shape = m.group(group), shape
    return node_id


def parse(source: str) -> Graph:
    graph = Graph()
    subgraph = ""
    for raw in source.splitlines():
        line = raw.split("%%")[0].strip()
        if not line:
            continue
        if line.startswith(("graph", "flowchart")):
            graph.direction = line.split()[1] if len(line.split()) > 1 else "TD"
            continue
        if line.startswith("subgraph"):
            rest = line[8:].strip()
            m_sub = re.match(r"^(\w+)\s*(?:\[(.*)\])?$", rest)
            subgraph = m_sub.group(1) if m_sub else rest
            graph.subgraphs[subgraph] = (m_sub.group(2) if m_sub and m_sub.group(2) else subgraph)
            continue
        if line == "end":
            subgraph = ""
            continue
        m = _EDGE_RE.match(line)
        if m:
            src = _node(graph, m.group(1), subgraph)
            dst = _node(graph, m.group(5), subgraph)
            token = m.group(2)
            style = "dotted" if token.startswith("-.") else ("thick" if token == "==>" else "solid")
            label = (m.group(3) or m.group(4) or "").strip()
            graph.edges.append(Edge(src, dst, label, token != "---", style))
        else:
            _node(graph, line, subgraph)
    return graph


# =============================================================================
# Layout: layered (back edges reversed, longest-path ranks, barycenter ordering), sizes from the text
# =============================================================================


def layout(graph: Graph, em: float) -> ImVec2:
    ids = list(graph.nodes)
    succs: dict[str, list[str]] = {i: [] for i in ids}
    for e in graph.edges:
        succs[e.src].append(e.dst)
    # back edges: found by a depth-first visit from the nodes in input order (as dagre does), and
    # reversed for the ranking so that the cycle example keeps its natural top-down order
    state: dict[str, int] = {}  # 0 visiting, 1 done
    back: set[tuple[str, str]] = set()

    def visit(n: str) -> None:
        state[n] = 0
        for m in succs[n]:
            if m not in state:
                visit(m)
            elif state[m] == 0:
                back.add((n, m))
        state[n] = 1

    for n in ids:
        if n not in state:
            visit(n)
    graph.back_edges = back
    forward_preds: dict[str, list[str]] = {i: [] for i in ids}
    for e in graph.edges:
        if (e.src, e.dst) in back:
            forward_preds[e.src].append(e.dst)
        else:
            forward_preds[e.dst].append(e.src)
    rank: dict[str, int] = {}

    def rank_of(n: str) -> int:
        if n not in rank:
            rank[n] = 1 + max((rank_of(p) for p in forward_preds[n]), default=-1)
        return rank[n]

    for n in ids:
        graph.nodes[n].rank = rank_of(n)
    layers: dict[int, list[str]] = {}
    for n in ids:
        layers.setdefault(graph.nodes[n].rank, []).append(n)
    for r in sorted(layers):
        for i, n in enumerate(layers[r]):
            graph.nodes[n].order = i
    # ordering: a few barycenter sweeps
    for _ in range(4):
        for r in sorted(layers):
            def bary(n: str, r: int = r) -> float:
                ps = [graph.nodes[p].order for p in forward_preds[n] if graph.nodes[p].rank < r]
                return sum(ps) / len(ps) if ps else graph.nodes[n].order
            layers[r].sort(key=bary)
            for i, n in enumerate(layers[r]):
                graph.nodes[n].order = i
    # sizes
    pad, gap_x, gap_y = 0.8 * em, 1.5 * em, 2.5 * em
    for node in graph.nodes.values():
        if node.lines:  # a class box: the widest line, one text line per row, a padding per compartment
            w = max(imgui.calc_text_size(t).x for comp in node.lines for t in comp) if any(node.lines) else 0
            h = sum(len(comp) * imgui.get_text_line_height() + 0.6 * em for comp in node.lines)
            node.size = ImVec2(w + 2 * pad, h)
            continue
        text = imgui.calc_text_size(node.label)
        extra = text.y if node.shape in ("diamond", "cylinder") else 0
        node.size = ImVec2(text.x + 2 * pad + (extra if node.shape == "diamond" else 0), text.y + 2 * pad + extra)
    vertical = graph.direction in ("TD", "TB")

    def cross(nd: Node) -> float:
        return nd.size.x if vertical else nd.size.y

    def main(nd: Node) -> float:
        return nd.size.y if vertical else nd.size.x

    # bands on the cross axis: one per subgraph (in source order), one for the free nodes; a band is as
    # wide as its widest layer, so that the subgraph boxes never overlap
    bands = list(graph.subgraphs) + [""]
    box_pad = 0.8 * em
    band_width: dict[str, float] = {b: 0.0 for b in bands}
    for r in sorted(layers):
        layers[r].sort(key=lambda n: (bands.index(graph.nodes[n].subgraph), graph.nodes[n].order))
        for b in bands:
            members = [graph.nodes[n] for n in layers[r] if graph.nodes[n].subgraph == b]
            if members:
                w = sum(cross(nd) for nd in members) + gap_x * (len(members) - 1)
                if b:  # room for the box, and for its title when the cross axis is vertical (LR)
                    w += 2 * box_pad + (0 if vertical else imgui.get_text_line_height() + 0.4 * em)
                band_width[b] = max(band_width[b], w)
    band_start: dict[str, float] = {}
    x = 0.0
    for b in bands:
        if band_width[b] > 0:
            band_start[b] = x
            x += band_width[b] + gap_x
    total_cross = max(x - gap_x, 0.0)
    # positions: layers along the main axis, nodes centered in their band
    offset_main = 0.0
    for r in sorted(layers):
        nodes = [graph.nodes[node_id] for node_id in layers[r]]
        thickness = max(main(nd) for nd in nodes)
        for b in bands:
            members = [nd for nd in nodes if nd.subgraph == b]
            if not members:
                continue
            w = sum(cross(nd) for nd in members) + gap_x * (len(members) - 1)
            cursor = band_start[b] + (band_width[b] - w) / 2
            if b and not vertical:
                cursor += (imgui.get_text_line_height() + 0.4 * em) / 2  # the title is above the members
            for nd in members:
                if vertical:
                    nd.pos = ImVec2(cursor, offset_main + (thickness - nd.size.y) / 2)
                else:
                    nd.pos = ImVec2(offset_main + (thickness - nd.size.x) / 2, cursor)
                cursor += cross(nd) + gap_x
        offset_main += thickness + gap_y
    # subgraph boxes: the members' bounding box, padded, with room for the title
    title_h = imgui.get_text_line_height() + 0.4 * em
    graph.boxes = {}
    for b in graph.subgraphs:
        members = [nd for nd in graph.nodes.values() if nd.subgraph == b]
        if not members:
            continue
        x0 = min(nd.pos.x for nd in members) - box_pad
        y0 = min(nd.pos.y for nd in members) - box_pad - title_h
        x1 = max(nd.pos.x + nd.size.x for nd in members) + box_pad
        y1 = max(nd.pos.y + nd.size.y for nd in members) + box_pad
        graph.boxes[b] = (ImVec2(x0, y0), ImVec2(x1, y1))
    # everything shifted along the main axis: room for the boxes' titles above the first layer (TD),
    # and for the back edges that come back in front of the first layer
    shift = (title_h + box_pad if graph.subgraphs and vertical else 0.0) + (1.5 * em if back else 0.0)
    graph.back_edges = back
    for nd in graph.nodes.values():
        if vertical:
            nd.pos.y += shift
        else:
            nd.pos.x += shift
    for b, (p0, p1) in graph.boxes.items():
        graph.boxes[b] = (ImVec2(p0.x, p0.y + shift), ImVec2(p1.x, p1.y + shift)) if vertical else (ImVec2(p0.x + shift, p0.y), ImVec2(p1.x + shift, p1.y))
    graph.lanes = sum(1 for e in graph.edges if _uses_lane(graph, e))
    lanes = 1.2 * em * graph.lanes  # room on the right (TD) or below (LR) for the lane edges
    main_total = offset_main - gap_y + shift
    return ImVec2(total_cross + lanes, main_total) if vertical else ImVec2(main_total, total_cross + lanes)


# =============================================================================
# Drawing: elbow edges, back edges around the graph, arrowheads at the end of the last segment
# =============================================================================


def _segment(dl: imgui.ImDrawList, a: ImVec2, b: ImVec2, col: int, style: str, em: float) -> None:
    if style != "dotted":
        dl.add_line(a, b, col, 2.5 if style == "thick" else 1.5)
        return
    dx, dy = b.x - a.x, b.y - a.y
    length = max((dx * dx + dy * dy) ** 0.5, 1e-3)
    ux, uy = dx / length, dy / length
    d = 0.0
    while d < length:
        e = min(d + 0.35 * em, length)
        dl.add_line(ImVec2(a.x + ux * d, a.y + uy * d), ImVec2(a.x + ux * e, a.y + uy * e), col, 1.5)
        d += 0.7 * em


def _polyline(dl: imgui.ImDrawList, pts: list[ImVec2], col: int, arrow: bool, em: float, style: str = "solid") -> None:
    """Draws the segments; with an arrow, the last segment stops at the base of the triangle"""
    end = pts[-1]
    if arrow:
        prev = pts[-2]
        dx, dy = end.x - prev.x, end.y - prev.y
        n = max((dx * dx + dy * dy) ** 0.5, 1e-3)
        ux, uy = dx / n, dy / n
        s = 0.55 * em
        base = ImVec2(end.x - s * ux, end.y - s * uy)
        pts = pts[:-1] + [base]
        dl.add_triangle_filled(end, ImVec2(base.x + s * 0.45 * uy, base.y - s * 0.45 * ux), ImVec2(base.x - s * 0.45 * uy, base.y + s * 0.45 * ux), col)
    for a, b in zip(pts, pts[1:], strict=False):
        _segment(dl, a, b, col, style, em)


def _uses_lane(graph: Graph, e: Edge) -> bool:
    """Back edges and edges spanning more than one layer travel on a lane past the graph"""
    return (e.src, e.dst) in graph.back_edges or graph.nodes[e.dst].rank - graph.nodes[e.src].rank > 1


def _anchors(graph: Graph, vertical: bool) -> dict[int, tuple[float, float]]:
    """For each edge: where it leaves its source and enters its target, as fractions of the node's side,
    spread so that edges of one node do not share a point (ordered by the other end's position)"""

    def cross(n: str) -> float:
        nd = graph.nodes[n]
        return nd.pos.x if vertical else nd.pos.y

    out: dict[str, list[int]] = {}
    inc: dict[str, list[int]] = {}
    for i, e in enumerate(graph.edges):
        out.setdefault(e.src, []).append(i)
        inc.setdefault(e.dst, []).append(i)
    result: dict[int, tuple[float, float]] = {i: (0.5, 0.5) for i in range(len(graph.edges))}
    for edges in out.values():
        edges.sort(key=lambda i: cross(graph.edges[i].dst))
        for k, i in enumerate(edges):
            result[i] = ((k + 1) / (len(edges) + 1), result[i][1])
    for edges in inc.values():
        edges.sort(key=lambda i: cross(graph.edges[i].src))
        for k, i in enumerate(edges):
            result[i] = (result[i][0], (k + 1) / (len(edges) + 1))
    return result


def _edge_points(graph: Graph, e: Edge, origin: ImVec2, size: ImVec2, vertical: bool, lane: int, em: float,
                 anchor: tuple[float, float] = (0.5, 0.5)) -> list[ImVec2]:
    """The elbow polyline of an edge: forward edges through the middle of the gap between layers; lane edges
    (back edges, edges skipping a layer) out of the source in the flow direction, into the gap after its layer,
    along a lane past the graph, back through the gap before the target's layer, into the target from the front"""
    a, b = graph.nodes[e.src], graph.nodes[e.dst]
    a0 = ImVec2(origin.x + a.pos.x, origin.y + a.pos.y)
    a1 = ImVec2(a0.x + a.size.x, a0.y + a.size.y)
    b0 = ImVec2(origin.x + b.pos.x, origin.y + b.pos.y)
    # the exit and entry points, spread along the sides
    if vertical:
        pa, pb = ImVec2(a0.x + a.size.x * anchor[0], a1.y), ImVec2(b0.x + b.size.x * anchor[1], b0.y)
    else:
        pa, pb = ImVec2(a1.x, a0.y + a.size.y * anchor[0]), ImVec2(b0.x, b0.y + b.size.y * anchor[1])
    if _uses_lane(graph, e):
        half_gap = 0.7 * em  # not the middle of the gap, where the forward edges run
        if vertical:
            lx = origin.x + size.x - 1.2 * em * graph.lanes + 1.2 * em * lane
            return [pa, ImVec2(pa.x, pa.y + half_gap), ImVec2(lx, pa.y + half_gap),
                    ImVec2(lx, pb.y - half_gap), ImVec2(pb.x, pb.y - half_gap), pb]
        ly = origin.y + size.y - 1.2 * em * graph.lanes + 1.2 * em * lane
        return [pa, ImVec2(pa.x + half_gap, pa.y), ImVec2(pa.x + half_gap, ly),
                ImVec2(pb.x - half_gap, ly), ImVec2(pb.x - half_gap, pb.y), pb]
    if vertical:
        mid_y = (a1.y + b0.y) / 2
        if abs(pa.x - pb.x) < 1:
            return [pa, pb]
        return [pa, ImVec2(pa.x, mid_y), ImVec2(pb.x, mid_y), pb]
    mid_x = (a1.x + b0.x) / 2
    if abs(pa.y - pb.y) < 1:
        return [pa, pb]
    return [pa, ImVec2(mid_x, pa.y), ImVec2(mid_x, pb.y), pb]


def _edge_label(dl: imgui.ImDrawList, pts: list[ImVec2], label: str, text_col: int, bg: int) -> None:
    """On the middle segment when there is one, else at the middle of the edge"""
    seg = (pts[len(pts) // 2 - 1], pts[len(pts) // 2]) if len(pts) > 2 else (pts[0], pts[1])
    ts = imgui.calc_text_size(label)
    mid = ImVec2((seg[0].x + seg[1].x) / 2 - ts.x / 2, (seg[0].y + seg[1].y) / 2 - ts.y / 2)
    dl.add_rect_filled(ImVec2(mid.x - 2, mid.y), ImVec2(mid.x + ts.x + 2, mid.y + ts.y), bg)
    dl.add_text(mid, text_col, label)


def draw(graph: Graph) -> None:
    em = imgui.get_font_size()
    size = layout(graph, em)
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + em, origin.y + em / 2)
    dl = imgui.get_window_draw_list()
    text_col = imgui.get_color_u32(imgui.Col_.text)
    border = imgui.get_color_u32(imgui.Col_.text, 0.6)
    fill = imgui.get_color_u32(imgui.Col_.frame_bg)
    window_bg = imgui.get_color_u32(imgui.Col_.window_bg)
    vertical = graph.direction in ("TD", "TB")

    def rect(node: Node) -> tuple[ImVec2, ImVec2]:
        p0 = ImVec2(origin.x + node.pos.x, origin.y + node.pos.y)
        return p0, ImVec2(p0.x + node.size.x, p0.y + node.size.y)

    for sub, (p0, p1) in graph.boxes.items():
        q0, q1 = ImVec2(origin.x + p0.x, origin.y + p0.y), ImVec2(origin.x + p1.x, origin.y + p1.y)
        dl.add_rect_filled(q0, q1, imgui.get_color_u32(imgui.Col_.text, 0.04), 0.3 * em)
        dl.add_rect(q0, q1, imgui.get_color_u32(imgui.Col_.text, 0.35), 0.3 * em, 1.0)
        dl.add_text(ImVec2(q0.x + 0.5 * em, q0.y + 0.2 * em), imgui.get_color_u32(imgui.Col_.text, 0.8), graph.subgraphs[sub])
    lane = 0
    anchors = _anchors(graph, vertical)
    for i, e in enumerate(graph.edges):
        if _uses_lane(graph, e):
            lane += 1
        pts = _edge_points(graph, e, origin, size, vertical, lane, em, anchors[i])
        _polyline(dl, pts, border, e.arrow, em, e.style)
        if e.label:
            _edge_label(dl, pts, e.label, text_col, window_bg)
    for node in graph.nodes.values():
        p0, p1 = rect(node)
        c = ImVec2((p0.x + p1.x) / 2, (p0.y + p1.y) / 2)
        if node.shape == "diamond":
            pts = [ImVec2(c.x, p0.y), ImVec2(p1.x, c.y), ImVec2(c.x, p1.y), ImVec2(p0.x, c.y)]
            dl.add_convex_poly_filled(pts, fill)  # type: ignore[arg-type]
            dl.add_polyline(pts, border, 1.5, imgui.ImDrawFlags_.closed.value)  # type: ignore[arg-type]
        elif node.shape == "cylinder":
            ry = 0.35 * em
            dl.add_rect_filled(ImVec2(p0.x, p0.y + ry), ImVec2(p1.x, p1.y - ry), fill)
            dl.add_ellipse_filled(ImVec2(c.x, p1.y - ry), ImVec2(node.size.x / 2, ry), fill)
            dl.add_ellipse_filled(ImVec2(c.x, p0.y + ry), ImVec2(node.size.x / 2, ry), fill)
            dl.add_line(ImVec2(p0.x, p0.y + ry), ImVec2(p0.x, p1.y - ry), border, 1.5)
            dl.add_line(ImVec2(p1.x, p0.y + ry), ImVec2(p1.x, p1.y - ry), border, 1.5)
            dl.add_ellipse(ImVec2(c.x, p0.y + ry), ImVec2(node.size.x / 2, ry), border, 0.0, 0, 1.5)
            dl.add_ellipse(ImVec2(c.x, p1.y - ry), ImVec2(node.size.x / 2, ry), border, 0.0, 0, 1.5)
        else:
            rounding = 0.6 * em if node.shape == "rounded" else 0.15 * em
            dl.add_rect_filled(p0, p1, fill, rounding)
            dl.add_rect(p0, p1, border, rounding, 1.5)
        ts = imgui.calc_text_size(node.label)
        dl.add_text(ImVec2(c.x - ts.x / 2, c.y - ts.y / 2), text_col, node.label)
    imgui.dummy(ImVec2(size.x + 2 * em, size.y + em))


# =============================================================================
# Sequence diagrams
# =============================================================================


@dataclass
class Message:
    src: str
    dst: str
    text: str
    dashed: bool = False
    arrowhead: bool = True


@dataclass
class SeqNote:
    over: list[str]
    text: str


@dataclass
class Loop:
    label: str
    first: int  # index of the first row inside the loop
    last: int = -1


@dataclass
class Sequence:
    participants: dict[str, str] = field(default_factory=dict)  # id -> label
    rows: list[Message | SeqNote] = field(default_factory=list)
    loops: list[Loop] = field(default_factory=list)


_MSG_RE = re.compile(r"^(\w+)\s*(-->>|->>|-->|->)\s*(\w+)\s*:\s*(.*)$")
_NOTE_RE = re.compile(r"^Note\s+(over|right of|left of)\s+([\w, ]+):\s*(.*)$", re.I)


def parse_sequence(source: str) -> Sequence:
    seq = Sequence()

    def participant(name: str, label: str | None = None) -> None:
        if name not in seq.participants or label:
            seq.participants[name] = label or seq.participants.get(name, name)

    open_loops: list[Loop] = []
    for raw in source.splitlines():
        line = raw.split("%%")[0].strip()
        if not line or line.startswith("sequenceDiagram"):
            continue
        if line.startswith(("participant ", "actor ")):
            rest = line.split(None, 1)[1]
            name, _, alias = rest.partition(" as ")
            participant(name.strip(), alias.strip() or None)
            continue
        if line.startswith("loop"):
            open_loops.append(Loop(line[4:].strip(), len(seq.rows)))
            continue
        if line == "end" and open_loops:
            loop = open_loops.pop()
            loop.last = len(seq.rows) - 1
            seq.loops.append(loop)
            continue
        if line.startswith(("activate", "deactivate")):
            continue
        m = _NOTE_RE.match(line)
        if m:
            names = [n.strip() for n in m.group(2).split(",")]
            for n in names:
                participant(n)
            seq.rows.append(SeqNote(names, m.group(3)))
            continue
        m = _MSG_RE.match(line)
        if m:
            participant(m.group(1))
            participant(m.group(3))
            arrow = m.group(2)
            seq.rows.append(Message(m.group(1), m.group(3), m.group(4), dashed=arrow.startswith("--"), arrowhead=arrow.endswith(">>")))
    return seq


def draw_sequence(seq: Sequence) -> None:
    em = imgui.get_font_size()
    dl = imgui.get_window_draw_list()
    text_col = imgui.get_color_u32(imgui.Col_.text)
    line_col = imgui.get_color_u32(imgui.Col_.text, 0.6)
    fill = imgui.get_color_u32(imgui.Col_.frame_bg)
    note_fill = imgui.get_color_u32(imgui.Col_.frame_bg_hovered)
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + em, origin.y + em / 2)
    ids = list(seq.participants)
    # participant boxes: a column per participant, wide enough for its label and the messages
    box_w = {i: imgui.calc_text_size(seq.participants[i]).x + 2 * em for i in ids}
    col_gap = 3 * em
    for r in seq.rows:
        if isinstance(r, Message) and r.src != r.dst:
            a, b = sorted((ids.index(r.src), ids.index(r.dst)))
            if b == a + 1:
                col_gap = max(col_gap, imgui.calc_text_size(r.text).x + 2 * em)
    x_center: dict[str, float] = {}
    x = 0.0
    for i in ids:
        x_center[i] = x + box_w[i] / 2
        x += box_w[i] + col_gap
    total_w = x - col_gap
    box_h = imgui.get_text_line_height() + em
    row_h = 2.2 * em
    height = box_h + (len(seq.rows) + 1) * row_h + box_h
    # lifelines and boxes (top and bottom)
    for i in ids:
        cx = origin.x + x_center[i]
        for y in (origin.y, origin.y + height - box_h):
            p0, p1 = ImVec2(cx - box_w[i] / 2, y), ImVec2(cx + box_w[i] / 2, y + box_h)
            dl.add_rect_filled(p0, p1, fill, 0.2 * em)
            dl.add_rect(p0, p1, line_col, 0.2 * em, 1.5)
            ts = imgui.calc_text_size(seq.participants[i])
            dl.add_text(ImVec2(cx - ts.x / 2, y + (box_h - ts.y) / 2), text_col, seq.participants[i])
        y0, y1 = origin.y + box_h, origin.y + height - box_h
        d = 0.0
        while d < y1 - y0:  # dashed lifeline
            dl.add_line(ImVec2(cx, y0 + d), ImVec2(cx, min(y0 + d + 0.5 * em, y1)), line_col, 1.0)
            d += em
    # loop frames, behind the rows
    for loop in seq.loops:
        y0 = origin.y + box_h + (loop.first + 0.4) * row_h
        y1 = origin.y + box_h + (loop.last + 1.3) * row_h
        p0, p1 = ImVec2(origin.x - 0.5 * em, y0), ImVec2(origin.x + total_w + 0.5 * em, y1)
        dl.add_rect(p0, p1, line_col, 0.0, 1.0)
        label = f"loop [{loop.label}]"
        ts = imgui.calc_text_size(label)
        dl.add_rect_filled(p0, ImVec2(p0.x + ts.x + em, p0.y + ts.y + 0.3 * em), fill)
        dl.add_text(ImVec2(p0.x + 0.5 * em, p0.y + 0.15 * em), text_col, label)
    # rows
    for k, r in enumerate(seq.rows):
        y = origin.y + box_h + (k + 1) * row_h
        if isinstance(r, SeqNote):
            xs = [origin.x + x_center[n] for n in r.over]
            ts = imgui.calc_text_size(r.text)
            cx = sum(xs) / len(xs)
            half = max((max(xs) - min(xs)) / 2 + em, ts.x / 2 + 0.5 * em)
            p0, p1 = ImVec2(cx - half, y - ts.y / 2 - 0.3 * em), ImVec2(cx + half, y + ts.y / 2 + 0.3 * em)
            dl.add_rect_filled(p0, p1, note_fill, 0.1 * em)
            dl.add_rect(p0, p1, line_col, 0.1 * em, 1.0)
            dl.add_text(ImVec2(cx - ts.x / 2, y - ts.y / 2), text_col, r.text)
            continue
        xa, xb = origin.x + x_center[r.src], origin.x + x_center[r.dst]
        ts = imgui.calc_text_size(r.text)
        if r.src == r.dst:  # self message: a small hook on the right of the lifeline
            w = 1.5 * em
            pts = [ImVec2(xa, y - 0.5 * em), ImVec2(xa + w, y - 0.5 * em), ImVec2(xa + w, y + 0.5 * em), ImVec2(xa, y + 0.5 * em)]
            for pa, pb in zip(pts, pts[1:], strict=False):
                dl.add_line(pa, pb, line_col, 1.5)
            dl.add_text(ImVec2(xa + w + 0.4 * em, y - ts.y / 2), text_col, r.text)
            tip, direction = pts[-1], -1.0
        else:
            if r.dashed:
                d, length = 0.0, abs(xb - xa)
                sign = 1.0 if xb > xa else -1.0
                while d < length:
                    dl.add_line(ImVec2(xa + sign * d, y), ImVec2(xa + sign * min(d + 0.5 * em, length), y), line_col, 1.5)
                    d += 0.8 * em
            else:
                dl.add_line(ImVec2(xa, y), ImVec2(xb, y), line_col, 1.5)
            dl.add_text(ImVec2((xa + xb) / 2 - ts.x / 2, y - ts.y - 0.2 * em), text_col, r.text)
            tip, direction = ImVec2(xb, y), (1.0 if xb > xa else -1.0)
        s_ = 0.55 * em
        p_back = ImVec2(tip.x - direction * s_, tip.y)
        if r.arrowhead:
            dl.add_rect_filled(ImVec2(min(tip.x, p_back.x), tip.y - 1), ImVec2(max(tip.x, p_back.x), tip.y + 1), imgui.get_color_u32(imgui.Col_.window_bg))  # the line stops at the base
            dl.add_triangle_filled(tip, ImVec2(p_back.x, tip.y - s_ * 0.45), ImVec2(p_back.x, tip.y + s_ * 0.45), line_col)
        else:
            dl.add_line(tip, ImVec2(p_back.x, tip.y - s_ * 0.45), line_col, 1.5)
            dl.add_line(tip, ImVec2(p_back.x, tip.y + s_ * 0.45), line_col, 1.5)
    imgui.dummy(ImVec2(total_w + 2 * em, height + em))


# =============================================================================
# Class diagrams: classes with compartments, namespaces as bands, UML relation markers
# =============================================================================


@dataclass
class Relation:
    src: str
    dst: str
    marker_src: str = ""   # triangle (inheritance, realization), diamond_filled (composition), diamond (aggregation)
    marker_dst: str = ""   # arrow (association, dependency)
    dashed: bool = False   # dependency, realization
    label: str = ""
    card_src: str = ""
    card_dst: str = ""


@dataclass
class ClassDiagram:
    graph: Graph = field(default_factory=Graph)
    relations: list[Relation] = field(default_factory=list)


# forward spellings (the marker at the source), and their mirrors
_RELATIONS = {
    "<|--": ("triangle", "", False), "*--": ("diamond_filled", "", False), "o--": ("diamond", "", False),
    "-->": ("", "arrow", False), "--": ("", "", False), "..>": ("", "arrow", True), "<|..": ("triangle", "", True), "..": ("", "", True),
}
_MIRRORS = {"--|>": "<|--", "--*": "*--", "--o": "o--", "<--": "-->", "<..": "..>", "..|>": "<|.."}
_REL_RE = re.compile(r'^(\w+)\s*(?:"([^"]*)"\s*)?(<\|--|\*--|o--|-->|--\|>|--\*|--o|<--|\.\.>|<\.\.|\.\.\|>|<\|\.\.|--|\.\.)\s*(?:"([^"]*)"\s*)?(\w+)\s*(?::\s*(.*))?$')
_MEMBER_RE = re.compile(r"^(\w+)\s*:\s*(.+)$")


def _class_node(d: ClassDiagram, name: str, namespace: str) -> Node:
    if name not in d.graph.nodes:
        node = Node(name, name, subgraph=namespace, lines=[[name], [], []])
        d.graph.nodes[name] = node
    node = d.graph.nodes[name]
    if namespace and not node.subgraph:
        node.subgraph = namespace
    return node


def _add_member(node: Node, member: str) -> None:
    member = member.strip()
    if member.startswith("<<") and member.endswith(">>"):
        node.lines[0].insert(0, "\u00ab" + member[2:-2] + "\u00bb")
    elif "(" in member:
        node.lines[2].append(member)
    else:
        node.lines[1].append(member)


def parse_class(source: str) -> ClassDiagram:
    d = ClassDiagram()
    namespace = ""
    current: Node | None = None  # inside `class X {`
    for raw in source.splitlines():
        line = raw.split("%%")[0].strip()
        if not line or line.startswith("classDiagram"):
            continue
        if current is not None:
            if line == "}":
                current = None
            else:
                _add_member(current, line)
            continue
        if line.startswith("namespace "):
            namespace = line[10:].strip().rstrip("{").strip()
            d.graph.subgraphs[namespace] = namespace
            continue
        if line == "}":
            namespace = ""
            continue
        if line.startswith("class "):
            rest = line[6:].strip()
            if rest.endswith("{"):
                current = _class_node(d, rest[:-1].strip(), namespace)
            else:
                _class_node(d, rest, namespace)
            continue
        if line.startswith("<<") and ">>" in line:  # <<interface>> Shape
            annotation, _, name = line.partition(">>")
            _add_member(_class_node(d, name.strip(), namespace), annotation + ">>")
            continue
        m = _REL_RE.match(line)
        if m:
            src, card_src, token, card_dst, dst, label = m.groups()
            if token in _MIRRORS:
                token = _MIRRORS[token]
                src, dst, card_src, card_dst = dst, src, card_dst, card_src
            marker_src, marker_dst, dashed = _RELATIONS[token]
            _class_node(d, src, namespace)
            _class_node(d, dst, namespace)
            d.relations.append(Relation(src, dst, marker_src, marker_dst, dashed, (label or "").strip(), card_src or "", card_dst or ""))
            d.graph.edges.append(Edge(src, dst, "", False, "dotted" if dashed else "solid"))
            continue
        m = _MEMBER_RE.match(line)
        if m:
            _add_member(_class_node(d, m.group(1), namespace), m.group(2))
    return d


def _marker(dl: imgui.ImDrawList, kind: str, tip: ImVec2, towards: ImVec2, col: int, bg: int, em: float) -> ImVec2:
    """Draws a UML marker at `tip`, pointing away from `towards` (the next point of the line);
    returns the point where the line should stop"""
    dx, dy = towards.x - tip.x, towards.y - tip.y
    n = max((dx * dx + dy * dy) ** 0.5, 1e-3)
    ux, uy = dx / n, dy / n  # from the tip along the line
    px, py = -uy, ux
    s = 0.8 * em
    if kind == "triangle":
        base = ImVec2(tip.x + s * ux, tip.y + s * uy)
        p1, p2 = ImVec2(base.x + s * 0.5 * px, base.y + s * 0.5 * py), ImVec2(base.x - s * 0.5 * px, base.y - s * 0.5 * py)
        dl.add_triangle_filled(tip, p1, p2, bg)
        dl.add_triangle(tip, p1, p2, col, 1.5)
        return base
    if kind in ("diamond", "diamond_filled"):
        mid = ImVec2(tip.x + s * 0.6 * ux, tip.y + s * 0.6 * uy)
        end = ImVec2(tip.x + s * 1.2 * ux, tip.y + s * 1.2 * uy)
        pts = [tip, ImVec2(mid.x + s * 0.35 * px, mid.y + s * 0.35 * py), end, ImVec2(mid.x - s * 0.35 * px, mid.y - s * 0.35 * py)]
        dl.add_convex_poly_filled(pts, col if kind == "diamond_filled" else bg)  # type: ignore[arg-type]
        dl.add_polyline(pts, col, 1.5, imgui.ImDrawFlags_.closed.value)  # type: ignore[arg-type]
        return end
    if kind == "arrow":
        base = ImVec2(tip.x + s * 0.7 * ux, tip.y + s * 0.7 * uy)
        dl.add_line(tip, ImVec2(base.x + s * 0.35 * px, base.y + s * 0.35 * py), col, 1.5)
        dl.add_line(tip, ImVec2(base.x - s * 0.35 * px, base.y - s * 0.35 * py), col, 1.5)
        return tip
    return tip


def draw_class(d: ClassDiagram) -> None:
    graph = d.graph
    em = imgui.get_font_size()
    size = layout(graph, em)
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + em, origin.y + em / 2)
    dl = imgui.get_window_draw_list()
    text_col = imgui.get_color_u32(imgui.Col_.text)
    border = imgui.get_color_u32(imgui.Col_.text, 0.6)
    fill = imgui.get_color_u32(imgui.Col_.frame_bg)
    window_bg = imgui.get_color_u32(imgui.Col_.window_bg)
    line_h = imgui.get_text_line_height()
    for sub, (p0, p1) in graph.boxes.items():
        q0, q1 = ImVec2(origin.x + p0.x, origin.y + p0.y), ImVec2(origin.x + p1.x, origin.y + p1.y)
        dl.add_rect_filled(q0, q1, imgui.get_color_u32(imgui.Col_.text, 0.04), 0.3 * em)
        dl.add_rect(q0, q1, imgui.get_color_u32(imgui.Col_.text, 0.35), 0.3 * em, 1.0)
        dl.add_text(ImVec2(q0.x + 0.5 * em, q0.y + 0.2 * em), imgui.get_color_u32(imgui.Col_.text, 0.8), graph.subgraphs[sub])
    lane = 0
    anchors = _anchors(graph, True)
    for i, (e, r) in enumerate(zip(graph.edges, d.relations, strict=True)):
        if _uses_lane(graph, e):
            lane += 1
        pts = _edge_points(graph, e, origin, size, True, lane, em, anchors[i])
        start = _marker(dl, r.marker_src, pts[0], pts[1], border, window_bg, em)
        end = _marker(dl, r.marker_dst, pts[-1], pts[-2], border, window_bg, em)
        _polyline(dl, [start] + pts[1:-1] + [end], border, False, em, "dotted" if r.dashed else "solid")
        if r.label:
            _edge_label(dl, pts, r.label, text_col, window_bg)
        for card, p, q in ((r.card_src, pts[0], pts[1]), (r.card_dst, pts[-1], pts[-2])):
            if card:
                dx, dy = q.x - p.x, q.y - p.y
                n = max((dx * dx + dy * dy) ** 0.5, 1e-3)
                ts = imgui.calc_text_size(card)
                along, side = 1.3 * em, 0.4 * em
                pos = ImVec2(p.x + dx / n * along + (side if dy != 0 else -ts.x / 2), p.y + dy / n * along + (side if dx != 0 else -ts.y / 2))
                dl.add_text(pos, text_col, card)
    for node in graph.nodes.values():
        p0 = ImVec2(origin.x + node.pos.x, origin.y + node.pos.y)
        p1 = ImVec2(p0.x + node.size.x, p0.y + node.size.y)
        dl.add_rect_filled(p0, p1, fill, 0.15 * em)
        dl.add_rect(p0, p1, border, 0.15 * em, 1.5)
        y = p0.y
        for i, comp in enumerate(node.lines):
            h = len(comp) * line_h + 0.6 * em
            if i > 0:
                dl.add_line(ImVec2(p0.x, y), ImVec2(p1.x, y), border, 1.0)
            for j, text in enumerate(comp):
                ts = imgui.calc_text_size(text)
                x = (p0.x + p1.x) / 2 - ts.x / 2 if i == 0 else p0.x + 0.6 * em  # the name is centered
                dl.add_text(ImVec2(x, y + 0.3 * em + j * line_h), text_col, text)
            y += h
    imgui.dummy(ImVec2(size.x + 2 * em, size.y + em))


_cache: dict[str, Graph | Sequence | ClassDiagram] = {}


def render_mermaid(code: str) -> None:
    if code not in _cache:
        head = code.lstrip()
        if head.startswith("sequenceDiagram"):
            _cache[code] = parse_sequence(code)
        elif head.startswith("classDiagram"):
            _cache[code] = parse_class(code)
        else:
            _cache[code] = parse(code)
    diagram = _cache[code]
    if isinstance(diagram, Sequence):
        draw_sequence(diagram)
    elif isinstance(diagram, ClassDiagram):
        draw_class(diagram)
    else:
        draw(diagram)


MD = r"""
# Mermaid, a native subset
```mermaid
flowchart LR
  subgraph Client
    UI[Web app]
    Cache[(Local cache)]
  end
  subgraph Services
    API[API gateway]
    Auth[Auth service]
    Orders[Order service]
  end
  subgraph Storage
    DB[(Orders DB)]
  end
  UI --> API
  UI --> Cache
  API --> Auth
  API --> Orders
  Orders --> DB
  Auth -. token .-> UI
```
The same graph, left to right:
```mermaid
graph LR
    A[Source file] --> B[Sections]
    B --> C{Imported?}
    C -->|prose| D(Markdown)
    C -->|code| E(Snippet)
```

```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{decide}
    C --> D[Keep]
    C --> E[Edit Definition]
    E --> B
    D --> F[Save Image and Code]
    F --> B
```

A class diagram:
```mermaid
classDiagram
    namespace Geometry {
        class Shape {
            <<interface>>
            +area() float
            +perimeter() float
        }
        class Circle {
            -radius: float
            +area() float
        }
        class Polygon {
            -points: List~Point~
            +area() float
        }
    }
    class Canvas {
        +shapes: List~Shape~
        +draw()
    }
    class Renderer
    class Style {
        +color: Color
        +thickness: float
    }
    Shape <|-- Circle : implements
    Shape <|-- Polygon
    Canvas "1" *-- "many" Shape : owns
    Canvas o-- Renderer : uses
    Renderer ..> Style : depends on
    Canvas --> Style : default
```
A sequence diagram:
```mermaid
sequenceDiagram
    participant App
    participant MD as imgui_md
    participant Host as Host services
    App->>MD: Render(text)
    MD->>MD: resolve @import
    MD->>Host: ReadAsset(path)
    Host-->>MD: bytes
    loop each formula
        MD->>Host: RenderLatex(latex)
        Host-->>MD: bitmap
        MD->Host: UploadRgba(bitmap)
    end
    Note over MD,Host: textures are ImTextureData, created by the backend
    MD-->>App: drawn
```
"""


_registered = False


def gui() -> None:
    global _registered
    if not _registered:  # the markdown context exists once the app runs
        imgui_md.register_fenced_block_renderer("mermaid", render_mermaid)
        _registered = True
    imgui_md.render(MD)


if __name__ == "__main__":
    immapp.run(gui, window_title="Mermaid spike", window_size=(900, 900), with_markdown=True)
