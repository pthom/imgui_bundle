#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui.h"


void DemoGui()
{
    ImGuiMd::RenderUnindented(R"(
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm.

         The following is the output of ImGui::ShowDemoWindow(), which is always accessible online with [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html).
    )");
    ImGui::ShowDemoWindow();
}
