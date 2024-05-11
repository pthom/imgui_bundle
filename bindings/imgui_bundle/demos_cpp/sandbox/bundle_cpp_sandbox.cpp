#include "hello_imgui/hello_imgui.h"
#include "imgui.h"


void Gui()
{
    ImGui::Text("Hello, world!");
}

int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;
    HelloImGui::Run(runnerParams);
    return 0;
}
