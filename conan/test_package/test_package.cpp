#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"
#include "immvision/immvision.h"

int main()
{
    ImmVision::UseRgbColorOrder();
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = [] {
        ImGuiMd::RenderUnindented("# imgui_bundle Conan package\nMarkdown, *ImPlot* and ImmVision are linked.");
        if (ImPlot::BeginPlot("plot")) { ImPlot::EndPlot(); }
    };
    params.windowTitle = "imgui_bundle test_package";
    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withImplot = true;
    ImmApp::Run(params, addons);
}
