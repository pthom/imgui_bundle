# Improve Bundle intro — Spec

## Goal
The intro tab is the first thing users see when they open the imgui bundle interactive manual. It should provide a clear and engaging introduction to the features and capabilities of the bundle, as well as guide users on how to navigate and use it effectively.

It should not be too wordy: a few sentences + some catchy images/animations.

This should not be a long project. I want this to be done in about 3 hours. Let's pick a few key features of the bundle to highlight in the intro tab, and then decide on the best way to present them.

Note: later we might envision to add an intro tab to the standalone imgui manual as well.


## Context

- Current intro: `bindings/imgui_bundle/demos_cpp/demo_imgui_bundle_intro.cpp` (and `.py`)
- Current content is very bare: tagline, 2–3 lines of markdown, navigation badges, animated logo
- Docs for inspiration: `docs/book/intro/intro.md`, `docs/book/intro/key_features.md`

## Brainstorming (archived)

Ideas considered during spec discussion:
- 3D custom background (too risky for time budget → Non-goal)
- ImmVision showcase (too specialized → Non-goal)
- ImAnim hero animation (too "show-off" → Not used)
- Table with angled headers (feels like reference docs → Non-goal)
- Custom 3D background with particles (too complex → Non-goal)


## Requirements

### Layout
```
[Animated logo]   Dear ImGui Bundle — batteries included
                  C++ & Python · 20+ libraries · cross-platform
                  <2–3 sentence description>

[badges: sources / docs / live demo]          (existing, keep)

────────────────────────────────────────────────────────────
  [Heart + knob]   │   [Lorenz attractor]   │  [Color picker]
      ImPlot        │       ImPlot3D         │     ImGui
────────────────────────────────────────────────────────────
```

ImPlot:heart, candlestick, IMGUI_DEMO_MARKER("Subplots/Tables");
ImPlot3d: Lorenz attractor, IMGUI_DEMO_MARKER("Plots/Mesh Plots"), IMGUI_DEMO_MARKER("Plots/Mesh Plots");

### Mini-demos (side by side, compact)
Three live animated demos embedded in columns:

1. **Beating heart** (`haiku_implot_heart`): animated 2D heart plot with a knob to control pulse rate.
   Shows: ImPlot + imgui-knobs + animation.

2. **Lorenz attractor** (`haiku_butterfly`): two diverging 3D trajectories growing in real time.
   Shows: ImPlot3D + animation.

3. **Color picker**: a `ImGui::ColorPicker4` (no extra data needed).
   Shows: ImGui widget richness, visually striking.

### Implementation constraints
- Each mini-demo is a self-contained sub-function with persistent state (static/class variables), NOT a standalone `immapp.run()` app.
- Animation must be smooth: `fps_idling.enable_idling = False` while the intro tab is visible.
- Demos shown side by side using `imgui.columns` or `imgui.begin_table`.
- Both C++ and Python versions must be implemented.
- Text is minimal: tagline + ≤ 3 sentences. No bullet-point lists in the UI.


## Non-goals
- Custom 3D OpenGL background (too risky for time budget — consider in a later session)
- ImmVision showcase (too specialized for an intro)
- Comprehensive library listing in the UI
- Angled-header table demo (feels like reference docs, not intro)
- Integration in the standalone imgui_manual (for a later session)


## Open questions
- Size of each mini-demo panel: equal width, or heart/Lorenz wider than color picker?
- Should the Lorenz demo include its parameter sliders, or just the plot (cleaner for intro)?
- Wording of the tagline / description: take from `intro.md` or rewrite?
