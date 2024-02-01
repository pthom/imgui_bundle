// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include "imgui_internal_pywrappers.h"


namespace ImGui
{
    std::tuple<ImGuiID, ImGuiID, ImGuiID> DockBuilderSplitNode_Py(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir)
    {
        ImGuiID id0, id1, id2;
        id0 = DockBuilderSplitNode(node_id, split_dir, size_ratio_for_node_at_dir, &id1, &id2);
        return std::make_tuple(id0, id1, id2);
    }
}
