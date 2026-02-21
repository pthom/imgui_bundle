# Plan: Lazy Loading of Demo Code Files

## Problem

All demo source files (~4.7 MB uncompressed, ~1 MB gzip) are currently preloaded
into Emscripten's MEMFS at startup before `main()` runs, adding ~1 MB to the
startup download. On desktop the files are copied at CMake configure-time into
`assets/demo_code/` with an awkward `.txt` suffix.

## Goals

1. Remove demo code files from Emscripten preloaded assets → lazy-fetch on demand
2. Change asset naming from `.txt` suffix to natural extensions (`.cpp`, `.py`, `.h`, `.pyi`)
3. Desktop: read lazily via `std::ifstream` from `demo_code/` folder outside `assets/`
4. Emscripten: fetch lazily via `emscripten_async_wget()` from the server

## Out of Scope (follow-up)

- Lazy loading `demos_cpp/` and `demos_python/` in the full bundle demo
- Python `show_imgui_manual_gui()` lazy loading
- Persistent cache across sessions (browser HTTP cache handles this)

---

## Core Architecture

### `demo_code/` folder — outside `assets/`

Files live in `external/imgui_manual/imgui_manual/demo_code/` with **natural extensions**.
This folder is **not tracked by git** (only `.gitkeep` is tracked) and is populated
by CMake at configure time via `iman_setup_demo_code_dir()`.

Key reason: files in `assets/` would be bundled into `index.data` at build time
(via `--preload-file`), defeating the purpose of lazy loading.

### Platform split

```
Desktop:
  Tab shown
    → LoadState = NotLoaded
    → LoadFile() called
    → std::ifstream(IMAN_DEMO_CODE_DIR + "/" + filename)
    → PopulateEditor() → LoadState = Loaded

Emscripten:
  Tab shown
    → LoadState = NotLoaded
    → RequestFileLoad() called
    → emscripten_async_wget(cppFetchUrl(), "/demo_code/filename", onLoad, onError)
    → [spinner shown while downloading]
    → onLoad callback → LoadFile() reads from MEMFS via LoadAssetFileData
    → PopulateEditor() → LoadState = Loaded
```

### `cppFetchUrl()` / `pyFetchUrl()`

Used as the server-relative URL for `emscripten_async_wget()` and as the MEMFS path
after download. e.g. `"demo_code/imgui_demo.cpp"`.

### `IMAN_DEMO_CODE_DIR`

CMake compile definition (desktop only): absolute path to `demo_code/` folder.
e.g. `/path/to/external/imgui_manual/imgui_manual/demo_code`

---

## Data Structure Changes

### `library_config.h` — `DemoFileInfo`

```cpp
struct DemoFileInfo {
    std::string baseName;
    bool hasPython       = false;
    bool isApiReference  = false;
    std::string cppGithubUrl;
    std::string pyGithubUrl;

    std::string cppDisplayName() const;  // e.g. "imgui_demo.cpp" or "imgui.h"
    std::string pyDisplayName() const;   // e.g. "imgui_demo.py" or "imgui.pyi"

    // Fetch URL for emscripten_async_wget (e.g. "demo_code/imgui_demo.cpp")
    // Desktop reads via std::ifstream(IMAN_DEMO_CODE_DIR + "/" + cppDisplayName())
    std::string cppFetchUrl() const;
    std::string pyFetchUrl() const;

    // REMOVED: cppAssetName(), pyAssetName()
};
```

### `demo_code_viewer.cpp` — `CodeFile` and `LoadState`

```cpp
enum class LoadState { NotLoaded, Loading, Loaded, Failed };

struct CodeFile {
    LoadState cppState = LoadState::NotLoaded;
    LoadState pyState  = LoadState::NotLoaded;
    std::string cppContent;
    std::string pyContent;
    TextEditor  cppEditor;
    TextEditor  pyEditor;
    std::map<std::string, int> pyMarkers;
    // Removed: bool cppLoaded, bool pyLoaded
};
```

---

## Loading Logic

### `PopulateEditor()` — shared helper

Sets up `TextEditor` from content string; updates `cppContent`/`pyContent` and `LoadState`.

### `LoadFile()` — desktop synchronous load

```cpp
void LoadFile(const DemoFileInfo& fileInfo)
{
    CodeFile& cf = g_codeFiles[fileInfo.baseName];
#ifndef __EMSCRIPTEN__
    auto loadOne = [&](const std::string& filename, LoadState& state, bool isPython)
    {
        if (state != LoadState::NotLoaded) return;
        state = LoadState::Loading;
        std::string path = std::string(IMAN_DEMO_CODE_DIR) + "/" + filename;
        std::ifstream f(path);
        if (f) {
            std::string content(std::istreambuf_iterator<char>(f), {});
            PopulateEditor(cf, content, isPython);
        } else {
            state = LoadState::Failed;
        }
    };
    loadOne(fileInfo.cppDisplayName(), cf.cppState, false);
    if (fileInfo.hasPython)
        loadOne(fileInfo.pyDisplayName(), cf.pyState, true);
#endif
}
```

### `RequestFileLoad()` — Emscripten async (Step 3)

```cpp
#ifdef __EMSCRIPTEN__
void RequestFileLoad(const DemoFileInfo& fileInfo)
{
    CodeFile& cf = g_codeFiles[fileInfo.baseName];
    auto fetchOne = [&](const std::string& url, LoadState& state)
    {
        if (state != LoadState::NotLoaded) return;
        state = LoadState::Loading;
        std::string localPath = "/" + url;
        emscripten_async_wget(url.c_str(), localPath.c_str(), OnWgetLoad, OnWgetError);
    };
    fetchOne(fileInfo.cppFetchUrl(), cf.cppState);
    if (fileInfo.hasPython)
        fetchOne(fileInfo.pyFetchUrl(), cf.pyState);
}
#endif
```

### `DemoCodeViewer_Show()` — trigger load

```cpp
#ifdef __EMSCRIPTEN__
    RequestFileLoad(currentFile);
#else
    LoadFile(currentFile);
#endif
```

---

## CMake Changes

### `imgui_manual_build.cmake`

- `iman_setup_demo_code_dir()`: copies all files to `demo_code/` with **natural extensions** (no `.txt`)
- `iman_copy_demo_code_assets()`: kept for Python package (still uses `.txt` — separate effort)
- `iman_add_imgui_manual_lib()`: adds `IMAN_DEMO_CODE_DIR` compile definition (desktop only)
- `iman_main()`: calls `iman_setup_demo_code_dir()` then `iman_add_imgui_manual_app()`; no asset copy for the app

### `.gitignore` (imgui_manual)

```
assets/demo_code/*.txt     # old — keep until Step 2 removes those files
demo_code/*                # new — CMake-populated, not tracked
!demo_code/.gitkeep        # keep the placeholder
```

### `justfile` (Step 3)

Add `_copy_demo_code` recipe for Emscripten serve/deploy (copies files to `demo_code/` alongside the `.wasm`).

---

## Files Changed

| File | Change |
|------|--------|
| `library_config.h` | Remove `cppAssetName/pyAssetName`; add `cppFetchUrl()/pyFetchUrl()` |
| `demo_code_viewer.cpp` | `LoadState`, `PopulateEditor()`, `LoadFile()` via `std::ifstream`; Step 3 adds `RequestFileLoad()` |
| `imgui_manual_build.cmake` | `iman_setup_demo_code_dir()`, `IMAN_DEMO_CODE_DIR`, reordered `iman_main()` |
| `demo_code/.gitkeep` | New placeholder file |
| `.gitignore` (imgui_manual) | Add `demo_code/*` + `!.gitkeep` |
| `justfile` | Step 3: `_copy_demo_code` recipe; update serve/deploy |

---

## Implementation Steps

### Step 1 — Desktop lazy load ✅
- `library_config.h`: `cppFetchUrl()/pyFetchUrl()` ✅
- `demo_code_viewer.cpp`: `LoadState`, `CodeFile`, `PopulateEditor()`, `LoadFile()` via `std::ifstream` ✅
- `imgui_manual_build.cmake`: `iman_setup_demo_code_dir()`, `IMAN_DEMO_CODE_DIR` ✅
- `demo_code/.gitkeep` + `.gitignore` ✅
- **→ Build `builds/claude_manual_desktop` and verify**

### Step 2 — Remove old `.txt` files from git ✅
- Folders deleted by user; no tracked files remained.

### Step 3 — Emscripten async fetch ✅
- `RequestFileLoad()` via `emscripten_async_wget()` added
- `/demo_code/` MEMFS dir created once at first fetch
- `manual_ems_serve`/`manual_ems_deploy` updated
- Verified: code viewer works on both desktop and Emscripten

im### Step 4 — Deploy
- `just manual_ems_deploy`
- Verify live site: `index.data` smaller, per-file XHR on tab switch
