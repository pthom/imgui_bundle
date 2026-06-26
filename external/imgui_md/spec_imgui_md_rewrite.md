# Advanced fork of imgui_md

## Draft of the specs

ImGui Bundle uses a highly customized and improved version of imgui_md (https://github.com/mekhontsev/imgui_md).
We are using a fork at https://github.com/pthom/imgui_md

* 3 commits in the original repos, much more in the current fork
* there is a wrapper that adds: an easy API, a derivate of imgui_md (for implem only reasons)

This new versions offers many advancements:
- Auto load fonts (bold, italic, code, etc)
- supports image loading
- supports LaTeX
- more md blocks are supported
etc etc

This version is tightly integrated into ImGui Bundle and uses HelloImGui.

My goal: publish a fork or a branch of imgui_md with most of the change which would work standalone
- should work without ImGui Bundle & Hello ImGui. However, ImGui Bundle should be able to use it.
- should provide tools to ease loading the fonts (maybe provides fonts)
- should work with images (and provide tooling to link with curl on desktop.
  Ideally also provide alternative for emscripten. See what imgui bundle does)
- Should be nicely documented, with examples and a readme
- etc.


---

## 1. Goal and guiding principle

Publish a **standalone repo** (renderer + a default, callback-driven wrapper) that builds against
plain Dear ImGui + md4c, and which ImGui Bundle then consumes as a submodule.

The guiding principle: **everything that today requires HelloImGui / ImmApp becomes a pluggable
seam** (a callback or a small backend struct) with a no-dependency default. ImGui Bundle stops
being the *host* of imgui_md and becomes one *consumer* that injects richer backends through those
seams.

"Standalone" does **not** mean zero-dependency. It means: depends only on Dear ImGui + md4c by
default; richer features (syntax highlight, LaTeX, image upload, URL download) are optional backends
that the user (or the bundle) wires in.


## 2. Current architecture (starting point)

```
external/imgui_md/
├── imgui_md/            ← low-level renderer (fork of mekhontsev/imgui_md)
│   ├── imgui_md.{h,cpp} ← base class + md4c callbacks. Depends only on imgui + md4c
│   └── (md4c parser lives in ../md4c)
├── imgui_md_wrapper/    ← the "easy API" (namespace ImGuiMd)
│   ├── imgui_md_wrapper.{h,cpp}      ← fonts, images, code highlight, latex, callbacks
│   └── imgui_md_url_download.{h,cpp} ← libcurl / emscripten image download
└── bindings/            ← Python bindings (litgen)
```

* **Renderer layer** (`imgui_md/`) is already almost standalone: it includes only `imgui.h` and
  `md4c.h`, and exposes all extension points as `virtual` overrides. Our fork added a lot here
  (admonitions, task lists, LaTeX spans, `<details>`/`<pre>`/`<summary>`, table cell alignment,
  quote bars, header spacing). **This is the layer worth upstreaming to mekhontsev/imgui_md.**
* **Wrapper layer** (`imgui_md_wrapper/`) is where all the ImGui-Bundle coupling lives. It already
  expresses most concerns as callbacks (`MarkdownCallbacks`), but the *default implementations*
  require HelloImGui. The rewrite is mostly about replacing those defaults with plain-ImGui ones.


## 3. Coupling inventory (what must be decoupled)

| Concern         | Current dependency                                            | Resolution                                    |
|-----------------|---------------------------------------------------------------|-----------------------------------------------|
| Font loading    | `HelloImGui::LoadFontTTF[_WithFontAwesomeIcons]`, `AssetExists`| Ship Roboto + plain `AddFontFromFileTTF` loader (§4.1) |
| Local images    | `HelloImGui::ImageAndSizeFromAsset/FromEncodedData`, `FreeImageCache` | stb_image decode + texture-backend struct (§4.2) |
| Asset paths     | `HelloImGui::AssetFileFullPath`                                | Caller-supplied file paths                    |
| URL download    | libcurl (`DesktopDownloadData`) + emscripten fetch            | Keep; already `#ifdef`-gated and callback-driven (§4.3) |
| Code highlight  | `immapp/snippets.h` (ImGuiColorTextEdit)                      | Plain monospaced default; highlight is optional backend (§4.4) |
| LaTeX           | `imgui_microtex` + HelloImGui asset lookup                    | Keep `#ifdef`; take explicit font paths (§4.5) |
| Open URL        | `ImmApp::BrowseToUrl`                                          | Inline ~10-line platform code (§4.6)          |
| String utils    | `fplus` (split/trim/join/to_lower)                            | Small std helpers (§4.6)                       |
| Unindent        | `CodeUtils::UnindentMarkdown`                                 | Small std helper (§4.6)                        |


## 4. Per-feature specification

### 4.1 Fonts — bundle Roboto + optional loader + merge-font API

* Ship the Roboto family (Regular/Bold/Italic/BoldItalic) and a code font in the repo's `fonts/`.
* Provide an **opt-in** loader that uses plain `io.Fonts->AddFontFromFileTTF` (no HelloImGui).
  A user who already manages fonts overrides `GetFont(MarkdownFontSpec)` and ignores the loader.
* The wrapper builds its own set of md fonts: regular, bold, italic, bold-italic, code, and h1–h6
  (sized via `MarkdownFontOptions::headerSizeFactors`).

**No bundled FontAwesome.** Instead, add a **merge-font API** so a user can merge their own icon
(or any) font into *every* md font:

* Primary (declarative) form — a config field:
  `MarkdownFontOptions::mergeFonts` = list of `{ path, glyphRanges (optional), sizeOffset (optional) }`.
  Each entry is merged (`MergeMode = true`) into each md font as it is created. Declarative so it
  replays correctly on a font reload.
* Convenience (imperative) wrapper: `ImGuiMd::AddMergeFontToAllMarkdownFonts(path, ...)`.

**Consequence — admonition / heading icons:** today the icons come from FontAwesome merged inside
`LoadFontTTF_WithFontAwesomeIcons`. With no bundled FA, the renderer must **fall back to text labels**
(`NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`) when the icon glyph is absent. ImGui Bundle gets
its icons back "for free" by merging FontAwesome through this same `mergeFonts` API. (See §4.7.)


### 4.2 Local images — stb_image decode + texture-backend struct

Decouple decode from GPU upload:

1. The wrapper reads image bytes (from a file path, or from a URL via §4.3).
2. stb_image decodes them into an **RGBA8 pixel buffer** `(pixels, w, h)`.
3. A user-supplied backend uploads that buffer to a backend-specific texture and, later, releases it.

Because the standalone cannot know the active render backend (GL/Vulkan/Metal/DX) or own the GPU
texture lifetime, the upload **and** release are both provided by the caller as a small struct:

```
struct MarkdownTextureBackend {
    // RGBA8 buffer -> texture id. Return invalid id on failure.
    std::function<ImTextureID(const uint8_t* rgba, int w, int h)> upload;
    // Release a texture previously returned by upload. Called from the
    // image cache on DeInitializeMarkdown / reload.
    std::function<void(ImTextureID)> release;
};
```

* Both fields optional. If `upload` is null, images are **skipped** (alt-text / placeholder shown),
  matching upstream's "user provides images" philosophy.
* The wrapper owns an image cache keyed by path/URL; on teardown or reload it calls `release` for
  every cached texture (fixes the lifetime gap that `HelloImGui::FreeImageCache` covers today).
* URL images (§4.3) funnel through the **same** decode + upload path.

ImGui Bundle injects a `MarkdownTextureBackend` wrapping HelloImGui's texture upload/free. A plain-GL
user writes ~10 lines (glGenTextures/glTexImage2D + glDeleteTextures).

**Ship a ready-made OpenGL backend in v1** behind `IMGUI_RICHMD_WITH_GL_IMAGES` (off by default),
so the common OpenGL case (glGenTextures/glTexImage2D + glDeleteTextures) needs zero user code: the
user just enables the option and gets a working `MarkdownTextureBackend`.


### 4.3 URL image download — keep as-is (already the model seam)

This is already cleanly factored and is the template the rest should follow:

* `MarkdownCallbacks::OnDownloadData(url) -> MarkdownDownloadResult` is the seam.
  Contract (per-frame poll until `Ready`/`Failed`, then cached) stays unchanged.
* Optional desktop backend `DesktopDownloadData` (libcurl, threaded) behind
  `#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES`.
* Optional emscripten-fetch backend behind the existing `__EMSCRIPTEN__` path.
* Python injects urllib / pyodide through `OnDownloadData`.

No HelloImGui involved. Standalone CMake just needs to isolate the libcurl `find_package` behind the
option. Downloaded bytes go to the §4.2 decode + upload path.


### 4.4 Code blocks — plain monospaced default, highlighting is optional

* Standalone default = **plain monospaced code block** using the code font, via the existing
  `imgui_md::render_code_block()` virtual. No syntax coloring, no ImGuiColorTextEdit.
* Drop the hard `immapp/snippets.h` dependency. Syntax highlighting (with language detection:
  cpp/c/python/glsl/sql/lua/angelscript) becomes an **optional backend** the bundle injects, or a
  `WITH_HIGHLIGHT` CMake option that pulls ImGuiColorTextEdit.
* This removes the single heaviest non-essential dependency from the default build.


### 4.5 LaTeX (MicroTeX) — vendor as optional component, reuse the texture seam

Current layout (already partly decoupled):

* **`MicroTeX/`** (the TeX engine) is *already a git submodule* (`github.com/pthom/MicroTeX.git`,
  branch `imgui_bundle`). Requires **FreeType**.
* **`imgui_microtex/`** (the ImGui+FreeType backend) has two API levels:
  * **Level 1:** `LaTeX → RGBA pixel buffer` — *no HelloImGui*.
  * **Level 2:** `LaTeX → HelloImGui::TextureGpuPtr` (cached) — the *only* HelloImGui coupling
    (`hello_imgui/texture_gpu.h`, `CreateTextureGpuFromRgbaData`).

**Key insight:** Level 1's RGBA buffer is exactly the input to the §4.2 `MarkdownTextureBackend::upload`.
So LaTeX needs no texture machinery of its own — render to RGBA (Level 1), then push through the same
upload/release seam as images. **Drop the Level-2 HelloImGui API.** One texture seam serves both
images and math.

**Packaging decision: vendor `imgui_microtex/` into the standalone repo** as an optional component,
with `MicroTeX` as a nested submodule, behind `IMGUI_RICHMD_WITH_LATEX` (off by default). FreeType is
required only when the option is ON: standalone does `find_package(Freetype)`; the bundle keeps
getting it via hello_imgui. This makes LaTeX work out-of-the-box for standalone users who opt in,
which is the "include it there" goal.

Remaining decoupling work:

* Rewrite `imgui_microtex` to expose only Level 1 (RGBA), routing the upload through the §4.2 backend.
* Replace the HelloImGui asset-path lookup (`AssetFileFullPath`) for MicroTeX's `.clm` / `.otf`
  font files with **explicit file paths** supplied by the caller.
* Keep lazy-init on first math span, and the existing text-label fallback when MicroTeX is
  unavailable.

*(Alternatives considered: callback-only seam with no vendored MicroTeX — lighter but LaTeX isn't
"easily available" standalone; imgui_microtex as its own separate repo — cleanest but requires
extracting it from the bundle now. Chose vendoring as the balance.)*


### 4.6 Small utilities — inline, drop deps

* `ImmApp::BrowseToUrl` → inline ~10 lines of platform `#ifdef`
  (`ShellExecute` / `open` / `xdg-open` / emscripten `window.open`). Removes the immapp dep for links.
* `fplus` (split_lines / trim_whitespace / join / to_lower_case) → small std helpers.
* `CodeUtils::UnindentMarkdown` → small std helper (used by `RenderUnindented`).


### 4.7 Renderer-layer features (the upstream-PR candidate)

These already live in `imgui_md/` (imgui + md4c only) and should be preserved and, ideally,
upstreamed: GitHub admonitions (`> [!NOTE]` …), task lists, LaTeX spans (`$…$`, `$$…$$`),
`<details>`/`<summary>`/`<pre>` HTML blocks, table cell alignment, quote vertical bars, header
spacing, autolinks, `set_flag()` for md4c flags. The only standalone-relevant change here is the
admonition **text fallback** from §4.1.


## 5. Proposed standalone repo structure

```
imgui_md (standalone repo)
├── imgui_md/         ← renderer (imgui + md4c only)        ← also the upstream-PR candidate
├── imgui_md_wrapper/ ← easy API, callback-driven, plain-ImGui defaults
│   └── backends/     ← optional: gl_images, curl_download, microtex, highlight
├── md4c/             ← git submodule (the parser)
├── imgui_microtex/   ← optional LaTeX component (WITH_LATEX); MicroTeX as a nested submodule
├── fonts/            ← Roboto family + code font  (no FontAwesome)
├── examples/         ← standalone demo (no bundle, no HelloImGui)
├── README.md         ← docs + examples
└── CMakeLists.txt    ← options below
```

CMake options (all default OFF in standalone, the bundle turns on what it needs):

* `IMGUI_RICHMD_WITH_LATEX`           — MicroTeX math rendering
* `IMGUI_RICHMD_WITH_HIGHLIGHT`       — ImGuiColorTextEdit syntax highlighting
* `IMGUI_RICHMD_WITH_GL_IMAGES`       — ready-made OpenGL texture backend
* `IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES` — libcurl URL download backend

ImGui Bundle consumes the repo as a submodule and injects its HelloImGui-based backends (fonts via
HelloImGui, images via its texture cache + `MarkdownTextureBackend`, highlighting via Snippets,
URL download via its existing path) through the seams above.


## 6. Resolved decisions

* **GL image backend** (§4.2): **ship in v1** behind `IMGUI_RICHMD_WITH_GL_IMAGES` (off by default).
* **md4c packaging** (§5): **git submodule**.
* **MicroTeX packaging** (§4.5): **vendor `imgui_microtex/` as an optional component** (nested
  MicroTeX submodule), behind `IMGUI_RICHMD_WITH_LATEX`; reuse the §4.2 texture seam; drop the
  Level-2 HelloImGui API.
* **Upstreaming** (§4.7): a PR to mekhontsev/imgui_md is a **later** step, not part of this effort.
* **Python bindings**: **stay in ImGui Bundle** (no litgen setup duplicated into the standalone repo).


## 7. Suggested milestones

1. **Decouple in place** — replace the wrapper's HelloImGui/immapp/fplus defaults with seams +
   plain-ImGui defaults, *inside the current bundle tree*, behind the CMake options above. Verify the
   bundle still builds and renders identically (bundle injects its backends).
2. **Extract** — move `imgui_md/` + `imgui_md_wrapper/` + `fonts/` + a standalone example into the
   new repo; build it against plain ImGui with a minimal backend (GLFW+GL example).
3. **Document** — README, examples, font/merge/image/latex how-tos.
4. **(Later) Upstream** the renderer-layer diffs to mekhontsev/imgui_md.
