// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once

#include "imgui-node-editor/imgui_node_editor.h"


using NodeEditorContext = ax::NodeEditor::EditorContext;

// The editor created by ImmApp::Run() with withNodeEditor or withNodeEditorConfig (an error if there is none)
IMGUI_NODE_EDITOR_API NodeEditorContext* DefaultNodeEditorContext_Immapp();
IMGUI_NODE_EDITOR_API void SuspendNodeEditorCanvas_Immapp(); // Same as ax::NodeEditor::Suspend()
IMGUI_NODE_EDITOR_API void ResumeNodeEditorCanvas_Immapp(); // Same as ax::NodeEditor::Resume()

// Ignores the user's input in the current editor this frame: e.g. the wheel over an image zooms it, not the canvas
IMGUI_NODE_EDITOR_API void DisableUserInputThisFrame();

// Sets the colors of the current editor from Dear ImGui's colors (ImmApp does it at each frame, unless disabled
// with updateNodeEditorColorsFromImguiColors = false)
IMGUI_NODE_EDITOR_API void UpdateNodeEditorColorsFromImguiColors();
