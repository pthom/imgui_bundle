// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include "imgui_pywrappers.h"


namespace ImGui
{
    bool SetDragDropPayload_PyId(const char* type, ImGuiPayloadId dataId, ImGuiCond cond)
    {
        bool r = ImGui::SetDragDropPayload(type, &dataId, sizeof(ImGuiPayloadId), cond);
        return r;
    }

    static std::optional<ImGuiPayload_PyId> nativePayloadToPython(const ImGuiPayload* nativePayload)
    {
        if (nativePayload == nullptr)
            return std::nullopt;
        ImGuiPayload_PyId r;
        r.DataId = *(const ImGuiPayloadId*)nativePayload->Data;
        r.Type  = nativePayload->DataType;
        return r;
    }

    std::optional<ImGuiPayload_PyId>   AcceptDragDropPayload_PyId(const char* type, ImGuiDragDropFlags flags)
    {
        const ImGuiPayload* nativePayload = ImGui::AcceptDragDropPayload(type, flags);
        return nativePayloadToPython(nativePayload);
    }

    std::optional<ImGuiPayload_PyId>   GetDragDropPayload_PyId()
    {
        const ImGuiPayload* nativePayload = ImGui::GetDragDropPayload();
        return nativePayloadToPython(nativePayload);
    }
}
