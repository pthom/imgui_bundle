from imgui_bundle.demos_python.sandbox.compare_wordle.wordle_app_imgui_bundle import end_horizontal_centered

# Wordle: GUI Framework Comparison

Same game, same logic (`wordle.py`), five different GUI frontends. The game logic is shared: a `GameState` class with `submit_guess()`, `keyboard_letter_states()`, and `reset()`. Only the GUI code differs.

## Line counts (GUI code only)

| Framework       | Lines | Paradigm                |
|-----------------|-------|-------------------------|
| ImGui Bundle    | 106   | Immediate mode, desktop |
| Textual         | 140   | Retained mode, terminal |
| NiceGUI         | 138   | Retained mode, web      |
| Kivy            | 165   | Retained mode, desktop  |
| PyQt6           | 167   | Retained mode, desktop  |

## The key difference: immediate vs retained mode

In **ImGui Bundle**, the `gui()` function runs every frame and directly renders the current state. There are no stored widget references, no event wiring, and no manual sync. The rendering code *is* the UI description:

```python
# ImGui: the grid rendering is the entire grid code
for row in range(6):
    begin_horizontal_centered("r", ...)
    for col in range(5):
        colored_button(ch, ls, tile)   # reads state, draws button
    end_horizontal_centered()
```

In every **retained-mode** framework (PyQt, NiceGUI, Textual, Kivy), the code splits into two parts:

1. **Build the UI** - create widgets, wire events, store references
2. **`refresh_ui()`** - iterate over all stored references, update each widget to match the state

This duplication is inherent to the retained-mode paradigm. The `refresh_ui()` function re-derives the same grid/keyboard state that ImGui computes implicitly each frame.

## Framework-by-framework notes

### ImGui Bundle (115 lines)
- `gui()` is called every frame - it reads state and draws, nothing else
- No widget references, no event callbacks, no sync logic
- Physical keyboard input: `imgui.is_key_pressed()` inline, no special setup
- On-screen keyboard clicks: `if colored_button(...):` returns True when clicked
- Centering: `imgui.spring()` on both sides of a horizontal layout
- Coloring: `push_style_color()` / `pop_style_color()`, 3 lines

### NiceGUI (142 lines)
- Web-based (runs in browser via localhost)
- Must store `tile_buttons[6][5]` and `key_buttons{}` for later updates
- `refresh_ui()` iterates 30 tiles + 26 keys to sync state to DOM
- Physical keyboard requires a JavaScript snippet injected via `ui.add_body_html()` plus a custom event bridge
- Key repeat must be filtered in JS (`e.repeat` check) - without this, holding a key types multiple letters
- Styling via CSS strings with `!important` overrides

### PyQt6 (171 lines)
- Classic desktop widget toolkit, signals/slots paradigm
- Required the most layout wrestling among working frameworks:
  - Grid tiles expanded vertically despite `setFixedSize()` - needed a wrapper `QWidget` with explicit pixel dimensions
  - Keyboard button alignment required `AlignVCenter` on each `addWidget()` call
  - All buttons need `setFocusPolicy(NoFocus)` to avoid stealing keyboard focus
  - Buttons need `setStyleSheet()` at creation AND in `refresh_ui()` (style resets on each call)
- `refresh_ui()` regenerates stylesheet strings for every button every time
- Physical keyboard: override `keyPressEvent()`, handle key codes manually

### Textual (140 lines)
- Terminal UI - renders in the console, surprisingly capable
- Uses CSS-like styling language, more structured than raw CSS strings
- Gotcha: method names starting with `_on_` are treated as event handlers by Textual's dispatch system - naming collision caused bugs until methods were renamed
- Widgets queried by string ID (`self.query_one("#tile-0-1", Static)`) rather than stored references - cleaner but slower
- Physical keyboard: `on_key` event handler built-in, no JS bridge needed

### Kivy (165 lines)
- Mobile-oriented framework with its own layout system
- Layout proved extremely difficult:
  - Centering widgets horizontally requires `AnchorLayout` wrappers, but those block touch events
  - `size_hint` defaults cause buttons to stretch to fill available space
  - `pos_hint={"center_x": 0.5}` is silently ignored inside `BoxLayout`
  - Coordinate system is bottom-left origin, causing touch dispatch bugs (clicking one button activates another)
- Requires workarounds for basic operations: `background_normal=""` to disable default button texture, `opacity=0` + `disabled=True` to hide a widget (no `hide()` method)
- The only framework where we could not get a fully correct layout

## Example: conditional UI (the "New Game" button)

A small but telling difference: the "New Game" button should only appear when the game is over.

**ImGui Bundle** - the button simply doesn't exist when the condition is false:

```python
# That's it. No button created, no reference stored, no visibility management.
if game_state.is_over and imgui.button("New Game"):
    game_state.reset()
```

**NiceGUI** - the button must always exist, with its visibility toggled:

```python
# At build time: create the button, store a reference, hide it
new_game_btn = ui.button("New Game", on_click=on_new_game).classes("mt-4")
new_game_btn.set_visibility(False)

# In refresh_ui(): sync visibility to state
new_game_btn.set_visibility(game_state.is_over)
```

The same pattern applies to PyQt (`hide()`/`setVisible()`), Textual (`styles.display`), and Kivy (`opacity` + `disabled` since Kivy has no `hide()`). In every retained-mode framework, the widget exists permanently and its visibility is managed as separate state. In ImGui, conditional UI is just an `if` statement.


## What this comparison shows

The retained-mode frameworks all share the same structural overhead:
- Store widget references at build time
- Wire event handlers to action functions
- Write a `refresh_ui()` that re-syncs all widgets to the current state
- Handle keyboard input through framework-specific mechanisms

ImGui's immediate mode eliminates all of this. The `gui()` function is both the UI description and the sync logic. When the state changes, the next frame automatically reflects it - no manual update needed.

For application code readability and conciseness, immediate mode wins clearly.
