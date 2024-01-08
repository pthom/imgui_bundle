// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Handwritten wrappers around parts of the imgui API, when needed for the python bindings
#include "imgui.h"
#include <pybind11/pybind11.h>
#include <optional>


using ImGuiPayloadId = std::size_t;


struct ImGuiPayload_PyId
{
    // Stores an id that represents the payload. For example, this could be given by python `id(object)`
    ImGuiPayloadId DataId;

    // A string representing the type of payload. It cannot exceed 32 characters.
    std::string Type;
};


namespace ImGui
{
    // Note: the drag and drop API differs a bit between C++ and Python.
    // * In C++, ImGui::SetDragDropPayload and AcceptDragDropPayload are able to accept any kind of object
    //   (by storing a buffer whose size is the object size).
    //
    // Unfortunately, this behaviour cannot be reproduced in python.
    //
    // * In Python, you can use imgui.set_drag_drop_payload_py_id and imgui.accept_drag_drop_payload_py_id.
    //   These versions can only store an integer id for the payload
    //   (so that you may have to store the corresponding payload somewhere else)
    IMGUI_API bool                               SetDragDropPayload_PyId(const char* type, ImGuiPayloadId dataId, ImGuiCond cond = 0);
    IMGUI_API std::optional<ImGuiPayload_PyId>   AcceptDragDropPayload_PyId(const char* type, ImGuiDragDropFlags flags = 0);
    IMGUI_API std::optional<ImGuiPayload_PyId>   GetDragDropPayload_PyId();
}
