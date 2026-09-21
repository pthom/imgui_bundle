// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_node_editor_pywrappers/imgui_node_editor_pywrappers.h"


namespace ax
{
namespace NodeEditor
{
    // The functions below fill an array provided by the caller, and return the number of elements they wrote.
    // Called with a null array, they return the number of elements they would write.
    template<typename IdType, typename FillFunction>
    static std::vector<IdType> _FilledVector(FillFunction fill_function)
    {
        int count = fill_function(nullptr, 0);
        std::vector<IdType> ids((size_t)count);
        if (count > 0)
            fill_function(ids.data(), count);
        return ids;
    }

    std::vector<NodeId> GetSelectedNodes()
    {
        return _FilledVector<NodeId>([](NodeId* ids, int size) { return GetSelectedNodes(ids, size); });
    }

    std::vector<LinkId> GetSelectedLinks()
    {
        return _FilledVector<LinkId>([](LinkId* ids, int size) { return GetSelectedLinks(ids, size); });
    }

    std::vector<NodeId> GetActionContextNodes()
    {
        return _FilledVector<NodeId>([](NodeId* ids, int size) { return GetActionContextNodes(ids, size); });
    }

    std::vector<LinkId> GetActionContextLinks()
    {
        return _FilledVector<LinkId>([](LinkId* ids, int size) { return GetActionContextLinks(ids, size); });
    }

    std::vector<NodeId> GetOrderedNodeIds()
    {
        // GetOrderedNodeIds() has no "null array" mode: GetNodeCount() is the number of ids it writes
        std::vector<NodeId> ids((size_t)GetNodeCount());
        int count = ids.empty() ? 0 : GetOrderedNodeIds(ids.data(), (int)ids.size());
        ids.resize((size_t)count);
        return ids;
    }

} // namespace NodeEditor
} // namespace ax
