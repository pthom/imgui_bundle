// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once

#include "imgui-node-editor/imgui_node_editor.h"


using NodeEditorContext = ax::NodeEditor::EditorContext;

NodeEditorContext* DefaultNodeEditorContext_Immapp();
void SuspendNodeEditorCanvas_Immapp();
void ResumeNodeEditorCanvas_Immapp();
