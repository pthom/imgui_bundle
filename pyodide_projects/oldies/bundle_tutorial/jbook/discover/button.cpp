#include "imgui.h"
#include <hello_imgui/hello_imgui.h>

class AppState {                                                // 1.
public:
    int counter = 0;                                            // 2.
};

void Gui(AppState& appState) {                                  // 3.
    ImGui::Text("Counter: %d", appState.counter);
    if (ImGui::Button("Increment"))                             // 4.
        appState.counter++;
    ImGui::SetItemTooltip("Click to increment the counter");    // 5.

    if (ImGui::Button("Exit")) {                                // 6.
        HelloImGui::GetRunnerParams()->appShallExit = true;
    }
}

int main() {
    AppState appState;                                          // 7.
    auto gui_fn = [&]() { Gui(appState); }; // 8.
    HelloImGui::Run(gui_fn, "Handling Button Clicks", true);    // 9.
}
