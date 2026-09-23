"""Mermaid spike: a native subset, registered as the renderer of ```mermaid blocks.
- flowcharts (graph TD/LR, rectangle/rounded/diamond nodes, labeled edges), laid out in layers;
- sequence diagrams (participants, the four arrow kinds, self-messages, notes, loop frames).
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
    for nd in graph.nodes.values():
        if vertical:
            nd.pos.y += shift
        else:
            nd.pos.x += shift
    for b, (p0, p1) in graph.boxes.items():
        graph.boxes[b] = (ImVec2(p0.x, p0.y + shift), ImVec2(p1.x, p1.y + shift)) if vertical else (ImVec2(p0.x + shift, p0.y), ImVec2(p1.x + shift, p1.y))
    lanes = 1.2 * em * len(back)  # room on the right (TD) or below (LR) for the back edges
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
    for e in graph.edges:
        a, b = graph.nodes[e.src], graph.nodes[e.dst]
        a0, a1 = rect(a)
        b0, b1 = rect(b)
        ca, cb = ImVec2((a0.x + a1.x) / 2, (a0.y + a1.y) / 2), ImVec2((b0.x + b1.x) / 2, (b0.y + b1.y) / 2)
        if (e.src, e.dst) in graph.back_edges:
            # out of the source in the flow direction, into the gap after its layer, along a lane past
            # the graph, back through the gap before the target's layer, into the target from the front
            lane += 1
            half_gap = 0.7 * em  # not the middle of the gap, where the forward edges run
            if vertical:
                lx = origin.x + size.x - 1.2 * em * len(graph.back_edges) + 1.2 * em * lane
                pts = [ImVec2(ca.x, a1.y), ImVec2(ca.x, a1.y + half_gap), ImVec2(lx, a1.y + half_gap),
                       ImVec2(lx, b0.y - half_gap), ImVec2(cb.x, b0.y - half_gap), ImVec2(cb.x, b0.y)]
            else:
                ly = origin.y + size.y - 1.2 * em * len(graph.back_edges) + 1.2 * em * lane
                pts = [ImVec2(a1.x, ca.y), ImVec2(a1.x + half_gap, ca.y), ImVec2(a1.x + half_gap, ly),
                       ImVec2(b0.x - half_gap, ly), ImVec2(b0.x - half_gap, cb.y), ImVec2(b0.x, cb.y)]
        elif vertical:
            mid_y = (a1.y + b0.y) / 2
            pts = [ImVec2(ca.x, a1.y), ImVec2(cb.x, b0.y)] if abs(ca.x - cb.x) < 1 else [ImVec2(ca.x, a1.y), ImVec2(ca.x, mid_y), ImVec2(cb.x, mid_y), ImVec2(cb.x, b0.y)]
        else:
            mid_x = (a1.x + b0.x) / 2
            pts = [ImVec2(a1.x, ca.y), ImVec2(b0.x, cb.y)] if abs(ca.y - cb.y) < 1 else [ImVec2(a1.x, ca.y), ImVec2(mid_x, ca.y), ImVec2(mid_x, cb.y), ImVec2(b0.x, cb.y)]
        _polyline(dl, pts, border, e.arrow, em, e.style)
        if e.label:
            # on the middle segment when there is one, else at the middle of the edge
            seg = (pts[len(pts) // 2 - 1], pts[len(pts) // 2]) if len(pts) > 2 else (pts[0], pts[1])
            ts = imgui.calc_text_size(e.label)
            mid = ImVec2((seg[0].x + seg[1].x) / 2 - ts.x / 2, (seg[0].y + seg[1].y) / 2 - ts.y / 2)
            dl.add_rect_filled(ImVec2(mid.x - 2, mid.y), ImVec2(mid.x + ts.x + 2, mid.y + ts.y), window_bg)
            dl.add_text(mid, text_col, e.label)
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


_cache: dict[str, Graph | Sequence] = {}


def render_mermaid(code: str) -> None:
    if code not in _cache:
        _cache[code] = parse_sequence(code) if code.lstrip().startswith("sequenceDiagram") else parse(code)
    diagram = _cache[code]
    if isinstance(diagram, Sequence):
        draw_sequence(diagram)
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
