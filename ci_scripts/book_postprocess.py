"""A pass on the book's built pages (docs/book/_build/html), after `jupyter-book build --html`.

A link with a hash can miss its anchor in two ways:
- The theme (mystmd's book theme 1.2.2, on react-router) can scroll a page back to the top after it hydrates: its
  scroll restoration looks the anchor up at that moment, and scrolls to the top when it misses. Firefox misses on the
  big API pages, so a link to an entry of the API landed on the top of the page.
- The pictures above the anchor push it down as they load: they have no size before. React reports a hydration error
  on every page and renders it again, and the pictures it renders load all at once. Chrome's scroll anchoring
  compensates, not always; Safari did not, and a link on a phone landed a few screens above its entry.
This pass adds a small script to every page: when the URL has a hash, it keeps its element in view while the page
settles, and stops at the reader's first gesture.

The API pages show hundreds of pictures (the demo sections, see api_pages.py): their images load lazily, as the reader
scrolls to them (the theme does not set `loading`), until React renders the page again (see above), without this
attribute.

The links to the ImGui Explorer (its sections, from the API pages and the demos) keep one explorer tab: a link closes
the tab that the previous one opened, then opens its own, in front. The theme renders external links as
`target="_blank" rel="noreferrer"`: a new tab per click, and no handle on it. A named tab
(`window.open(url, "imgui_explorer")`) would be reused instead, but Safari on iOS loads a link into an existing tab in
the background, without showing it (`focus()` does not either): the second link seemed to do nothing. A page reload
loses the handle on the previous tab, which then stays open. A click with a modifier key keeps the browser's own
behavior.

Run by `just doc_build_cf`; idempotent (a marker in each script tag).
"""
import re
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / "docs/book/_build/html"
MARKER = 'id="imgui-bundle-hash-fix"'
SCRIPT = """<script id="imgui-bundle-hash-fix">
// The URL's hash element leaves the view while the page settles (the theme's scroll restoration, the pictures above
// it as they load): scroll back to it whenever it moves, until the reader's first gesture (see
// ci_scripts/book_postprocess.py).
(function () {
  if (!location.hash) return;
  var id = decodeURIComponent(location.hash.slice(1)), done = false, started = Date.now(), lastTop = null;
  var stop = function () { done = true; };
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (e) {
    addEventListener(e, stop, { passive: true, once: true });
  });
  var timer = setInterval(function () {
    if (done || Date.now() - started > 20000) { clearInterval(timer); return; }
    var el = document.getElementById(id);  // looked up each time: React may render the page again
    if (!el) return;
    if (lastTop === null || Math.abs(el.getBoundingClientRect().top - lastTop) > 2) {
      el.scrollIntoView();
      lastTop = el.getBoundingClientRect().top;  // near the page's end, the element may stay below its scroll margin
    }
  }, 100);
})();
</script>
"""
EXPLORER_TAB_MARKER = 'id="imgui-bundle-explorer-tab"'
EXPLORER_TAB_SCRIPT = """<script id="imgui-bundle-explorer-tab">
// The ImGui Explorer's links keep one explorer tab: each closes the previous one's tab, then opens its own, in front
// (see ci_scripts/book_postprocess.py)
(function () {
  var explorerTab = null;
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var link = e.target.closest && e.target.closest('a[href^="https://pthom.github.io/imgui_explorer"]');
    if (!link) return;
    if (explorerTab && !explorerTab.closed) explorerTab.close();
    explorerTab = window.open(link.href, '_blank');
    if (explorerTab) e.preventDefault();
  });
})();
</script>
"""


def main() -> None:
    if not HTML.is_dir():
        sys.exit(f"{HTML} not found: build the book first")
    pages = sorted(HTML.rglob("index.html"))
    done = 0
    for page in pages:
        text = page.read_text()
        if MARKER in text or "</head>" not in text:
            continue
        page.write_text(text.replace("</head>", SCRIPT + "</head>", 1))
        done += 1
    print(f"hash fix: {done} pages of {len(pages)} patched in {HTML}")
    done = 0
    for page in pages:
        text = page.read_text()
        if EXPLORER_TAB_MARKER in text or "</head>" not in text:
            continue
        page.write_text(text.replace("</head>", EXPLORER_TAB_SCRIPT + "</head>", 1))
        done += 1
    print(f"explorer tab: {done} pages of {len(pages)} patched in {HTML}")
    lazy = 0
    for page in sorted((HTML / "api").rglob("index.html")):
        text = page.read_text()
        patched = re.sub(r"<img (?![^>]*\bloading=)", '<img loading="lazy" ', text)
        if patched != text:
            page.write_text(patched)
            lazy += 1
    print(f"lazy images: {lazy} API pages patched")


if __name__ == "__main__":
    main()
