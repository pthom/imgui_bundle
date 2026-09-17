// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include "imgui_internal_pywrappers.h"
#include <cstring>


namespace ImGui
{
    std::tuple<ImGuiID, ImGuiID, ImGuiID> DockBuilderSplitNode_Py(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir)
    {
        ImGuiID id0, id1, id2;
        id0 = DockBuilderSplitNode(node_id, split_dir, size_ratio_for_node_at_dir, &id1, &id2);
        return std::make_tuple(id0, id1, id2);
    }

    DockBuilderSplitNodeResult DockBuilderSplitNode(ImGuiID node_id, ImGuiDir split_dir, float size_ratio_for_node_at_dir)
    {
        DockBuilderSplitNodeResult r;
        DockBuilderSplitNode(node_id, split_dir, size_ratio_for_node_at_dir, &r.id_at_dir, &r.id_at_opposite_dir);
        return r;
    }

    // Note: the text is copied to a fixed-size buffer (8000 chars), as in the previous implementation
    static constexpr size_t kInputTextBufferSize = 8000;

    bool InputTextEx(const char* label, const char* hint, std::string* s, const ImVec2& size_arg, ImGuiInputTextFlags flags, ImGuiInputTextCallback callback)
    {
        char buffer[kInputTextBufferSize];
        strncpy(buffer, s->c_str(), kInputTextBufferSize);
        buffer[kInputTextBufferSize - 1] = '\0';
        bool result = InputTextEx(label, hint, buffer, (int)kInputTextBufferSize, size_arg, flags, callback, nullptr);
        *s = buffer;
        return result;
    }

    bool TempInputText(const ImRect& bb, ImGuiID id, const char* label, std::string* s, ImGuiInputTextFlags flags)
    {
        char buffer[kInputTextBufferSize];
        strncpy(buffer, s->c_str(), kInputTextBufferSize);
        buffer[kInputTextBufferSize - 1] = '\0';
        bool result = TempInputText(bb, id, label, buffer, kInputTextBufferSize, flags);
        *s = buffer;
        return result;
    }
}
