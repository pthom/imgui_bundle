#include "imgui.h"
#include <hello_imgui/hello_imgui.h>

void Gui() {                                                                // 1.
    ImGui::Text("Hello, World");                                            // 2.
}

int main() {
    HelloImGui::Run(                                                        // 3.
        Gui,             // guiFunction
        "Hello, World!", // windowTitle
        true);           // windowSizeAuto
}
