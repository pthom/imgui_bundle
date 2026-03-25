"""Sandbox to test imgui_knobs customizable colors with theme switching."""
from imgui_bundle import imgui, imgui_knobs, hello_imgui, immapp, ImVec4

# Knob state
knob_value = 0.5
knob_int_value = 50

# Custom color editors (RGBA) — base / hovered / active for each color set
use_custom = False
primary_base = [0.1, 0.45, 0.7, 1.0]
primary_hovered = [0.1, 0.5, 1.0, 1.0]
primary_active = [0.1, 0.5, 1.0, 1.0]
secondary_base = [0.7, 0.7, 0.7, 1.0]
secondary_hovered = [0.6, 0.6, 0.6, 1.0]
secondary_active = [0.6, 0.6, 0.6, 1.0]
track_base = [0.3, 0.3, 0.7, 1.0]
track_hovered = [0.3, 0.3, 0.7, 1.0]
track_active = [0.3, 0.3, 0.7, 1.0]

# Theme names
themes = [
    "Darcula (Dark)",
    "ImGui Dark",
    "ImGui Light",
    "ImGui Classic",
    "SoDark",
    "PhotoshopStyle",
]


def apply_theme(index: int):
    if index == 0:
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.darcula)
    elif index == 1:
        imgui.style_colors_dark()
    elif index == 2:
        imgui.style_colors_light()
    elif index == 3:
        imgui.style_colors_classic()
    elif index == 4:
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.so_dark_accent_blue)
    elif index == 5:
        hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.photoshop_style)


current_theme = 0


def gui():
    global knob_value, knob_int_value, use_custom, current_theme
    global primary_base, primary_hovered, primary_active
    global secondary_base, secondary_hovered, secondary_active
    global track_base, track_hovered, track_active

    em = hello_imgui.em_size()

    # --- Theme switcher ---
    imgui.text("Theme:")
    imgui.same_line()
    imgui.set_next_item_width(em * 15)
    changed, current_theme = imgui.combo("##theme", current_theme, themes)
    if changed:
        apply_theme(current_theme)

    # Show current WindowBg luminance
    bg = imgui.get_style().color_(imgui.Col_.window_bg)
    luminance = 0.299 * bg.x + 0.587 * bg.y + 0.114 * bg.z
    imgui.same_line()
    imgui.text(f"(WindowBg luminance: {luminance:.2f}, {'dark' if luminance < 0.5 else 'light'})")

    imgui.separator()

    # --- Custom colors toggle ---
    _, use_custom = imgui.checkbox("Use custom colors", use_custom)

    def col_to_imcolor(c):
        return imgui.ImColor(c[0], c[1], c[2], c[3])

    def color_set_editor(label: str, base, hovered, active):
        """Edit base/hovered/active colors for a color_set. Returns updated values."""
        if imgui.tree_node(label):
            _, base = imgui.color_edit4("Base##" + label, base)
            _, hovered = imgui.color_edit4("Hovered##" + label, hovered)
            _, active = imgui.color_edit4("Active##" + label, active)
            imgui.tree_pop()
        return base, hovered, active

    if use_custom:
        imgui.indent()
        primary_base, primary_hovered, primary_active = color_set_editor(
            "Primary (indicator)", primary_base, primary_hovered, primary_active)
        secondary_base, secondary_hovered, secondary_active = color_set_editor(
            "Secondary (circle)", secondary_base, secondary_hovered, secondary_active)
        track_base, track_hovered, track_active = color_set_editor(
            "Track (arc)", track_base, track_hovered, track_active)
        imgui.unindent()

        colors = imgui_knobs.KnobColors(
            primary=imgui_knobs.color_set(
                col_to_imcolor(primary_base), col_to_imcolor(primary_hovered), col_to_imcolor(primary_active)),
            secondary=imgui_knobs.color_set(
                col_to_imcolor(secondary_base), col_to_imcolor(secondary_hovered), col_to_imcolor(secondary_active)),
            track=imgui_knobs.color_set(
                col_to_imcolor(track_base), col_to_imcolor(track_hovered), col_to_imcolor(track_active)),
        )
        imgui_knobs.set_knob_colors(colors)
    else:
        imgui_knobs.unset_knob_colors()

    imgui.separator()

    # --- All knob variants ---
    variants = [
        ("Tick", imgui_knobs.ImGuiKnobVariant_.tick),
        ("Dot", imgui_knobs.ImGuiKnobVariant_.dot),
        ("Wiper", imgui_knobs.ImGuiKnobVariant_.wiper),
        ("WiperOnly", imgui_knobs.ImGuiKnobVariant_.wiper_only),
        ("WiperDot", imgui_knobs.ImGuiKnobVariant_.wiper_dot),
        ("Stepped", imgui_knobs.ImGuiKnobVariant_.stepped),
        ("Space", imgui_knobs.ImGuiKnobVariant_.space),
    ]

    imgui.text("All knob variants (float):")
    for i, (name, variant) in enumerate(variants):
        if i > 0:
            imgui.same_line()
        changed, knob_value = imgui_knobs.knob(
            name, knob_value, 0.0, 1.0, 0.0, "%.2f",
            variant, em * 4, imgui_knobs.ImGuiKnobFlags_.no_input.value)

    imgui.spacing()
    imgui.text("Int knob:")
    _, knob_int_value = imgui_knobs.knob_int(
        "BPM", knob_int_value, 60, 300, 0.0, "%i",
        imgui_knobs.ImGuiKnobVariant_.wiper_dot, em * 5)


immapp.run(gui, window_title="Knob Colors Sandbox", window_size=(900, 500))
