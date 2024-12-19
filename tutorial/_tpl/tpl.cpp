#include "imgui.h"
#include <hello_imgui/hello_imgui.h>

class AppState {
};

void Gui(AppState& appState) {
}

int main() {
    AppState appState;
    auto gui_fn = [&]() { Gui(appState); };
    HelloImGui::Run(gui_fn, "TEMPLATE", true);
}
