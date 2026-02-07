# ImAnim Demo "a la ImGui Manual"

## Goal

Create an interactive demo for ImAnim, similar to ImGui Manual. Users can explore the demo and immediately see the corresponding source code. When hovering any widget (with tracking enabled), the code view scrolls to the relevant section.

## Architecture

```
+------------------------------------------+
|  ImAnim Demo (left 30%)  |  Code View    |
|  - Demo tab              |  (right 70%)  |
|  - Doc tab               |               |
|  - Usecases tab          |  [Tabs: demo, |
|                          |   doc, usecase]|
|  [Follow source] checkbox|               |
|  Marker info display     |  Syntax-      |
|                          |  highlighted  |
|  <interactive widgets>   |  source code  |
+------------------------------------------+
```

## Technical Choices

- **Asset loading**: `HelloImGui::LoadAssetFileData` to load source files at runtime
- **Code viewer**: ImGuiColorTextEdit from ImGui Bundle (syntax highlighting)
- **Multi-file**: Tabs in code viewer, auto-switch when tracking across files
- **Marker names**: Hierarchical, e.g. "Advanced Interpolation/Style Interpolation"

## Implementation Steps

### Phase 1: Infrastructure

- [x] **1.1** Set up CMake to copy source files to `assets/demo_code/` at configure time
  - Files copied as `.cpp.txt` for macOS app bundle compatibility
- [x] **1.2** Create `demo_code_viewer.h/cpp` with:
  - Function to load source files at startup using `HelloImGui::LoadAssetFileData`
  - Store file contents in a map: `filename -> content`
  - Code viewer window using ImGuiColorTextEdit
  - Tabs for switching between files
  - Function to scroll to a specific line in a specific file
  - Status bar with line/column info
  - Copy button and "View on github" placeholder
- [x] **1.3** Wire up `GImGuiDemoMarkerHook` to call the code viewer's scroll function
  - Renamed from `GImGuiDemoMarkerCallback` to avoid symbol conflict with imgui_bundle
- [x] **1.4** Update `main_helloimgui.cpp` to:
  - Initialize code viewer at startup
  - Replace placeholder right dock window with code viewer
  - Set up the callback

### Phase 2: Add Markers to im_anim_demo.cpp

- [x] **2.1** Add `#define IMGUI_DEMO_MARKERS_FILE "im_anim_demo.cpp"` and include hooks
- [x] **2.2** Add `IMGUI_DEMO_MARKER` calls at each demo section
  - Used perl script to add markers before all TreeNode calls
  - Added markers to ShowXXXDemo() functions
- [ ] **2.3** Add `IMGUI_DEMO_MARKER_SHOW_SHORT_INFO()` at the top of the demo window
- [x] **2.4** Test tracking and code view synchronization

### Phase 3: Extend to Other Files

- [x] **3.1** Add markers to `im_anim_doc.cpp`
- [x] **3.2** Add markers to `im_anim_usecase.cpp`
  - Used perl script for TreeNode calls
  - Modified USECASE_ITEM macro to include IMGUI_DEMO_MARKER
  - Added markers to ShowUsecase_XXX() functions
- [x] **3.3** Ensure tab switching works correctly across files

### Phase 4: Polish

- [x] **4.1** Ensure line highlighting in code view (SelectLine is called)
- [x] **4.2** Add keyboard shortcut reminder (Ctrl+Alt+C to toggle tracking)
- [x] Add main menu (Quit / Link & About / Ad on Status Bar)
- [ ] **4.3** Test and refine UX
- [ ] **4.4** Implement "View on github at this line" button
  - Use `HyperlinkHelper::OpenUrl()` to open browser
  - Build URL: `https://github.com/USER/REPO/blob/BRANCH/filename#L{line}`
  - Need to configure base GitHub URL and branch
