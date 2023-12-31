// Demo imgui_tex_inspect
// See equivalent python program: bindings/imgui_bundle/demos/demos_tex_inspect/demo_tex_inspect.py

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY

#ifdef IMGUI_BUNDLE_WITH_TEXT_INSPECT
#include "immapp/immapp.h"
#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"
#include "demo_utils/api_demos.h"

int main(int, char **)
{
    HelloImGui::SetAssetsFolder(DemosAssetsFolder());
    HelloImGui::SimpleRunnerParams runnerParams{.guiFunction = ImGuiTexInspect::ShowDemoWindow, .windowSize={1000, 1000}};
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withTexInspect = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}

#else // #ifdef IMGUI_BUNDLE_WITH_TEXT_INSPECT
int main(int, char **) { return 0; }
#endif

#endif // #ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY

