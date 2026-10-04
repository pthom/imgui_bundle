"""A pass on the book's built pages (docs/book/_build/html), after `jupyter-book build --html`.

The theme (mystmd's book theme, on react-router) can scroll a page back to the top after it hydrates, when the URL
has a hash: its scroll restoration looks the anchor up at that moment, and scrolls to the top when it misses. Firefox
misses on the big API pages (React reports a hydration error there and renders the page again), so a link to an entry
of the API landed on the top of the page. This pass adds a small script to every page: when the URL has a hash, it
re-applies it once the page has settled, and stops at the reader's first gesture.

Run by `just doc_build_cf`; idempotent (a marker in the script tag).
"""
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


if __name__ == "__main__":
    main()
