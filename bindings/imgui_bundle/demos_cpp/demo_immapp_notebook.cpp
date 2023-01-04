#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"


void demo_immapp_notebook()
{
    ImGuiMd::RenderUnindented(R"(
        # Notebook integration
        ImmApp adds support for integration inside jupyter notebook: the application will be run in an external window, and a screenshot will be placed on the notebook after execution.

        This requires a window server, and will not run on google collab.

        Below is a screenshot, that you can test by running `jupyter notebook` inside `bindings/imgui_bundle/demos_python/notebooks`

    )");

    HelloImGui::ImageFromAsset("images/immapp_notebook_screenshot.jpg", ImVec2(0, HelloImGui::EmSize(30)));
}
