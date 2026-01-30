# Documentation Improvement Plan

This document summarizes findings from reviewing demos and documentation, with actionable improvements for `docs/book/` (which builds to book.pdf).

## Executive Summary

The demos are excellent and well-documented. The main gap is that **book.pdf doesn't leverage them enough** - it describes features abstractly without pointing to concrete examples.

---

## 1. Missing Sections in book.pdf

### 1.1 Platform Behavior Table (Async/Pyodide)

**Add to Python Users section:**

```markdown
## Platform-Specific Behavior

| Platform | `run()` | `run_async()` |
|----------|---------|---------------|
| Desktop  | Blocking | Awaitable |
| Pyodide  | Fire-and-forget (returns immediately) | Awaitable |
| Notebook | Use `nb.start()` | Use `nb.start()` |

Note: In Pyodide, browsers cannot block, so `run()` starts the GUI and returns immediately.
```

**Reference:** Recent refactoring in `pyodide_patch_runners.py`

### 1.2 Troubleshooting / FAQ Section

**Add new section covering common issues:**

- Pyodide: "My app freezes" → Use `run()` or `run_async()`, not blocking patterns
- DPI: "Widgets look too small/large" → Use `em_size()` for sizing
- Fonts: "Icons don't show" → Check `load_additional_fonts` callback
- Assets: "Image not found" → Check `hello_imgui.set_assets_folder()`

### 1.3 Asset Management Examples

**Currently missing practical examples. Add:**

```python
# Set assets folder (call before run)
hello_imgui.set_assets_folder("my_assets")

# Load font in callback
def load_fonts():
    hello_imgui.load_font("fonts/Roboto.ttf", 18.0)

params.callbacks.load_additional_fonts = load_fonts

# Display image from assets
hello_imgui.image_from_asset("images/logo.png", hello_imgui.em_to_vec2(5, 5))
```

**Reference:** `demos_immapp/demo_assets_addons.py` has great examples

### 1.4 Callbacks Reference

**Add complete list (currently scattered):**

```markdown
## RunnerParams Callbacks

### GUI (called every frame)
- `show_gui`: Main GUI content
- `show_menus`: Menu bar content
- `show_app_menu_items`: Items in App menu
- `show_status`: Status bar content

### Lifecycle
- `post_init`: After OpenGL initialization
- `before_exit`: Before shutdown
- `load_additional_fonts`: Font loading

### Rendering
- `custom_background`: Custom OpenGL background
- `pre_new_frame`: Before each frame

### Mobile
- `mobile_on_pause`: App backgrounded
- `mobile_on_resume`: App foregrounded
```

---

## 2. Library Documentation (Demo-First Approach)

### Philosophy

**Don't duplicate demo content.** The demos are tested, runnable, and already well-documented. The book should be a signpost to them, not a copy.

### Template for Each Library

For each library, add a section with:

1. **Brief intro** (2-3 sentences): What it does, when to use it
2. **Code snippet**: Highlight key usage from an existing demo
3. **Links**: Full demo path + API reference (.pyi file)

### Libraries to Document

| Library | Purpose | Demo to Reference | API |
|---------|---------|-------------------|-----|
| **ImPlot** | 2D plotting (line, bar, scatter, etc.) | `haiku_implot_heart.py` | `implot/__init__.pyi` |
| **ImPlot3D** | 3D plotting | `haiku_butterfly.py` | `implot3d/__init__.pyi` |
| **ImmVision** | Image visualization/debugging | `demos_immvision/demo_immvision_display.py` | `immvision.pyi` |
| **imgui_md** | Markdown rendering | `demo_assets_addons.py` | `imgui_md.pyi` |
| **ColorTextEdit** | Syntax-highlighted text editor | `demos_tex_edit/demo_text_edit.py` | `imgui_color_text_edit.pyi` |
| **imgui_knobs** | Rotary knobs | `haiku_implot_heart.py` | `imgui_knobs.pyi` |
| **Node Editor** | Visual node graphs | `demos_node_editor/` | `imgui_node_editor.pyi` |
| **ImGuizmo** | 3D gizmos for transforms | `demos_imguizmo/` | `imguizmo.pyi` |

### Example Section (ImPlot)

```markdown
## ImPlot - 2D Plotting

ImPlot adds interactive 2D plots to your GUI: line charts, bar charts, scatter plots,
heatmaps, and more. Plots support zooming, panning, and hover inspection.

**Quick example** (from `haiku_implot_heart.py`):

    if implot.begin_plot("Heart", implot.ImVec2(-1, -1)):
        implot.plot_line("heart", x_values, y_values)
        implot.end_plot()

**See also:**
- Full demo: `demos_immapp/haiku_implot_heart.py`
- Complete demo gallery: `demos_implot/implot_demo.py`
- API reference: `implot/__init__.pyi`
```

### Example Section (ImmVision)

```markdown
## ImmVision - Image Visualization

ImmVision provides interactive image display with zoom, pan, pixel inspection,
and colormap support. Useful for debugging computer vision pipelines.

**Quick example:**

    # Initialize color order once at startup
    immvision.use_rgb_color_order()

    # Display with full interactivity
    params = immvision.ImageParams()
    immvision.image("My Image", image_array, params)

**See also:**
- Display demo: `demos_immvision/demo_immvision_display.py`
- Inspector demo: `demos_immvision/demo_immvision_inspector.py`
- API reference: `immvision.pyi`
```

---

## 3. Demo References in Documentation

### 2.1 Link Features to Demos

| Feature | Demo to Reference |
|---------|-------------------|
| Hello World | `demos_immapp/demo_hello_world.py` (14 lines) |
| Complex app (docking, fonts, settings) | `demos_immapp/demo_docking.py` |
| Assets, icons, em_size | `demos_immapp/demo_assets_addons.py` |
| ImPlot basics | `demos_immapp/haiku_implot_heart.py` |
| Async parallel execution | `demos_immapp/demo_run_async.py` |
| FPS/power management | `demos_immapp/demo_powersave.py` |
| Custom OpenGL background | `demos_immapp/demo_custom_background.py` |
| Test automation | `demos_immapp/demo_testengine.py` |

### 2.2 Add Framework Comparison Code

The `sandbox/compare_other_libs/` folder has side-by-side comparisons:
- `ex_imgui_bundle.py` (13 lines)
- `ex_qt.py` (31 lines)
- `ex_gradio.py`, `ex_nicegui.py`, `ex_dearpygui.py`

**Action:** Include these in the "Why ImGui Bundle?" comparison section.

---

## 4. Structural Improvements

### 3.1 Progressive Disclosure

Current Python section mixes beginner and advanced topics. Suggested reorg:

```
Python Users
├── Quick Start (hello_world, 5 min)
├── Core Concepts (immediate mode, widgets)
├── Building Apps (ImmApp, RunnerParams)
├── Add-ons (ImPlot, Markdown, etc.)
├── Advanced
│   ├── Async & Notebooks
│   ├── Pyodide Web Deployment
│   └── Custom Backends
└── Troubleshooting
```

### 3.2 Visual Architecture Diagram

Add diagram showing:
```
Your Code (gui function)
    ↓
ImmApp / HelloImGui (lifecycle, settings)
    ↓
Dear ImGui (widgets, rendering)
    ↓
Backend (GLFW/SDL + OpenGL/Metal/Vulkan)
```

---

## 5. Content Updates Needed

### 4.1 Pyodide Section

**Current:** Mentions `start()` which was removed
**Update to:** Document that `run()` is fire-and-forget in Pyodide

```python
# Same code works everywhere
immapp.run(gui, window_title="My App")
# Desktop: blocks until closed
# Pyodide: starts and returns immediately
```

### 4.2 demo_run_async.py Docstring

**Current:** Mentions manual FPS settings
**Reality:** `run_async()` now sets these automatically

Consider updating the demo docstring to reflect this.

---

## 6. Quick Wins

These can be done quickly:

1. [ ] Add platform behavior table to Pyodide section
2. [ ] Add asset management code example
3. [ ] Add callbacks reference list
4. [ ] Include compare_other_libs code in comparison section
5. [ ] Fix Pyodide section (remove `start()` references if any remain in docs)
6. [ ] Add library sections using demo-first template (Section 2)

---

## 7. Files to Modify

| File | Changes |
|------|---------|
| `docs/book/python/python_pyodide.md` | Platform table, update examples |
| `docs/book/python/python_asyncio.md` | Clarify async patterns |
| `docs/book/runners/` | Add callbacks reference |
| `docs/book/intro/` | Add compare_other_libs examples |
| New: `docs/book/python/troubleshooting.md` | FAQ section |
| New or expand: `docs/book/addons/` | Library docs using demo-first template |

---

## 8. Demo Improvements (Optional)

| Demo | Suggested Change |
|------|------------------|
| Add `demo_pyodide_example.py` | Show fire-and-forget pattern |
| Update `demo_run_async.py` | Clarify auto-settings in docstring |
| Promote `compare_other_libs/` | Move to demos_immapp or add to launcher |

---

## 9. Interactive Manual (Demo Launcher)

### Overview

The **interactive manual** is the primary way users discover and explore ImGui Bundle features:

- **Entry point:** `demos_python/demo_immapp_launcher.py`
- **Demos folder:** `demos_python/demos_immapp/`
- **C++ equivalent:** `demos_cpp/demos_immapp/`

It displays a table of demos with descriptions, and can show both Python and C++ source code inline. This is a powerful learning tool.

### Current Demo List (from demo_immapp_launcher.py)

| Demo | Description |
|------|-------------|
| `demo_hello_world` | Hello world with ImmApp |
| `demo_assets_addons` | Assets, Markdown, ImPlot |
| `demo_docking` | Complex layouts, fonts, settings, menus |
| `demo_custom_background` | Custom 3D OpenGL background |
| `demo_powersave` | FPS idling and power management |
| `demo_testengine` | ImGui Test Engine automation |
| `demo_python_context_manager` | Python context managers for begin/end |
| `demo_run_async` | Parallel Python execution with GUI |
| `demo_command_palette` | VSCode-style command palette |
| `demo_parametric_curve` | Immediate GUI paradigm illustration |
| `haiku_implot_heart` | ImPlot + imgui_knobs demo |
| `haiku_butterfly` | ImPlot3D butterfly effect |
| `demo_drag_and_drop` | Drag and drop |
| `demo_implot_markdown` | Quick ImPlot + Markdown setup |
| `demo_matplotlib` | Matplotlib integration |
| `demo_pydantic` | Pydantic with ImVec2/ImVec4 |
| `example_python_backend_*` | Pure Python backends (GLFW, SDL2, SDL3, pyglet, wgpu) |

### Future Improvements (Ideas)

1. **Categorize demos:**
   ```
   Getting Started
   ├── demo_hello_world
   ├── demo_assets_addons

   Application Patterns
   ├── demo_docking
   ├── demo_powersave

   Plotting
   ├── haiku_implot_heart
   ├── haiku_butterfly
   ├── demo_implot_markdown

   Advanced
   ├── demo_run_async
   ├── demo_custom_background
   ├── demo_testengine

   Python-Specific
   ├── demo_python_context_manager
   ├── demo_matplotlib
   ├── demo_pydantic
   ├── example_python_backend_*
   ```

2. **Add difficulty/complexity indicators** (beginner/intermediate/advanced)

3. **Add tags/filters** - users could filter by: plotting, async, layout, etc.

4. **Link to related documentation** - each demo could link to relevant book.pdf section

5. **Add missing demos:**
   - `demo_pyodide` - Fire-and-forget web deployment pattern
   - `demo_notebooks` - Jupyter notebook usage
   - `demo_assets_fonts` - Focused font loading example

6. **Improve DemoApp metadata:**
   ```python
   DemoApp(
       "demo_docking",
       "Complex layouts with docking, fonts, settings",
       category="Application Patterns",
       difficulty="Advanced",
       tags=["docking", "fonts", "settings", "menus"],
   )
   ```

### Files Involved

- `demos_python/demo_immapp_launcher.py` - Launcher with demo list
- `demos_python/demo_utils/demo_app_table.py` - Table rendering logic
- `demos_python/demos_immapp/*.py` - Individual demos
- `demos_cpp/demos_immapp/*.cpp` - C++ equivalents

---

## 10. Fiatlight - A Project Built on ImGui Bundle

[Fiatlight](https://github.com/pthom/fiatlight) is a Python framework that automatically generates interactive GUIs from functions and data structures. It showcases what's possible with ImGui Bundle.

### What It Does

- **Automatic GUI from functions**: `fiatlight.run([f1, f2])` creates an interactive pipeline
- **Function graph visualization**: Connect functions visually, see data flow
- **State persistence**: Inputs, layouts, and preferences saved automatically
- **Web deployment**: Same code runs locally or as static web pages

### Links

| Resource | URL |
|----------|-----|
| **Documentation** | https://pthom.github.io/fiatlight_doc/flgt/intro.html |
| **PDF Manual** | https://pthom.github.io/fiatlight_doc/flgt.pdf |
| **Video Tutorials** | https://pthom.github.io/fiatlight_doc/flgt/video_tutorials.html |
| **Repository** | https://github.com/pthom/fiatlight |

### Documentation Highlights

Fiatlight's docs are tutorial-oriented with good progressive disclosure:
- First Steps → Manual → API → Domain Kits
- 6 video tutorials covering beginner to advanced
- Visual examples throughout

### Potential Cross-References

Consider mentioning Fiatlight in book.pdf as:
- An example of a complex application built with ImGui Bundle
- Inspiration for users wanting to build similar tools
- A showcase of the node editor library in action

---

## Notes

- Demos are the best documentation - they're tested and runnable
- book.pdf should point TO demos, not duplicate their content
- The interactive manual (`demo_immapp_launcher.py`) already shows source code inline
- **The interactive manual itself could become a better navigation/discovery tool**

Generated: 2026-01-30
