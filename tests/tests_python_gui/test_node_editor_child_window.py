"""Child windows do not work inside the canvas of imgui-node-editor: BeginChild() inside a node must raise an error
(in Python, IM_ASSERT raises a RuntimeError), but not inside a popup opened from a node, nor while the editor is suspended."""

from imgui_bundle import hello_imgui, imgui, immapp, imgui_node_editor as ed


def test_begin_child_inside_node_raises() -> None:
    results: dict[str, object] = {"error_in_node": "", "child_in_suspended_editor": False}

    def gui() -> None:
        frame = imgui.get_frame_count()
        ed.begin("editor")
        ed.begin_node(ed.NodeId(1))
        imgui.text("node")
        if frame == 4:
            try:
                imgui.begin_child("child", hello_imgui.em_to_vec2(4, 4))
                imgui.end_child()
            except RuntimeError as e:
                results["error_in_node"] = str(e)
        if frame == 6:
            ed.suspend()
            if imgui.begin_child("child_suspended", hello_imgui.em_to_vec2(4, 4)):
                results["child_in_suspended_editor"] = True
            imgui.end_child()
            ed.resume()
        ed.end_node()
        ed.end()
        if frame == 8:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test node editor child window"
    runner_params.callbacks.show_gui = gui
    runner_params.ini_disable = True
    addons = immapp.AddOnsParams()
    addons.with_node_editor = True
    immapp.run(runner_params, addons)

    assert "BeginChild" in str(results["error_in_node"]), f"expected an error, got: {results['error_in_node']!r}"
    assert results["child_in_suspended_editor"] is True
    print("OK test_begin_child_inside_node_raises")


def test_markdown_code_block_inside_node() -> None:
    """A markdown code block is rendered inside a child window. Inside a node, immapp tells the markdown renderer
    that child windows cannot be used (MarkdownCallbacks.can_use_child_windows), and the block becomes inline code."""
    from imgui_bundle import rich_md

    results: dict[str, object] = {"error": "", "frames_with_markdown": 0}
    markdown = "Some text\n\n```python\nprint('hello')\n```\n"

    def gui() -> None:
        frame = imgui.get_frame_count()
        rich_md.render(markdown)  # outside of the editor: a real code block
        ed.begin("editor")
        ed.begin_node(ed.NodeId(1))
        imgui.dummy(hello_imgui.em_to_vec2(15, 0))
        try:
            rich_md.render(markdown)
            results["frames_with_markdown"] = int(str(results["frames_with_markdown"])) + 1
        except RuntimeError as e:
            results["error"] = str(e)
        ed.end_node()
        ed.end()
        if frame == 8:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test markdown code block inside a node"
    runner_params.callbacks.show_gui = gui
    runner_params.ini_disable = True
    addons = immapp.AddOnsParams()
    addons.with_node_editor = True
    addons.with_markdown = True
    immapp.run(runner_params, addons)

    assert results["error"] == "", f"markdown inside a node raised: {results['error']}"
    assert int(str(results["frames_with_markdown"])) > 3
    print("OK test_markdown_code_block_inside_node")


if __name__ == "__main__":
    test_begin_child_inside_node_raises()
    test_markdown_code_block_inside_node()
