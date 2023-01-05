#pragma once

#include "imgui-node-editor/imgui_node_editor.h"


using NodeEditorContext = ax::NodeEditor::EditorContext;

NodeEditorContext* DefaultNodeEditorContext_Immapp();
void SuspendNodeEditorCanvas_Immapp();
void ResumeNodeEditorCanvas_Immapp();
