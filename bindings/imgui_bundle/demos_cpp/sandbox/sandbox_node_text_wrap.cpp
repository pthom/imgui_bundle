#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui_md_wrapper.h"
#include "immapp/immapp.h"

namespace ed = ax::NodeEditor;

static float gNodeWidth = 400;
static float gValue = 5.f;
bool gResetNodeLayout = false;

void Gui()
{
    // This whole function is using only ImGui and ImGui Node editor
    ed::Begin("My Editor");

    ed::BeginNode(1);

    if (gResetNodeLayout)
    {
        gResetNodeLayout = false;
    }
    else
    {
        // Test ImGui::Separator: it should use the actual node width.
        ImGui::TextWrapped("Below is a separator and a separator text. They should use the actual node width.");
        ImGui::Separator();
        ImGui::SeparatorText("Hello");

        //
        // A dummy button, to artificially set the node width
        //
        ImGui::SeparatorText("Dummy Button");
        ImGuiMd::RenderUnindented(R"(
            This is a _dummy button_, to artificially set the node width.
            Below it is a fixed width slider, which enables to set this button's width.
        )");
        ImVec2 dummyButtonSize(gNodeWidth, 20);
        ImGui::Button("Dummy", dummyButtonSize);
        // With a fixed width slider, so that we can set the node width.
        ImGui::SetNextItemWidth(200.f);
        ImGui::SliderFloat("width", &gNodeWidth, 0, 700);

        //
        // Test ImGui::TextWrapped: it should use the actual node width.
        //
        // Notes:
        // * If using the slider to make the node wider, the wrapped text with will adapt.
        // * After that if you try to reduce the node width, The wrapped text with will not reduce
        //   (This is because the node caches its previous size, and the wrapped text will use it.
        //   This is okay.)
        ImGui::SeparatorText("Test TextWrapped");
        ImGui::TextWrapped(R"(
Note:
    * If using the slider to make the node wider, the wrapped text with will adapt.
    * After that if you try to reduce the node width, The wrapped text with will not reduce (This is because the node caches its previous size, and the wrapped text will use it. This is okay.)
    )");

        //
        // Test ImGui::SliderFloat: it should use the actual node width.
        //
        ImGui::SeparatorText("Slider with default width");
        ImGui::TextWrapped("Below is a slider using the default width. It should be the same width as the node (There is a hard code max label size, which corresponds to 4 wide characters)." );
        ImGui::SliderFloat("value##2", &gValue, 0, 20.f);

        //
        // Reset Node Layout
        //
        ImGui::SeparatorText("Reset Layout");
        ImGuiMd::RenderUnindented(R"(
            Click the button below to reset the node layout. Its content will disappear for one frame,
            allowing it to be re-laid out with the new width.
        )");
        if (ImGui::Button("Reset Layout"))
            gResetNodeLayout = true;
    }
    ed::EndNode();

    ed::End();
}



int main()
{
    // Specific to ImGui Bundle (replace this by another runner if desired)
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;

    // Specific to ImGui Bundle (replace this by another runner if desired)
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withNodeEditor = true;

    // Change the node editor config to force ImGui to use the node width.
    addOnsParams.withNodeEditorConfig = ed::Config();
    addOnsParams.withNodeEditorConfig->ForceWindowContentWidthToNodeWidth = true;

    addOnsParams.withMarkdown = true;

    ImmApp::Run(runnerParams, addOnsParams);
}

#else // #if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
int main(){}
#endif
