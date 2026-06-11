#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

struct AppState {
    float globe_size = 100.0f;
};

void Gui(AppState& app_state) {
    HelloImGui::ImageFromAsset("images/world.png", ImVec2(app_state.globe_size, 0.0f));
    bool changed = ImGui::SliderFloat("Globe size", &app_state.globe_size, 20.0f, 200.0f);
}

int main() {
    AppState app_state;
    auto gui_fn = [&]() { Gui(app_state); };
    HelloImGui::Run(gui_fn, "Edit Values", false, false, {220, 220});
}