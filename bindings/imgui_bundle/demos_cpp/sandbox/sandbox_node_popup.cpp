// Demonstrates a collection of patches to imgui-node-editor and imgui
// to make them work together in a smoother way.
// - Handle node width in separators
// - Handle Popups
// - Warn users if using BeginChild / EndChild
// - Handle InputTextMultiline
//
// Source for https://github.com/thedmd/imgui-node-editor/issues/310
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui-node-editor/imgui_node_editor.h"

namespace ed = ax::NodeEditor;

ImVec4 gColor(0.1, 0.2, 0.8, 1);
std::string gLoremIpsum = "Lorem ipsum dolor sit amet, consectetur adipiscing, \n"
                    "sed do eiusmod tempor incididunt \n"
                    "ut labore et dolore magna aliqua. "
                    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. \n"
                    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \n"
                    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

void Gui()
{
    ed::Begin("My Node Editor");

    ed::BeginNode(1);

    ImGui::Dummy(ImVec2(500, 0));

    ImGuiMd::RenderUnindented(R"(
        This is a sandbox to test various patches to imgui-node-editor and imgui.
        The goal is to make imgui-node-editor work smoothly with imgui.
        These patches are applied inside [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle).
        The code for this demo is available [here](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/sandbox/sandbox_node_popup.cpp).
    )");

    if (ImGui::CollapsingHeader("Handle node width in separators"))
    {
        ImGuiMd::RenderUnindented(R"(
            Thanks to [this patch](https://github.com/pthom/imgui-node-editor/commit/148a06dcbddcf10a77382bff21bc168d5e518a65),
            `ImGui::SeparatorText()`, `ImGui::Separator()`, and `ImGui::CollapsingHeader()` use the actual node width.
            It was proposed [here](https://github.com/thedmd/imgui-node-editor/issues/298)

            (The collapsing header you are looking at was fixed by this patch)
        )");
        ImGui::SeparatorText("SeparatorText example");
        ImGui::Text("Below is a separator");
        ImGui::Separator();
    }

    if (ImGui::CollapsingHeader("Handle Popups"))
    {
        ImGuiMd::RenderUnindented(R"(
            [@lukaasm](https://github.com/lukaasm) proposed a patch [here](https://github.com/thedmd/imgui-node-editor/issues/242#issuecomment-1681806764),
            which solves many issues with popups in the node editor (by automatically suspending the canvas, and placing popups correctly).

            Example implementation for this patch:
            * inside [imgui-node-editor](https://github.com/pthom/imgui-node-editor/commit/8b178424fcf7c452a7b5c14fb90b02487615ff70)
            * inside [imgui](https://github.com/pthom/imgui/commit/1942772deac459210a321251bcc8857ac8170035)

            With this patch, `ImGui::ColorEdit`, `ImGui::Begin/EndCombo` will work correctly.
        )");
        ImGui::SetNextItemWidth(200.f);
        ImGui::ColorEdit4("Color", &gColor.x);

        static int item_current_2 = 0;
        ImGui::Combo("combo", &item_current_2, "aaaa\0bbbb\0cccc\0dddd\0eeee\0\0");
    }

    if (ImGui::CollapsingHeader("Warn users / BeginChild"))
    {
        ImGuiMd::RenderUnindented(R"(
            imgui-node-editor remains incompatible with `ImGui::BeginChild()` and `ImGui::EndChild()`.

            Below is the list of ImGui widgets which are concerned (because they use BeginChild/EndChild):

            * ImGui::InputTextMultiline()
            * ImGui::BeginListbox() and ImGui::EndListbox()
            * ImGui::BeginChild() and ImGui::EndChild()

            We can warn the developer whenever they use these functions inside a node:

            * patch inside [imgui](https://github.com/pthom/imgui/commit/52c093f4f259d7e99579e683b4f8c0247e2e8271)
            * patch inside [imgui-node-editor](https://github.com/pthom/imgui-node-editor/commit/e4704e6a646e90f6b0df41240539261d1ede9d55)
        )");

        static bool showChildWindow = false;
        ImGui::Text("Click to show a child window (this will trigger an IM_ASSERT!)");
        ImGui::Checkbox("Show Child Window", &showChildWindow);
        if (showChildWindow)
        {
            ImGui::BeginChild("child window", ImVec2(200, 200), true);
            ImGui::Text("Hello from child window");
            ImGui::EndChild();
        }
    }

    if (ImGui::CollapsingHeader("Handle InputTextMultiline"))
    {
        ImGuiMd::RenderUnindented(R"(
            By default `InputTextMultiline` uses a child window, which is not compatible with the node editor.
            An additional patch adapts its behavior, by showing a preview within a single line text input,
            followed by a "..." button which triggers a popup with the full text edition.

            To apply this, two patches are required:

            * inside imgui-node-editor: A patch on top of @lukaasm's [patch](https://github.com/thedmd/imgui-node-editor/issues/242#issuecomment-1681806764):
              we need to handle the "depth" of call to ImGui::Begin/End (only the first call should trigger):
              it is available [here](https://github.com/pthom/imgui-node-editor/commit/3966e21ac9d43b159e6d19493e20ab5e2e8465ec)
            * inside imgui: A patch for InputTextMultiline is available [here]( https://github.com/pthom/imgui/commit/b51b61346c5d7b98b960624b43a330279ccc8308)

        )");
        //ImGui::SetNextItemWidth(200);
        ImGui::InputTextMultiline("lorem ipsum", &gLoremIpsum, ImVec2(0, ImGui::GetTextLineHeight() * 16));
    }

    ed::EndNode();

    ed::End();
}


int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;
    ImmApp::AddOnsParams addOnsParams;
    runnerParams.callbacks.ShowGui = Gui;
    addOnsParams.withMarkdown = true;
    addOnsParams.withNodeEditor = true;
    addOnsParams.withNodeEditorConfig = ed::Config();
    addOnsParams.withNodeEditorConfig->ForceWindowContentWidthToNodeWidth = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
#else
int main() {}
#endif
