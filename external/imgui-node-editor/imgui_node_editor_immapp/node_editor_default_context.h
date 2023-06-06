// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once

#include "imgui-node-editor/imgui_node_editor.h"


using NodeEditorContext = ax::NodeEditor::EditorContext;

IMGUI_NODE_EDITOR_API NodeEditorContext* DefaultNodeEditorContext_Immapp();
IMGUI_NODE_EDITOR_API void SuspendNodeEditorCanvas_Immapp();
IMGUI_NODE_EDITOR_API void ResumeNodeEditorCanvas_Immapp();
