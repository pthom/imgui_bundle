"""Shortcuts in the browser on macOS: what Dear ImGui receives for Cmd and Ctrl.

With io.config_mac_osx_behaviors, Dear ImGui swaps Cmd and Ctrl as the keys arrive, so that Cmd+C copies. Its default
is always False in a browser build: hello_imgui turns it on when the browser runs on an Apple platform (the log shows
it at the first frame). The checkbox toggles it (for the next key events). "C down" tells whether C stays down after
Cmd+C: browsers on macOS may not send its key-up while Cmd is held. Run it in the demo runner:
    http://localhost:6789/?file=sandbox%2Fsandbox_mac_shortcuts.py
"""
from imgui_bundle import imgui, immapp, rich_md

text = "Select some of this text, copy it, paste it below."
log: list[str] = []


def gui() -> None:
    global text
    io = imgui.get_io()
    if not log:  # the backend sets it when the app starts
        log.append(f"first frame: io.config_mac_osx_behaviors = {io.config_mac_osx_behaviors}")
    _, io.config_mac_osx_behaviors = imgui.checkbox("config_mac_osx_behaviors (Cmd acts as Ctrl)",
                                                    io.config_mac_osx_behaviors)
    imgui.text(f"Modifiers now: key_ctrl={io.key_ctrl}  key_super={io.key_super}  key_alt={io.key_alt}"
               f"    C down: {imgui.is_key_down(imgui.Key.c)}")
    for key in (imgui.Key.c, imgui.Key.v):
        if imgui.is_key_pressed(key, False):
            log.append(f"{imgui.get_key_name(key)} pressed with key_ctrl={io.key_ctrl} key_super={io.key_super}")

    imgui.separator()
    rich_md.render("Some **markdown** to select with the mouse, then copy (Cmd+C, or Ctrl+C).")
    _, text = imgui.input_text_multiline("##text", text, imgui.ImVec2(-1, imgui.get_text_line_height() * 5))

    imgui.separator()
    imgui.text("Log (last 12)")
    for line in log[-12:]:
        imgui.text(line)


immapp.run(gui, window_title="Mac shortcuts", window_size=(760, 520), with_markdown=True)
