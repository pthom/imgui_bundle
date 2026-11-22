"""The node editor's zoom from Python (issue 515): the wheel lands exactly on custom_zoom_levels, and an app snaps the
zoom to a level with set_zoom(), once is_navigating() tells that a fit has ended."""

from imgui_bundle import imgui, immapp, imgui_node_editor as ed
from imgui_bundle.immapp import testing

LEVELS = [1.0, 2.0, 3.0, 4.0]


def test_node_editor_zoom_gui() -> None:
    state = {"snap": False, "navigate": False}
    seen: dict[str, object] = {}

    def gui() -> None:
        ed.begin("graph")
        ed.begin_node(ed.NodeId(1))
        imgui.text("Node")
        ed.end_node()
        if state["navigate"]:
            ed.navigate_to_content(0.3)
            state["navigate"] = False
            seen["navigating"] = ed.is_navigating()
        if state["snap"] and not ed.is_navigating():
            zoom = ed.get_zoom()
            nearest = min(LEVELS, key=lambda level: abs(level - zoom))
            if zoom != nearest:
                ed.set_zoom(nearest)
        seen["zoom"] = ed.get_zoom()
        ed.end()

    def test(ctx: imgui.test_engine.TestContext) -> None:
        ctx.sleep(0.3)
        ctx.mouse_move_to_pos(imgui.get_main_viewport().get_center())
        ctx.mouse_wheel_y(1.0)
        ctx.sleep(0.5)  # the wheel's animation lasts 0.15 s
        seen["after_wheel"] = seen["zoom"]
        state["snap"] = True
        state["navigate"] = True
        ctx.sleep(0.8)
        seen["after_fit"] = seen["zoom"]

    config = ed.Config()
    config.settings_file = None
    config.enable_smooth_zoom = False
    config.custom_zoom_levels = LEVELS
    add_ons = immapp.AddOnsParams(with_node_editor_config=config)
    testing.run(gui, test, window_size=(800, 600), add_ons_params=add_ons, run_speed=testing.TestRunSpeed.normal)

    assert seen["after_wheel"] == 2.0, seen
    assert seen["navigating"] is True, seen
    assert seen["after_fit"] in LEVELS, seen
