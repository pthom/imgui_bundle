#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"


void show_gui()
{
    // Display Markdown text
    ImGuiMd::Render("Hello, _World_");
    // Display a static image, taken from assets/images/world.png
    // Notes:
    //     * we use EmToVec2 to make sure the Gui render identically on high and low dpi monitors
    //     * we can specify only one dimension, and the image will be scaled proportionally to its size:
    //           in this example, the image height will correspond to 10 text lines
    HelloImGui::ImageFromAsset("images/world.png", ImmApp::EmToVec2(0.f, 10.f));

    // Display a button
    if (ImGui::Button("Bye"))
    {
        // ... and immediately handle its action if it is clicked!
        HelloImGui::GetRunnerParams()->appShallExit = true;
    }
}

int main(int, char**)
{
    ChdirBesideAssetsFolder();
    ImmApp::RunWithMarkdown(
        show_gui
        , "Hello, globe!"
        , true // window_size_auto
        // Uncomment the next line to restore the window position and size from previous run
        // , true // window_restore_previous_geometry
    );

    return 0;
}
