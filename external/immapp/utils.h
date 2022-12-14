#pragma once
#include "hello_imgui/hello_imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui_md/imgui_md_wrapper.h"

#include <optional>

namespace ImmApp
{
    // Chronometer in seconds
    double ClockSeconds();

    // Utilities for node editor
    using NodeEditorContext = ax::NodeEditor::EditorContext;
    NodeEditorContext* CurrentNodeEditorContext();
    void SuspendNodeEditorCanvas();
    void ResumeNodeEditorCanvas();

} // namespace ImmApp
