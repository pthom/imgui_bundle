# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle._imgui_bundle import immapp_cpp as immapp_cpp  # type: ignore
from imgui_bundle._imgui_bundle.immapp_cpp import (  # type: ignore
    clock_seconds,

    default_node_editor_context,
    default_node_editor_config,

    delete_node_editor_settings,
    has_node_editor_settings,
    node_editor_settings_location,

    em_size,
    em_to_vec2,
    pixels_to_em,
    pixel_size_to_em,

    run,
    run_with_markdown,
    AddOnsParams,
    snippets,

    begin_plot_in_node_editor,
    end_plot_in_node_editor,
    show_resizable_plot_in_node_editor,
    show_resizable_plot_in_node_editor_em,
    widget_with_resize_handle_in_node_editor,
    widget_with_resize_handle_in_node_editor_em,
)

# Note: to enable font awesome 6:
#     runner_params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome_4
from imgui_bundle.immapp import icons_fontawesome_6 as icons_fontawesome_6
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome  # v4

from imgui_bundle.immapp.immapp_utils import (
    static as static,
    run_anon_block as run_anon_block,
)
from imgui_bundle.immapp.immapp_notebook import run_nb as run_nb
from imgui_bundle.immapp import immapp_code_utils

from imgui_bundle._imgui_bundle.hello_imgui import (  # type: ignore
    RunnerParams as RunnerParams,
    SimpleRunnerParams as SimpleRunnerParams,
)

__all__ = [
    "clock_seconds",
    "default_node_editor_context",
    "default_node_editor_config",
    "delete_node_editor_settings",
    "has_node_editor_settings",
    "node_editor_settings_location",
    "em_size",
    "em_to_vec2",
    "pixels_to_em",
    "pixel_size_to_em",
    "run",
    "run_with_markdown",
    "AddOnsParams",
    "icons_fontawesome",  # v4
    "icons_fontawesome_4",
    "icons_fontawesome_6",
    "static",
    "run_anon_block",
    "run_nb",
    "RunnerParams",
    "SimpleRunnerParams",
    "snippets",
    "begin_plot_in_node_editor",
    "end_plot_in_node_editor",
    "show_resizable_plot_in_node_editor",
    "show_resizable_plot_in_node_editor_em",
    "widget_with_resize_handle_in_node_editor",
    "widget_with_resize_handle_in_node_editor_em",
    "immapp_code_utils",
]
