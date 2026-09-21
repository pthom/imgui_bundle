"""Test the parts of the imgui-node-editor API that are specific to Python:
functions that return a list (the C++ versions fill an array), and Style.color_() / set_color_()"""

import pathlib

from imgui_bundle import hello_imgui, imgui, immapp, imgui_node_editor as ed, ImVec4


def test_node_editor_python_api() -> None:
    results: dict[str, object] = {}

    def gui() -> None:
        frame = imgui.get_frame_count()
        ed.begin("editor")
        for node_id in (1, 2, 3):
            ed.begin_node(ed.NodeId(node_id))
            imgui.text(f"node {node_id}")
            ed.end_node()
        if frame == 3:
            ed.select_node(ed.NodeId(2))
            ed.select_node(ed.NodeId(3), True)
        if frame == 6:
            results["selected_nodes"] = sorted(n.id() for n in ed.get_selected_nodes())
            results["selected_links"] = [link.id() for link in ed.get_selected_links()]
            results["ordered_node_ids"] = sorted(n.id() for n in ed.get_ordered_node_ids())
            results["action_context_nodes"] = sorted(n.id() for n in ed.get_action_context_nodes())
            results["action_context_links"] = [link.id() for link in ed.get_action_context_links()]

            style = ed.get_style()
            style.set_color_(ed.StyleColor.bg, ImVec4(0.1, 0.2, 0.3, 1.0))
            color = style.color_(ed.StyleColor.bg)
            results["color_roundtrip"] = (round(color.x, 2), round(color.y, 2), round(color.z, 2), round(color.w, 2))
            color.x = 0.9  # color_() returns a reference: the style must see the change
            results["color_is_reference"] = round(style.color_(ed.StyleColor.bg).x, 2)
        ed.end()
        if frame == 8:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test node editor python API"
    runner_params.callbacks.show_gui = gui
    runner_params.ini_disable = True
    addons = immapp.AddOnsParams()
    addons.with_node_editor = True
    immapp.run(runner_params, addons)

    assert results["selected_nodes"] == [2, 3]
    assert results["selected_links"] == []
    assert results["ordered_node_ids"] == [1, 2, 3]
    # imgui-node-editor builds the "action context" lists from the selected objects
    assert results["action_context_nodes"] == [2, 3]
    assert results["action_context_links"] == []
    assert results["color_roundtrip"] == (0.1, 0.2, 0.3, 1.0)
    assert results["color_is_reference"] == 0.9
    print("OK test_node_editor_python_api")


def test_config_settings_file(tmp_path: pathlib.Path) -> None:
    """Config.settings_file is a `const char*` in C++, and the editor keeps the pointer. In Python it is a property that owns
    a copy of the string: the str given by the caller may disappear, and None means "no settings file"."""
    import gc

    config = ed.Config()
    assert config.settings_file == "NodeEditor.json"  # default value of the C++ library

    settings_path = tmp_path / "node_editor_settings.json"
    config.settings_file = str(settings_path)  # the temporary str dies right after this line
    gc.collect()
    assert config.settings_file == str(settings_path)

    config.settings_file = None
    assert config.settings_file is None
    config.settings_file = ""
    assert config.settings_file == ""

    # An editor created with this config saves its state in the file, long after the str was garbage collected
    config.settings_file = str(settings_path)
    gc.collect()

    def gui() -> None:
        ed.begin("editor")
        ed.begin_node(ed.NodeId(1))
        imgui.text("node")
        ed.end_node()
        if imgui.get_frame_count() == 3:
            ed.set_node_position(ed.NodeId(1), imgui.ImVec2(123, 45))
        ed.end()
        if imgui.get_frame_count() == 8:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test node editor settings file"
    runner_params.callbacks.show_gui = gui
    runner_params.ini_disable = True
    addons = immapp.AddOnsParams()
    addons.with_node_editor_config = config
    immapp.run(runner_params, addons)

    assert settings_path.exists(), "the editor did not save its settings"
    assert '"x":123' in settings_path.read_text().replace(" ", "")
    print("OK test_config_settings_file")


if __name__ == "__main__":
    test_node_editor_python_api()
