"""Lazy download of LaTeX math fonts in Pyodide builds.

Desktop wheels bundle the Latin Modern Math fonts under
``imgui_bundle/assets/fonts/latex/`` (876 KB total). Pyodide wheels
exclude them via ``IMGUI_BUNDLE_SLIM_PYODIDE_WHEEL=1`` (see
``pyproject.toml``) and instead download them on first use to keep
the wheel small.

The download is triggered by ``immapp.run(with_latex=True)`` (and the
async / notebook variants) via patches installed in
``pyodide_patch_runners.py``. The fetch is gated on ``with_latex`` so
that users who do not need LaTeX never pay the cost.

Files are written into the same on-disk path the desktop wheel would
use (``<package>/assets/fonts/latex/``), so the C++ wrapper's
``HelloImGui::AssetFileFullPath("fonts/latex/...")`` lookup finds them
without needing any C++ change.

Failure mode: if all download URLs fail, an error is logged to the
JS console and the GUI starts anyway. The C++ wrapper
(``imgui_md_wrapper.cpp::EnsureMicroTeXInitialized``) then detects the
missing assets via ``HelloImGui::AssetExists`` and falls back to
rendering the LaTeX source as plain text inside the markdown, instead
of crashing on the asset lookup.
"""
from __future__ import annotations

import os

# Pin to a stable git tag so jsdelivr serves an immutable, edge-cached
# version of the fonts. The tag points at a known-good repo state and
# is bumped manually if the font files ever change (essentially never:
# Latin Modern Math is from ~2014). Bump to ``latex-fonts-v2`` if you
# rename or replace the font files.
_FONTS_REPO_REF = "latex-fonts-v1"

# Fallback chain. Each entry is a base URL; the file name is appended.
# Tried in order until one succeeds.
_FONTS_BASE_URLS: tuple[str, ...] = (
    f"https://cdn.jsdelivr.net/gh/pthom/imgui_bundle@{_FONTS_REPO_REF}/imgui_bundle_assets/fonts/latex",
    f"https://raw.githubusercontent.com/pthom/imgui_bundle/{_FONTS_REPO_REF}/imgui_bundle_assets/fonts/latex",
)

# Files to fetch.
_FONT_FILES: tuple[str, ...] = (
    "latinmodern-math.clm1",
    "latinmodern-math.otf",
)


def _fonts_target_dir() -> str:
    """Return the on-disk directory where the fonts should live.

    Matches the desktop wheel layout, so the C++ asset lookup
    ``HelloImGui::AssetFileFullPath("fonts/latex/...")`` finds them
    without any further configuration.
    """
    here = os.path.dirname(__file__)
    return os.path.join(here, "assets", "fonts", "latex")


def _fonts_present() -> bool:
    target = _fonts_target_dir()
    return all(os.path.exists(os.path.join(target, f)) for f in _FONT_FILES)


async def _pyfetch_bytes(url: str) -> bytes:
    """Fetch ``url`` as bytes via Pyodide's ``pyfetch``. Raises on non-200."""
    import pyodide.http  # type: ignore[import-not-found]

    resp = await pyodide.http.pyfetch(url)
    if resp.status != 200:
        raise RuntimeError(f"HTTP {resp.status} for {url}")
    return await resp.bytes()


async def _download_one(fname: str, target_dir: str) -> None:
    """Download a single font file, trying each base URL in order."""
    last_error: Exception | None = None
    for base in _FONTS_BASE_URLS:
        url = f"{base}/{fname}"
        try:
            data = await _pyfetch_bytes(url)
        except Exception as e:  # noqa: BLE001
            last_error = e
            continue
        out_path = os.path.join(target_dir, fname)
        with open(out_path, "wb") as f:
            f.write(data)
        return
    assert last_error is not None
    raise RuntimeError(
        f"All download URLs failed for {fname}: {last_error}"
    )


async def ensure_fonts_async() -> None:
    """Make sure the LaTeX font files exist on disk. No-op if already present.

    Called from the patched Pyodide runners before the GUI starts when
    ``with_latex=True``. Safe to call multiple times: subsequent calls
    return immediately if both font files already exist.

    Raises ``RuntimeError`` if any font fails to download from every
    URL in the fallback chain. Callers in ``pyodide_patch_runners.py``
    catch this and log to the JS console without aborting the app.
    """
    if _fonts_present():
        return
    target_dir = _fonts_target_dir()
    os.makedirs(target_dir, exist_ok=True)
    for fname in _FONT_FILES:
        await _download_one(fname, target_dir)
