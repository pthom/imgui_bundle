// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include "imgui_internal.h"
#include <pybind11/pybind11.h>
#include <optional>
#include <tuple>


namespace ImGui
{
    // DockBuilderSplitNode_Py() create 2 child nodes within 1 node. The initial node becomes a parent node.
    // This version is an adaptation for the python bindings (the C++ version uses two output parameters for the ID of the child nodes, this version returns a tuple)
    IMGUI_API std::tuple<ImGuiID, ImGuiID, ImGuiID>       DockBuilderSplitNode_Py(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir);
}
