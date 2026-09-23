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
    shape: str = "rect"  # rect, rounded, diamond
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


@dataclass
class Graph:
    direction: str = "TD"
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)


_NODE_RE = re.compile(r"^\s*(\w+)\s*(\[([^\]]*)\]|\(([^)]*)\)|\{([^}]*)\})?\s*$")
_EDGE_RE = re.compile(r"^(.*?)\s*(-->|---)\s*(?:\|([^|]*)\|\s*)?(.*)$")


def _node(graph: Graph, text: str) -> str:
    m = _NODE_RE.match(text)
    if not m:
        raise ValueError(f"cannot parse node: {text!r}")
    node_id = m.group(1)
    if node_id not in graph.nodes:
        graph.nodes[node_id] = Node(node_id, node_id)
    node = graph.nodes[node_id]
    if m.group(3) is not None:
        node.label, node.shape = m.group(3), "rect"
    elif m.group(4) is not None:
        node.label, node.shape = m.group(4), "rounded"
    elif m.group(5) is not None:
        node.label, node.shape = m.group(5), "diamond"
    return node_id


def parse(source: str) -> Graph:
    graph = Graph()
    for raw in source.splitlines():
        line = raw.split("%%")[0].strip()
        if not line:
            continue
        if line.startswith(("graph", "flowchart")):
            graph.direction = line.split()[1] if len(line.split()) > 1 else "TD"
            continue
        m = _EDGE_RE.match(line)
        if m:
            src = _node(graph, m.group(1))
            dst = _node(graph, m.group(4))
            graph.edges.append(Edge(src, dst, (m.group(3) or "").strip(), m.group(2) == "-->"))
        else:
            _node(graph, line)
    return graph


# =============================================================================
# Layout: layered (longest path ranks, barycenter ordering), sizes from the text
# =============================================================================


def layout(graph: Graph, em: float) -> ImVec2:
    ids = list(graph.nodes)
    preds: dict[str, list[str]] = {i: [] for i in ids}
    succs: dict[str, list[str]] = {i: [] for i in ids}
    for e in graph.edges:
        preds[e.dst].append(e.src)
        succs[e.src].append(e.dst)
    # ranks: longest path from a source (cycles are cut by the visit order)
    rank: dict[str, int] = {}

    def rank_of(n: str, stack: tuple[str, ...] = ()) -> int:
        if n in rank:
            return rank[n]
        if n in stack:
            return 0
        rank[n] = 1 + max((rank_of(p, stack + (n,)) for p in preds[n]), default=-1)
        return rank[n]

    for n in ids:
        graph.nodes[n].rank = rank_of(n)
    layers: dict[int, list[str]] = {}
    for n in ids:
        layers.setdefault(graph.nodes[n].rank, []).append(n)
    # ordering: a few barycenter sweeps
    for _ in range(4):
        for r in sorted(layers):
            def bary(n: str, r: int = r) -> float:
                ps = [graph.nodes[p].order for p in preds[n] if graph.nodes[p].rank < r]
                return sum(ps) / len(ps) if ps else graph.nodes[n].order
            layers[r].sort(key=bary)
            for i, n in enumerate(layers[r]):
                graph.nodes[n].order = i
    # sizes and positions
    pad, gap_x, gap_y = 0.8 * em, 1.5 * em, 2.0 * em
    for node in graph.nodes.values():
        text = imgui.calc_text_size(node.label)
        node.size = ImVec2(text.x + 2 * pad + (text.y if node.shape == "diamond" else 0), text.y + 2 * pad + (text.y if node.shape == "diamond" else 0))
    vertical = graph.direction in ("TD", "TB")
    offset_main = 0.0
    total_cross = 0.0
    for r in sorted(layers):
        nodes = [graph.nodes[node_id] for node_id in layers[r]]
        thickness = max((nd.size.y if vertical else nd.size.x) for nd in nodes)
        cross_total = sum((nd.size.x if vertical else nd.size.y) for nd in nodes) + gap_x * (len(nodes) - 1)
        total_cross = max(total_cross, cross_total)
        cursor = 0.0
        for nd in nodes:
            if vertical:
                nd.pos = ImVec2(cursor, offset_main + (thickness - nd.size.y) / 2)
                cursor += nd.size.x + gap_x
            else:
                nd.pos = ImVec2(offset_main + (thickness - nd.size.x) / 2, cursor)
                cursor += nd.size.y + gap_x
        # center the layer on the cross axis
        shift = (0 - cross_total) / 2
        for nd in nodes:
            if vertical:
                nd.pos.x += shift
            else:
                nd.pos.y += shift
        offset_main += thickness + gap_y
    # move everything to positive coordinates
    for nd in graph.nodes.values():
        if vertical:
            nd.pos.x += total_cross / 2
        else:
            nd.pos.y += total_cross / 2
    return ImVec2(total_cross, offset_main - gap_y) if vertical else ImVec2(offset_main - gap_y, total_cross)


# =============================================================================
# Drawing
# =============================================================================


def _anchor(node: Node, towards: ImVec2, origin: ImVec2) -> ImVec2:
    """The point of the node's border in the direction of `towards`"""
    cx, cy = origin.x + node.pos.x + node.size.x / 2, origin.y + node.pos.y + node.size.y / 2
    dx, dy = towards.x - cx, towards.y - cy
    if abs(dx) * node.size.y > abs(dy) * node.size.x:
        t = (node.size.x / 2) / abs(dx) if dx else 0
    else:
        t = (node.size.y / 2) / abs(dy) if dy else 0
    return ImVec2(cx + dx * t, cy + dy * t)


def draw(graph: Graph) -> None:
    em = imgui.get_font_size()
    size = layout(graph, em)
    origin = imgui.get_cursor_screen_pos()
    origin = ImVec2(origin.x + em, origin.y + em / 2)
    dl = imgui.get_window_draw_list()
    text_col = imgui.get_color_u32(imgui.Col_.text)
    border = imgui.get_color_u32(imgui.Col_.text, 0.6)
    fill = imgui.get_color_u32(imgui.Col_.frame_bg)
    for e in graph.edges:
        a, b = graph.nodes[e.src], graph.nodes[e.dst]
        ca = ImVec2(origin.x + a.pos.x + a.size.x / 2, origin.y + a.pos.y + a.size.y / 2)
        cb = ImVec2(origin.x + b.pos.x + b.size.x / 2, origin.y + b.pos.y + b.size.y / 2)
        p0, p1 = _anchor(a, cb, origin), _anchor(b, ca, origin)
        dl.add_line(p0, p1, border, 1.5)
        if e.arrow:
            dx, dy = p1.x - p0.x, p1.y - p0.y
            n = max((dx * dx + dy * dy) ** 0.5, 1e-3)
            ux, uy = dx / n, dy / n
            s = 0.5 * em
            dl.add_triangle_filled(p1, ImVec2(p1.x - s * ux + s * 0.5 * uy, p1.y - s * uy - s * 0.5 * ux), ImVec2(p1.x - s * ux - s * 0.5 * uy, p1.y - s * uy + s * 0.5 * ux), border)
        if e.label:
            ts = imgui.calc_text_size(e.label)
            mid = ImVec2((p0.x + p1.x) / 2 - ts.x / 2, (p0.y + p1.y) / 2 - ts.y / 2)
            dl.add_rect_filled(ImVec2(mid.x - 2, mid.y), ImVec2(mid.x + ts.x + 2, mid.y + ts.y), imgui.get_color_u32(imgui.Col_.window_bg))
            dl.add_text(mid, text_col, e.label)
    for node in graph.nodes.values():
        p0 = ImVec2(origin.x + node.pos.x, origin.y + node.pos.y)
        p1 = ImVec2(p0.x + node.size.x, p0.y + node.size.y)
        c = ImVec2((p0.x + p1.x) / 2, (p0.y + p1.y) / 2)
        if node.shape == "diamond":
            pts = [ImVec2(c.x, p0.y), ImVec2(p1.x, c.y), ImVec2(c.x, p1.y), ImVec2(p0.x, c.y)]
            dl.add_convex_poly_filled(pts, fill)  # type: ignore[arg-type]
            dl.add_polyline(pts, border, 1.5, imgui.ImDrawFlags_.closed.value)  # type: ignore[arg-type]
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
        s_ = 0.5 * em
        p_back = ImVec2(tip.x - direction * s_, tip.y)
        if r.arrowhead:
            dl.add_triangle_filled(tip, ImVec2(p_back.x, tip.y - s_ * 0.5), ImVec2(p_back.x, tip.y + s_ * 0.5), line_col)
        else:
            dl.add_line(tip, ImVec2(p_back.x, tip.y - s_ * 0.5), line_col, 1.5)
            dl.add_line(tip, ImVec2(p_back.x, tip.y + s_ * 0.5), line_col, 1.5)
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
graph TD
    A[Markdown text] --> B(md4c parser)
    B --> C{Fenced block?}
    C -->|yes| D[Registered renderer]
    C -->|no| E[imgui_md renderer]
    D --> F[Draw list]
    E --> F
    E --> G[Host services]
    G --> H[Textures, assets, LaTeX]
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
