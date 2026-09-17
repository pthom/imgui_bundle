// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include "imgui_internal.h"
#include <optional>
#include <tuple>
#include <string>


namespace ImGui
{
    // DockBuilderSplitNode_Py() create 2 child nodes within 1 node. The initial node becomes a parent node.
    // This version is an adaptation for the python bindings (the C++ version uses two output parameters for the ID of the child nodes, this version returns a tuple)
    IMGUI_API std::tuple<ImGuiID, ImGuiID, ImGuiID>       DockBuilderSplitNode_Py(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir);

    // Result of DockBuilderSplitNode() (python version)
    struct DockBuilderSplitNodeResult { ImGuiID id_at_dir; ImGuiID id_at_opposite_dir; };
    // DockBuilderSplitNode() creates 2 child nodes within 1 node. The initial node becomes a parent node.
    // (python version: the two output parameters of the C++ version are returned in a struct)
    IMGUI_API DockBuilderSplitNodeResult DockBuilderSplitNode(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir);

    // Python versions of InputTextEx() and TempInputText(): the text buffer is a string (returned modified)
    IMGUI_API bool          InputTextEx(const char* label, const char* hint, std::string* s, const ImVec2& size_arg, ImGuiInputTextFlags flags, ImGuiInputTextCallback callback = NULL);
    IMGUI_API bool          TempInputText(const ImRect& bb, ImGuiID id, const char* label, std::string* s, ImGuiInputTextFlags flags);
}
