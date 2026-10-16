"""A pass on the book's built pages (docs/book/_build/html), after `jupyter-book build --html`.

The theme (mystmd's book theme, on react-router) can scroll a page back to the top after it hydrates, when the URL
has a hash: its scroll restoration looks the anchor up at that moment, and scrolls to the top when it misses. Firefox
misses on the big API pages (React reports a hydration error there and renders the page again), so a link to an entry
of the API landed on the top of the page. This pass adds a small script to every page: when the URL has a hash, it
re-applies it once the page has settled, and stops at the reader's first gesture.

The API pages show hundreds of pictures (the demo sections, see api_pages.py): their images load lazily, as the reader
scrolls to them (the theme does not set `loading`).

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
// The theme's scroll restoration may scroll back to the top after hydration (seen in Firefox): re-apply the URL's
// hash once the page has settled, until the reader scrolls (see ci_scripts/book_postprocess.py).
(function () {
  if (!location.hash) return;
  var id = decodeURIComponent(location.hash.slice(1)), done = false, started = Date.now();
  var stop = function () { done = true; };
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (e) {
    addEventListener(e, stop, { passive: true, once: true });
  });
  var timer = setInterval(function () {
    if (done || Date.now() - started > 6000) { clearInterval(timer); return; }
    var el = document.getElementById(id);
    if (el && window.scrollY < 2 && el.getBoundingClientRect().top > 150) el.scrollIntoView();
  }, 250);
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
