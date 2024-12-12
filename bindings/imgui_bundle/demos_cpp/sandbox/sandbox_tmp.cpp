#include "hello_imgui/hello_imgui.h"
#include "imgui.h"


void Gui()
{
    ImGui::Text("Hello, world!");
}

int main()
{
    HelloImGui::Run(Gui);
}