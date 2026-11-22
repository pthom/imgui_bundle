"""The node editor's Config.custom_zoom_levels from Python: a list of positive, ascending scales."""

import pytest
import imgui_bundle

pytestmark = pytest.mark.skipif(
    not imgui_bundle.has_submodule("imgui_node_editor"),
    reason="imgui_node_editor submodule not available in this build",
)


def test_custom_zoom_levels() -> None:
    from imgui_bundle import imgui_node_editor as ed

    config = ed.Config()
    assert config.custom_zoom_levels == []  # the default levels
    config.custom_zoom_levels = [1.0, 2.0, 4.0]
    assert config.custom_zoom_levels == [1.0, 2.0, 4.0]
    for bad in ([2.0, 1.0], [0.0, 1.0], [1.0, 1.0]):
        with pytest.raises(ValueError):
            config.custom_zoom_levels = bad
    assert config.custom_zoom_levels == [1.0, 2.0, 4.0]  # unchanged by a refused value
