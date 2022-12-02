#include "imgui_bundle/imgui_bundle.h"
#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"

#include "demos_interface.h"


// This returns a closure function that will later be invoked to run the app
GuiFunction make_closure_demo_tex_inspect()
{
    auto gui = [=]() mutable // mutable => this is a closure
    {
        ImGuiTexInspect::ShowDemoWindow();
    };
    return gui;
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    auto gui = make_closure_demo_tex_inspect();

    HelloImGui::SimpleRunnerParams runnerParams{.guiFunction = gui, .windowSize={1200, 1100}};
    ImGuiBundle::AddOnsParams addOnsParams;
    addOnsParams.withTexInspect = true;
    ImGuiBundle::Run(runnerParams, addOnsParams);

//    HelloImGui::RunnerParams runnerParams;
//    runnerParams.callbacks.ShowGui = gui;
//    runnerParams.appWindowParams.windowGeometry.size = {1200, 1000};
//    runnerParams.backendType = HelloImGui::BackendType::Sdl;
//    ImGuiBundle::AddOnsParams addOnsParams;
//    addOnsParams.withTexInspect = true;
//    ImGuiBundle::Run(runnerParams, addOnsParams);

}
#endif
