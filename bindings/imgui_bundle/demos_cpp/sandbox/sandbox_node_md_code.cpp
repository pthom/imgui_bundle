#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui-node-editor/imgui_node_editor.h"


namespace ed = ax::NodeEditor;

void Gui()
{
    ImGuiMd::RenderUnindented(R"(
        Below is a code block rendered in markdown outside of a node editor: it should use ImGuiColorTextEdit

        ```cpp
        // This is a code block
        int main() {
            return 0;
        }
        ```
    )");

    ed::Begin("My Node Editor");
    ed::BeginNode(1);

    ImGui::Dummy(ImVec2(500, 0));
    ImGuiMd::RenderUnindented(R"(
        Below is a code block rendered in markdown inside a node editor:
        it should not use ImGuiColorTextEdit, but instead render as a simple code block,
        with no syntax highlighting (but using a code font).

        ```cpp
        // This is a code block
        int main() {
            return 0;
        }
        ```
    )");

    ed::EndNode();
    ed::End();
}


int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;
    ImmApp::AddOnsParams addOnsParams;
    runnerParams.callbacks.ShowGui = Gui;
    addOnsParams.withMarkdown = true;

    // important: force the window content width to be the same as the node width
    addOnsParams.withNodeEditor = true;
    addOnsParams.withNodeEditorConfig = ed::Config();
    addOnsParams.withNodeEditorConfig->ForceWindowContentWidthToNodeWidth = true;

    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
#else
int main() {}
#endif
