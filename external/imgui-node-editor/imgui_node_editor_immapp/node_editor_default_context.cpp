// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#define IMGUI_DEFINE_MATH_OPERATORS
#include "node_editor_default_context.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"


namespace ImmApp
{
    ax::NodeEditor::EditorContext* DefaultNodeEditorContext();
}

ax::NodeEditor::EditorContext* DefaultNodeEditorContext_Immapp()
{
    return ImmApp::DefaultNodeEditorContext();
}

void SuspendNodeEditorCanvas_Immapp()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Suspend();
}

void ResumeNodeEditorCanvas_Immapp()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Resume();
}
