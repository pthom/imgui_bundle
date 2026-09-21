// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui-node-editor API, when needed for the python bindings
#pragma once
#include "imgui-node-editor/imgui_node_editor.h"
#include <vector>


namespace ax
{
namespace NodeEditor
{
    // The C++ API fills an array provided by the caller (`int GetSelectedNodes(NodeId* nodes, int size)`).
    // The Python API returns a list.

    IMGUI_NODE_EDITOR_API std::vector<NodeId> GetSelectedNodes();
    IMGUI_NODE_EDITOR_API std::vector<LinkId> GetSelectedLinks();

    IMGUI_NODE_EDITOR_API std::vector<NodeId> GetActionContextNodes();
    IMGUI_NODE_EDITOR_API std::vector<LinkId> GetActionContextLinks();

    // Returns the node ids, in the order they are drawn
    IMGUI_NODE_EDITOR_API std::vector<NodeId> GetOrderedNodeIds();

} // namespace NodeEditor
} // namespace ax
