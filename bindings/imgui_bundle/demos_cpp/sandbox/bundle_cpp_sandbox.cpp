// This demo show how we can call ImGui::ErrorCheckEndFrameRecover()
// to recover from errors originating when ImGui::End() is not called (for example when an exception is raised)

#include "hello_imgui.h"
#include "imgui.h"
#include "imgui_internal.h"

void Gui()
{
    ImGui::Text("Hello");
    ImGui::ShowIDStackToolWindow();
}


int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;

    //runnerParams.useImGuiTestEngine = true;

    HelloImGui::Run(runnerParams);
    return 0;
}
