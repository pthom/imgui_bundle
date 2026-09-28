"""Open a LOCAL web page (Emscripten or Pyodide build) in Chrome, run a few actions, take screenshots.

Usage (throwaway environment, nothing installed in the project venv):
    uv run --no-project --with playwright python drive_page.py URL --out PREFIX ACTION [ACTION ...]

Actions, executed in order:
    wait:SECONDS     wait (wasm startup: ~6 s; Pyodide page: ~40 s)
    click:X,Y        mouse click at viewport coordinates (read them on a previous screenshot)
    move:X,Y         move the mouse (ImGui scrolls the hovered window: move before wheel)
    key:KEYS         press keys, Playwright syntax (key:Control+a, key:Enter)
    wheel:DX,DY      mouse wheel scroll (positive DY scrolls down), at the last mouse position
    shot:NAME        save PREFIX_NAME.png
    py:EXPRESSION    Pyodide pages only: evaluate a Python expression with window.pyodide, print the result
    js:EXPRESSION    evaluate a JavaScript expression, print the result (a promise is awaited,
                     e.g. js:navigator.clipboard.readText() after clicking a copy button)

The window is VISIBLE unless --headless is given. It uses the installed Chrome with a throwaway profile.
"""
import argparse
import os
import sys
import threading
from urllib.parse import urlparse

from playwright.sync_api import Page, sync_playwright

VIEWPORT = {"width": 1400, "height": 900}


def click(page: Page, x: float, y: float, visible: bool) -> None:
    # ImGui must see the mouse move on one frame, and the button on the following ones
    page.mouse.move(x - 120, y - 40)
    page.mouse.move(x, y, steps=25 if visible else 2)
    page.wait_for_timeout(500 if visible else 150)
    page.mouse.down()
    page.wait_for_timeout(80)
    page.mouse.up()
    page.wait_for_timeout(1500 if visible else 600)  # with idling, the app redraws slowly


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("actions", nargs="+")
    parser.add_argument("--out", required=True, help="prefix of the screenshots")
    parser.add_argument("--headless", action="store_true", help="no window (ask the user first)")
    parser.add_argument("--console", action="store_true", help="print the page's console messages (Pyodide prints Python's stdout/stderr there)")
    parser.add_argument("--allow-remote", action="store_true", help="allow a page which is not served from this machine")
    parser.add_argument("--timeout", type=float, default=150.0, help="hard limit for the whole run, in seconds")
    args = parser.parse_args()

    host = urlparse(args.url).hostname
    if host not in ("localhost", "127.0.0.1") and not args.allow_remote:
        sys.exit(f"refusing to open a non local page ({host}): pass --allow-remote if the user asked for it")

    # These pages never become idle (render loop): never rely on the browser to exit by itself
    watchdog = threading.Timer(args.timeout, lambda: (print("TIMEOUT: aborting"), os._exit(2)))
    watchdog.daemon = True
    watchdog.start()

    visible = not args.headless
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=args.headless)
        # clipboard permissions: `js:navigator.clipboard.readText()` checks what an ImGui copy button wrote
        context = browser.new_context(viewport=VIEWPORT, permissions=["clipboard-read", "clipboard-write"])  # type: ignore[arg-type]
        page = context.new_page()
        page.on("pageerror", lambda e: print("PAGE ERROR:", str(e)[:200], "\n" + "\n".join((e.stack or "").splitlines()[:25])))
        if args.console:
            page.on("console", lambda m: print(f"CONSOLE {m.type}:", m.text[:300]))
        page.goto(args.url, wait_until="load", timeout=60000)
        for action in args.actions:
            kind, _, value = action.partition(":")
            if kind == "wait":
                page.wait_for_timeout(float(value) * 1000)
            elif kind == "click":
                x, y = (float(v) for v in value.split(","))
                click(page, x, y, visible)
            elif kind == "move":
                x, y = (float(v) for v in value.split(","))
                page.mouse.move(x, y, steps=10 if visible else 2)
                page.wait_for_timeout(300)
            elif kind == "key":
                page.keyboard.press(value)
                page.wait_for_timeout(600)
            elif kind == "wheel":
                dx, dy = (float(v) for v in value.split(","))
                page.mouse.wheel(dx, dy)
                page.wait_for_timeout(1500 if visible else 600)
            elif kind == "shot":
                path = f"{args.out}_{value}.png"
                page.screenshot(path=path)
                print("screenshot:", path)
            elif kind == "py":
                print(f"py {value!r} ->", page.evaluate("code => window.pyodide.runPython(code)", value))
            elif kind == "js":
                print(f"js {value!r} ->", page.evaluate(value))
            else:
                sys.exit(f"unknown action: {action}")
        browser.close()
    watchdog.cancel()
    print("done, browser closed")


if __name__ == "__main__":
    main()
