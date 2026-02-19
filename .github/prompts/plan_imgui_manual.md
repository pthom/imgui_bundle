# Plan: Evolve imgui_manual for Multiple Libraries and Python Support

## Current State Analysis

The `imgui_manual/` project is an interactive demo viewer:
- **Left panel (30%)**: Demo windows with widgets
- **Right panel (70%)**: Source code viewer with syntax highlighting
- **Core feature**: When hovering any widget with "Follow source" enabled, the code view scrolls to the relevant `IMGUI_DEMO_MARKER`

### Current Components

| File | Purpose |
|------|---------|
| `imgui_manual.main.cpp` | Main app: docking setup, hooks, menus |
| `demo_code_viewer.cpp/h` | Loads/displays source with ImGuiColorTextEdit |
| `imgui_demo_marker_hooks.cpp/h` | IMGUI_DEMO_MARKER tracking system |
| `CMakeLists.txt` | Copies demo files, force-includes headers |
| `assets/demo_code/*.txt` | Runtime copies of demo source files |

### Current Limitations

1. **Hardcoded file list** in `demo_code_viewer.cpp` (lines 44-49)
2. **Hardcoded docking windows** in `imgui_manual.main.cpp` (lines 39-84)
3. **C++ only** - no Python demo support
4. **ImAnim only** - no ImGui/ImPlot/ImPlot3D demos shown (even though files are copied)
5. **No library tabs** - all demos lumped together

### Available Demo Files

| Library | C++ Demo Files | Python Demo Files |
|---------|----------------|-------------------|
| ImAnim | 4 files: im_anim_demo, im_anim_demo_basics, im_anim_doc, im_anim_usecase | `external/ImAnim/ImAnim/im_anim_demo_basics.py` |
| ImGui | 1 file: imgui_demo.cpp | `bindings/imgui_bundle/demos_python/demos_immapp/imgui_demo.py` (3500 lines, not a line-by-line port) |
| ImPlot | 1 file: implot_demo.cpp | `demos_python/demos_implot/implot_demo.py` |
| ImPlot3D | 1 file: implot3d_demo.cpp | `demos_python/demos_implot3d/implot3d_demo.py` |

---

## Goals

1. **Multi-library support**: Tabs or separate apps for ImGui, ImPlot, ImPlot3D, ImAnim
2. **Python demo support**: Show Python code alongside C++ when available
3. **Reduce repetition**: Data-driven configuration instead of copy-paste code
4. **Flexible deployment**: Combined app AND separate per-library apps (multiple executables)

---

## Proposed Architecture

### Phase 1: Refactor to Data-Driven Configuration

**Goal**: Replace hardcoded lists with configuration structures.

#### 1.1 Create `library_config.h`

```cpp
struct DemoFileInfo {
    const char* baseName;         // "im_anim_demo_basics" (without extension)
    bool hasPython;               // true if .py exists alongside .cpp
};

struct LibraryConfig {
    const char* name;                    // "ImAnim"
    const char* dockWindowPrefix;        // "ImAnim"
    std::vector<DemoFileInfo> files;
    std::function<void()> frameSetup;    // e.g., iam_update_begin_frame()
    std::function<void(bool)> demoGui;   // e.g., ImAnimDemoBasicsWindow
};

// All available libraries
extern std::vector<LibraryConfig> g_allLibraries;
```

**File naming convention** (no configurability needed):
- C++ file: `demo_xxx.cpp` → asset: `demo_xxx.cpp.txt`
- Python file: `demo_xxx.py` (same folder as C++) → asset: `demo_xxx.py.txt`
- Python files will need to be co-located with C++ files (move `imgui_demo.py` to `external/imgui/imgui/`)

#### 1.2 Refactor `demo_code_viewer.cpp`

- Accept file list dynamically from `LibraryConfig`
- Add language toggle (C++/Python) when both available
- Generalize tab creation

#### 1.3 Refactor `imgui_manual.main.cpp`

- Generate docking windows from `LibraryConfig`
- Support library tabs in left panel OR separate apps
- Make frame setup callbacks configurable

### Phase 2: Add Python Demo Support

**Goal**: Display Python source code when available.

#### 2.1 Update CMakeLists.txt

- Copy Python demo files to `assets/demo_code/`
- For each `demo_xxx.cpp`, check if `demo_xxx.py` exists in same folder and copy it

#### 2.2 Python Demo Files with IMGUI_DEMO_MARKER

Python marker pattern (does nothing - code viewer uses line matching):
```python
def IMGUI_DEMO_MARKER(section: str) -> None:
    """Marker for the interactive manual. Maps sections to source code."""
    pass
```

Existing Python demos:
- `external/ImAnim/ImAnim/im_anim_demo_basics.py` - already exists
- `imgui_demo.py` - exists but needs to be moved to `external/imgui/imgui/`
- ImPlot/ImPlot3D demos - may need to be moved to external lib folders

#### 2.3 Add Language Toggle to Code Viewer

```cpp
struct CodeFile {
    std::string cppContent;
    std::string pythonContent;  // Empty if not available
    TextEditor cppEditor;
    TextEditor pythonEditor;
    bool showPython = false;    // Toggle state
};
```

UI: `[C++] [Python]` toggle buttons when both available.

### Phase 3: Support All Libraries

**Goal**: Add ImGui, ImPlot, ImPlot3D to the manual.

#### 3.1 Library Configurations

```cpp
// ImAnim
LibraryConfig imAnimConfig = {
    .name = "ImAnim",
    .files = {
        {"im_anim_demo_basics", true},   // has Python
        {"im_anim_demo", false},
        {"im_anim_doc", false},
        {"im_anim_usecase", false},
    },
    .frameSetup = []{ iam_update_begin_frame(); iam_clip_update(ImGui::GetIO().DeltaTime); },
    .demoGui = ImAnimDemoBasicsWindow,
};

// ImGui
LibraryConfig imGuiConfig = {
    .name = "ImGui",
    .files = {{"imgui_demo", true}},  // has Python (not line-by-line match)
    .frameSetup = nullptr,
    .demoGui = [](bool) { ImGui::ShowDemoWindow(); },
};

// ImPlot
LibraryConfig imPlotConfig = {
    .name = "ImPlot",
    .files = {{"implot_demo", true}},
    .frameSetup = nullptr,
    .demoGui = [](bool) { ImPlot::ShowDemoWindow(); },
};

// ImPlot3D
LibraryConfig imPlot3DConfig = {
    .name = "ImPlot3D",
    .files = {{"implot3d_demo", true}},
    .frameSetup = nullptr,
    .demoGui = [](bool) { ImPlot3D::ShowDemoWindow(); },
};
```

#### 3.2 Build Multiple Executables

CMakeLists.txt will create multiple targets (no options needed):

```cmake
# Combined app with all libraries
imgui_bundle_add_app(imgui_manual_all ...)

# Per-library apps
imgui_bundle_add_app(imgui_manual_imanim ...)
imgui_bundle_add_app(imgui_manual_imgui ...)
imgui_bundle_add_app(imgui_manual_implot ...)
imgui_bundle_add_app(imgui_manual_implot3d ...)
```

Each app links only the libraries it needs and uses a subset of `LibraryConfig`.

### Phase 4: UI Design for Multi-Library

#### Option A: Library Tabs (Combined App)

```
+--------------------------------------------------------+
| [ImGui] [ImPlot] [ImPlot3D] [ImAnim]  <- Library tabs  |
+--------------------------------------------------------+
| Demo Window        |  Source Code Viewer               |
| (30%)              |  (70%)                             |
|                    |  [C++] [Python] <- language toggle |
| [Follow source]    |  [Tabs: file1, file2, ...]        |
|                    |                                    |
| <widgets>          |  <syntax highlighted code>        |
+--------------------------------------------------------+
```

#### Option B: Separate Apps

Build targets:
- `imgui_manual_all` - Combined app with tabs
- `imgui_manual_imanim` - ImAnim only
- `imgui_manual_imgui` - ImGui only
- `imgui_manual_implot` - ImPlot only
- `imgui_manual_implot3d` - ImPlot3D only

### Phase 5: Polish

#### 5.1 GitHub Link Implementation

```cpp
void OpenGitHubAtLine(const char* baseName, int line, bool isPython) {
    // Determine repo/path based on library
    std::string ext = isPython ? ".py" : ".cpp";
    std::string url = GetGitHubBaseUrl(baseName) + baseName + ext + "#L" + std::to_string(line);
    OpenUrl(url);
}
```

#### 5.2 Search Functionality

- [x] Search within current file
- [x] Search across all files

---

## Implementation Order

### Step 1: Immediate Cleanup (No Breaking Changes)
- [x] Extract file list to a config structure (still hardcoded, but centralized)
- [x] Add ImGui/ImPlot/ImPlot3D files to code viewer tabs
- [x] Test that existing functionality still works (app runs, needs manual verification)

### Step 2: Add Python Toggle
- [x] Move Python demos to bindings/imgui_bundle/demos_python/ , cpp demos remain in external/ folders
- [x] Update CMake to copy Python demo files
- [x] Add Python editor alongside C++ editor
- [x] Add [C++] [Python] toggle buttons

### Step 3: Add Library Selection and Multi-Library Support
- [x] Create library selection UI (changed from tabs to top edge toolbar for better UX)
- [x] Handle imgui, implot and implot3d demos:
  - Solution: Added `ShowDemoWindow_MaybeDocked(bool create_window, bool* p_open)` to ImGui fork
  - ImPlot and ImPlot3D already had `ShowAllDemos()` pattern
  - When `create_window=false`, demo content is shown directly in the dockable window
- [x] Filter code viewer files by selected library (GetCurrentLibraryFiles() in demo_code_viewer.cpp)
- [x] Wire up library-specific frame setup (ImAnim setup in PreNewFrame callback)
- [x] Add "Open in detached window" checkbox option

### Step 4: Adapt imgui_demo.cpp
- [x] imgui_demo.cpp should be adapted to support force include pattern (need to rebase some changes)
- [x] Rewiew IMGUI_DEMO_MARKER locations in imgui_demo.cpp

### Step 5: Make Python code viewer work with IMGUI_DEMO_MARKER
- [x] Make sure the Python code viewer can jump to the correct line based on IMGUI_DEMO_MARKER calls in the Python demos
  (require reading the source code of the Python demos to find the correct line numbers for each marker, and mapping them to the marker names)
  (later, in Python this may require inspecting the python source code, with the inspect module)
  test this with the existing `imgui_demo.py` and the `im_anim_demo_basics.py` which already has markers

### Step 6: adapt implot_demo and implot3d_demo, and im_anim demos
- [x] Review im_anim demos so that demo markers are inside the tree node.
- [x] Add IMGUI_DEMO_MARKER to implot_demo.cpp and implot3d_demo.cpp
- [x] Add the same IMGUI_DEMO_MARKER (with exact same section names) to the Python demos
- [x] Add missing demos in implot3d_demo.py (and add markers)
List of demo functions that are not present in implot3d_demo.py, but present in implot3d_demo.cpp.
'demo_config', 'demo_legend_options', 'demo_log_scale', 'demo_symmetric_log_scale', 'demo_mouse_picking', 'demo_equal_axes', 'demo_auto_fitting_data',
'demo_custom_per_point_style', 'demo_offset_and_stride', 'demo_custom_overlay', 'demo_axis_constraints', 'demo_plot_flags'
- [x] Not useful: Port ShowDemoWindow_MaybeDocked to implot and implot3d demos? Check if it useful (i.e. bring more demos to python)

### Step 7: Build Multiple Executables
- [X] Args / Run the manual showing only one library at a time
  (--lib implot, --lib implot3d, --lib imanim, --lib imgui, or ?lib=implot for emscripten)
- [x] Each target uses appropriate LibraryConfig subset
- [x] Deploy online: see https://traineq.org/ImGuiBundle/imgui_manual/ (+ ?lib=... for specific library)

### Step 8: Polish
- [x] Implement GitHub link
- [x] Remember to move python github links back to main branch
- [x] Add file/marker search: search in demo files or in declarations (header files or stub). 
  This requires adding header files or stubs to the libraries. 
  possible use case: user wants to find the signature and doc for a specific function or widget in the demo code. He selects it, clicks (right-click or place a button somewhere? this is to be discussed) "search in code", and the relevant header file or stub is opened in the code viewer, with the first matching line highlighted and the possibility to search for other occurrences in the file.
- [x] Also handle imgui_internal.h, implot(3d)_internal.h (+ stubs)
- [x] Remove external modules from ImAnim
- [x] Layout manual without docking, only window

### Step 11: Manual in python
Nooo: Try to avoid doing this...
  bindings/imgui_bundle/demos_python/demos_imgui_manual contains Python demos for the manual.
  They are almost line by line ports of the C++ demos, including the IMGUI_DEMO_MARKER calls.
  Let's try to make a simplified version of the manual in Python, with simplified features:
  - we run only one file at a time
    - the code viewer only shows the Python demo file source (using inspect)

### WWW
- [x] specify default python or C++ for ShowImGuiManualGui
- [x] add python demos
- [x] add full python demos also (for implot, implot3d, and imanim)
- [x] fix imgui_demo.py : 
- [x] add menu bars to all demos py
- [x] "Code for this demo": only on selected demos
- [x] Add link to imgui_manual in imgui_manual for imgui
- [x] Fix choice lib in emscripten
- [x] Can't switch between C++ and Python!
- [x] "Code for this demo" => fail in emscripten
- [ ] Contact ocornut / preview: 
https://traineq.org/ImGuiBundle/imgui_manual/?lib=imgui 
https://traineq.org/ImGuiBundle/imgui_manual/?lib=implot
https://traineq.org/ImGuiBundle/imgui_manual/

Link to commit / demo_markers
Link to demo bundle 

- [x] publish imgui_bundle_demo
- [ ] fix CI errors
- [ ] redirect current manual to new
- [ ] close manual repo
- [ ] pyodide wheels: remove demo_assets, demo_cpp, demos_python

### Step 10: Integration
- [x] Add imgui/implot[3d]/imanim manual in bundle interactive manual:
- [ ] Update bundle book and documentation
- [ ] Add doc for ImAnim in the bundle book (compare C++ and Python API, esp enum usage)


### Step 11: Publish & Communicate
- [ ] Release v1.92
- [ ] Mail to ocornut and other maintainers about the new manual and its features
- [ ] PR to imgui, implot, implot3d and imanim with DemoMarker. Advocate for adoption in the main repos.

