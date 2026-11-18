"""Touch check of the playground, in headless Chrome with a phone's touch screen: one finger scrolls a document by the
length of its drag, and two fingers that spread scale the font.

It catches a touch layer that miscounts the fingers: a finger that reaches it twice turns a one-finger drag into a
two-finger gesture (no scroll, a zoom, or a scroll too fast).

Usage:
    uv run --no-project --with playwright python ci_scripts/playground_touch_check.py [TARGET]
    just cf_touch_check [TARGET]

TARGET: a folder that holds playground/ and local_wheels/ (default: _cf_staging, the staged site; also
pyodide_projects/projects), served on a free port of 127.0.0.1; or a site's URL (https://imgui-bundle.pages.dev/).

It drives the installed Google Chrome (Playwright's channel "chrome"), with touch events sent through the DevTools
protocol, and reads Dear ImGui's state from inside the page, through Pyodide. Exit status 0 when every check passes.
"""

import functools
import http.server
import json
import sys
import threading
import time
from typing import Any

from playwright.sync_api import CDPSession, Page, ViewportSize, sync_playwright

DEMO = "demo_imgui_md_document.py"  # a long document: its content is the page's only scroll area
VIEWPORT: ViewportSize = {"width": 390, "height": 844}  # a phone, in CSS pixels
DRAG = 150  # the one-finger drag, upward, in CSS pixels
SPREAD = (40, 120)  # the pinch: each finger's distance to the center, at its start and at its end (CSS pixels)
STEPS = 15  # touch moves per gesture, one every MOVE_DELAY seconds
MOVE_DELAY = 0.033
STARTUP_TIMEOUT = 150  # seconds: Pyodide, the wheel, the demo

STATE_PY = r"""
import json
from imgui_bundle import imgui
scrolls = [w.scroll.y for w in imgui.get_current_context().windows if w.was_active and w.scroll_max.y > 0]
json.dumps({
    "frame": imgui.get_frame_count(),
    "scrolls": scrolls,
    "font_scale": imgui.get_style().font_scale_main,
    "mouse_down": bool(imgui.get_io().mouse_down[0]),
    "display_width": imgui.get_io().display_size.x,
})
"""


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 (the base class's name)
        pass


def serve(folder: str) -> str:
    handler = functools.partial(QuietHandler, directory=folder)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_port}/"


def state(page: Page) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(page.evaluate("(code) => pyodide.runPython(code)", STATE_PY))
    return result


def wait_for_app(page: Page) -> None:
    """Wait until the demo runs: its frames advance."""
    start = time.time()
    while time.time() - start < STARTUP_TIMEOUT:
        try:
            f1 = state(page)["frame"]
            time.sleep(1.0)
            if state(page)["frame"] > f1 > 5:
                time.sleep(2.0)  # the document's layout settles
                return
        except Exception:  # Pyodide or the demo not loaded yet
            time.sleep(1.0)
    raise TimeoutError(f"the demo did not start within {STARTUP_TIMEOUT} s")


def touch(cdp: CDPSession, kind: str, points: list[tuple[float, float]]) -> None:
    touch_points = [{"x": x, "y": y, "id": i + 1} for i, (x, y) in enumerate(points)]
    cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": touch_points})


def move_fingers(cdp: CDPSession, starts: list[tuple[float, float]], ends: list[tuple[float, float]]) -> None:
    """Fingers down at starts, then moved to ends: they stay down."""
    touch(cdp, "touchStart", starts)
    time.sleep(0.05)
    for step in range(1, STEPS + 1):
        t = step / STEPS
        touch(cdp, "touchMove", [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) for (x0, y0), (x1, y1) in zip(starts, ends)])
        time.sleep(MOVE_DELAY)


def lift_fingers(cdp: CDPSession) -> None:
    touch(cdp, "touchEnd", [])
    time.sleep(1.0)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "_cf_staging"
    base = target if target.startswith("http") else serve(target)
    url = f"{base.rstrip('/')}/playground/?demo={DEMO}"
    print(f"Touch check: {url}")
    results: list[tuple[str, bool]] = []

    with sync_playwright() as p:
        # SwiftShader gives headless Chrome its WebGL
        browser = p.chromium.launch(channel="chrome", headless=True,
                                    args=["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=3, is_mobile=True, has_touch=True)
        page = context.new_page()
        page.goto(url, timeout=60000)
        wait_for_app(page)
        cdp = context.new_cdp_session(page)
        box = page.evaluate("(() => { const r = document.getElementById('canvas').getBoundingClientRect();"
                            " return [r.x, r.y, r.width, r.height]; })()")
        cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2

        # One finger, upward, on the document's text
        before = state(page)
        if len(before["scrolls"]) != 1:
            print(f"  expected one scroll area, found {len(before['scrolls'])}")
            return 1
        x, y = cx, box[1] + box[3] * 0.7
        move_fingers(cdp, [(x, y)], [(x, y - DRAG)])
        held = state(page)
        lift_fingers(cdp)
        after = state(page)
        expected = DRAG * before["display_width"] / box[2]  # CSS pixels to Dear ImGui's units
        scrolled = after["scrolls"][0] - before["scrolls"][0]
        results.append((f"one finger: a drag of {expected:.0f} scrolls by {scrolled:.1f}",
                        abs(scrolled - expected) <= 3))
        results.append((f"one finger: the press reaches Dear ImGui (mouse down: {held['mouse_down']})",
                        held["mouse_down"]))
        results.append((f"one finger: the font scale stays at 1 ({after['font_scale']:.2f})",
                        abs(after["font_scale"] - 1.0) < 0.01))

        # Two fingers that spread, around the center
        (s0, s1) = SPREAD
        move_fingers(cdp, [(cx - s0, cy), (cx + s0, cy)], [(cx - s1, cy), (cx + s1, cy)])
        lift_fingers(cdp)
        pinched = state(page)
        scales = f"{after['font_scale']:.2f} -> {pinched['font_scale']:.2f}"
        results.append((f"two fingers: a pinch scales the font ({scales})", pinched["font_scale"] > 1.2))
        browser.close()

    for label, ok in results:
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
