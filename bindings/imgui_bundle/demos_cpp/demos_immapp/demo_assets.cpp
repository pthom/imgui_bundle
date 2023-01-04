#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"


void show_gui()
{
    // Display Markdown text
    ImGuiMd::Render("Hello, _World_");
    // Display a static image, taken from assets/images/world.jpg
    HelloImGui::ImageFromAsset("images/world.jpg");

    // Display a button
    if (ImGui::Button("Bye"))
    {
        // ... and immediately handle its action if it is clicked!
        HelloImGui::GetRunnerParams()->appShallExit = true;
    }
}

int main()
{
    HelloImGui::SetAssetsFolder(DemosAssetsFolder());
    ImmApp::RunWithMarkdown(
        show_gui,
        "Hello, globe!",
        true // window_size_auto
        // Uncomment the next line to restore the window position and size from previous run
        // window_restore_previous_geometry=true
    );

    return 0;
}
