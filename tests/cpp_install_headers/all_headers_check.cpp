// The installed package holds every library: each one's main header, at the path an app includes it from, and one
// function of each, which the linker must find. The calls never run (they would need a GUI): they make the link
// check each library. The markdown API of v1.92.900 (imgui_md_wrapper.h) has its own check, in tests/cpp_compat.
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"  // Dear ImGui's path
#include "imgui_stdlib.h"           // the include root, as earlier installs had it: both work, even together
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui_kit/imgui_kit.h"
#include "imgui_rich_md/rich_md.h"
#include "imgui_microtex/imgui_microtex.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "immvision/immvision.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "ImGuizmo.h"
#include "ImCurveEdit.h"
#include "ImSequencer.h"
#include "GraphEditor.h"
#include "ImFileDialog/ImFileDialog.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui-knobs/imgui-knobs.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imspinner/imspinner.h"
#include "imgui-command-palette/imcmd_command_palette.h"
#include "ImCoolBar/ImCoolBar.h"
#include "ImAnim/im_anim.h"
#include "nanovg.h"
#include "nvg_imgui/nvg_imgui.h"
#include "imgui_explorer/imgui_explorer.h"
#include "nlohmann/json.hpp"
#include "portable_file_dialogs/portable_file_dialogs.h"  // last: on Windows, it includes <windows.h> (min, max)

#include <cstdio>

int main(int argc, char**)
{
    if (argc > 1000)  // never true: the calls only give the linker one function of each library to find
    {
        ImGui::GetVersion();
        HelloImGui::GetRunnerParams();
        ImmApp::ClockSeconds();
        ImGuiKit::BeginFillRow("row");
        RichMd::Render("# markdown");
        RichMd::Latex::ClearTextureCache();
        ImPlot::CreateContext();
        ImPlot3D::CreateContext();
        ax::NodeEditor::CreateEditor();
        ImmVision::ClearTextureCache();
        ImGuiTestEngine_CreateContext();
        ImGuiTexInspect::CreateContext();
        ImGuizmo::Enable(true);
        ifd::FileDialog::Instance().Close();
        TextEditor editor;
        ImGuiKnobs::Knob("knob", nullptr, 0.f, 1.f);
        ImGui::Toggle("toggle", nullptr);
        ImCmd::CreateContext();
        ImGui::BeginCoolBar("bar");
        iam_update_begin_frame();
        nvgBeginFrame(nullptr, 1.f, 1.f, 1.f);
        ShowImGuiExplorerGui_Cpp();
        (void)nlohmann::json::parse("{}");
    }
    printf("imgui_bundle's installed package: every library's header included, and one function of each linked\n");
    return 0;
}
