# Refactor IMGUI_DEMO_MARKER: eliminate force-include, use per-file identifier

## Context

The `IMGUI_DEMO_MARKER` macro is used throughout demo files (imgui, implot, implot3d, imanim) to mark code sections for the interactive code browser in imgui_manual. Currently, the bundle uses a **force-include** mechanism (`-include` compiler flag) to override the empty fallback macro with a real implementation from `imgui_demo_marker_hooks.h`. This is fragile, non-portable, and uses `__FILE__` which leaks developer paths.

**Goal:** Replace force-include with a self-contained per-file `#define IMGUI_DEMO_MARKER_FILE "name"` pattern. Add minimal infrastructure to `imgui.h` that Omar could accept upstream.

## Step 1: Add callback infrastructure to imgui.h

**File:** `external/imgui/imgui/imgui.h`

Prepare it as a clean addition to imgui.h (no mention of imgui_bundle).

Near line 109, add to the section TOC:
```
// [SECTION] Demo markers (IMGUI_DEMO_MARKERS), for imgui_manual and related
```

Near line 4853, add the implementation with explanatory comments:

```cpp
//-----------------------------------------------------------------------------
// [SECTION] Demo markers (IMGUI_DEMO_MARKER)
//-----------------------------------------------------------------------------
// IMGUI_DEMO_MARKER() is placed throughout demo code to mark interesting sections.
// It enables interactive code browsers (e.g. imgui_manual) to link UI elements
// to their source code.
//
// Usage: Each demo translation unit defines IMGUI_DEMO_MARKER_FILE before
// including imgui.h. TUs without it get an empty macro (zero cost).
//
//   #define IMGUI_DEMO_MARKER_FILE "imgui_demo"
//   #include "imgui.h"
//
// The callback globals are defined in imgui_demo.cpp.
//-----------------------------------------------------------------------------

typedef void (*ImGuiDemoMarkerCallback)(const char* file, int line, const char* section, void* user_data);
extern ImGuiDemoMarkerCallback  GImGuiDemoMarkerCallback;
extern void*                    GImGuiDemoMarkerCallbackUserData;
#ifdef IMGUI_DEMO_MARKER_FILE
#define IMGUI_DEMO_MARKER(section)  do { if (GImGuiDemoMarkerCallback != NULL) GImGuiDemoMarkerCallback(IMGUI_DEMO_MARKER_FILE, __LINE__, section, GImGuiDemoMarkerCallbackUserData); } while (0)
#else
#define IMGUI_DEMO_MARKER(section)
#endif
```

## Step 2: Add global definitions in imgui_demo.cpp

**File:** `external/imgui/imgui/imgui_demo.cpp`

- Add `#define IMGUI_DEMO_MARKER_FILE "imgui_demo"` before `#include "imgui.h"` (~line 130)
- Replace the old `#ifndef IMGUI_DEMO_MARKER` guard block (~lines 229-233) with the global definitions:

```cpp
// [ADAPT_IMGUI_BUNDLE]
ImGuiDemoMarkerCallback  GImGuiDemoMarkerCallback = NULL;
void*                    GImGuiDemoMarkerCallbackUserData = NULL;
// [/ADAPT_IMGUI_BUNDLE]
```

## Step 3: Update each other demo file

For each file: add `#define IMGUI_DEMO_MARKER_FILE "name"` before the first `#include`, and remove the `#ifndef IMGUI_DEMO_MARKER` guard block.

| File | IMGUI_DEMO_MARKER_FILE value |
|------|------------------------------|
| `external/implot/implot/implot_demo.cpp` | `"implot_demo"` |
| `external/implot3d/implot3d/implot3d_demo.cpp` | `"implot3d_demo"` |
| `external/ImAnim/ImAnim/im_anim_demo.cpp` | `"im_anim_demo"` |
| `external/ImAnim/ImAnim/im_anim_demo_basics.cpp` | `"im_anim_demo_basics"` |
| `external/ImAnim/ImAnim/im_anim_doc.cpp` | `"im_anim_doc"` |
| `external/ImAnim/ImAnim/im_anim_usecase.cpp` | `"im_anim_usecase"` |

These values match `DemoFileInfo::baseName` in `library_config.cpp`.

## Step 4: Move zone tracking into imgui_manual.cpp

**File:** `external/imgui_manual/imgui_manual/src/imgui_manual.cpp`

- Move `DemoMarkersRegistry` class + `DemoMarker_IsMouveHovering()` from `imgui_demo_marker_hooks.cpp` into `imgui_manual.cpp` (in an anonymous namespace)
- Update `OnDemoMarkerHook` to new callback signature and inline the hover check:

```cpp
void OnDemoMarkerCallback(const char* file, int line, const char* section, void* user_data)
{
    (void)user_data;
    if (!DemoMarker_IsMouveHovering(line))
        return;
    // file is IMGUI_DEMO_MARKER_FILE value (e.g. "imgui_demo"), append ".cpp" for display
    char filename[256];
    snprintf(filename, sizeof(filename), "%s.cpp", file);
    snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
        "%s:%d - \"%s\"", filename, line + 1, section);
    if (GDemoMarker_FlagFollowSource)
        DemoCodeViewer_ShowCodeAt(filename, line, section);
}
```

- Update initialization: `GImGuiDemoMarkerCallback = OnDemoMarkerCallback;` (line 190)
- Remove `#include "imgui_demo_marker_hooks.h"` and `BaseFilename()` function

## Step 5: Remove force-include from CMake

**File:** `external/imgui_manual/imgui_manual/imgui_manual_build.cmake`

- Delete `_force_include()` function
- Delete `iman_force_include_marker_hooks()` function
- Remove the call to `iman_force_include_marker_hooks()` from `iman_main()`
- Remove `imgui_demo_marker_hooks.h` from source lists if referenced

## Step 6: Delete hook files

Delete:
- `external/imgui_manual/imgui_manual/src/imgui_demo_marker_hooks.h`
- `external/imgui_manual/imgui_manual/src/imgui_demo_marker_hooks.cpp`

## Verification

1. **Desktop build:** `just manual_desktop_build` — run app, hover demos in all libraries, verify code viewer follows correctly
2. **Emscripten build:** `just manual_ems_build` — same test in browser
3. **Build without manual:** verify no link errors when `IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB=OFF`
4. **No `__FILE__`** in any IMGUI_DEMO_MARKER expansion
5. **No `-include` flags** in build output