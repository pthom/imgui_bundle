#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nanovg.h"

#include "nanovg_demo/nanovg_demo.h"

#include <memory>
#include <functional>

using NvgDrawingFunction = std::function<void(float width, float height)>;


void RenderNvgBackground(NvgDrawingFunction nvgDrawingFunction)
{
    auto vg = ImmApp::NanoVGContext();
    auto displaySize = ImGui::GetIO().DisplaySize;
    float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;

    nvgBeginFrame(vg, displaySize.x, displaySize.y, pixelRatio);
    nvgDrawingFunction(displaySize.x, displaySize.y);
    nvgEndFrame(vg);
}


struct MyNvgDemo
{
    bool Blowup = false;
    DemoData nvgDemoData;
    NVGcontext* vg;

    MyNvgDemo(NVGcontext* _vg)
        : vg(_vg)
    {
        int status = loadDemoData(vg, &nvgDemoData);
        IM_ASSERT((status == 0) && "Could not load demo data!");
    }

    ~MyNvgDemo()
    {
        freeDemoData(vg, &nvgDemoData);
    }

    void Render(float width, float height)
    {
        // Clear background
        {
            nvgBeginPath(vg);
            nvgRect(vg, 0, 0, width, height);
            nvgFillColor(vg, nvgRGBA(50, 50, 50, 255));
            nvgFill(vg);
        }

        double now = ImGui::GetTime();
        auto mousePos = ImGui::GetMousePos();
        renderDemo(vg, mousePos.x, mousePos.y, width, height, now, Blowup, &nvgDemoData);
    }

};


struct AppState
{
    std::unique_ptr<MyNvgDemo> myNvgDemo;
};



int main(int, char**)
{
    ChdirBesideAssetsFolder();

    AppState appState;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    runnerParams.appWindowParams.windowGeometry.size = {1000, 600};
    ImmApp::AddOnsParams addons;
    addons.withNanoVG = true;

    runnerParams.callbacks.PostInit = [&]()
    {
        auto vg = ImmApp::NanoVGContext();
        appState.myNvgDemo = std::make_unique<MyNvgDemo>(vg);
    };
    runnerParams.callbacks.BeforeExit = [&]()
    {
        appState.myNvgDemo.release();
    };


    runnerParams.callbacks.CustomBackground = [&]()
    {
        //auto displaySize = ImGui::GetIO().DisplaySize;
        //appState->Render(displaySize.x, displaySize.y);

        auto nvgDrawingFunction = [&](float width, float height)
        {
            appState.myNvgDemo->Render(width, height);
        };
        RenderNvgBackground(nvgDrawingFunction);
    };

    runnerParams.callbacks.ShowGui = [&]()
    {
        ImGui::Begin("My Window!");
        ImGui::Text("Hello, _World_");
        ImGui::End();
    };

    ImmApp::Run(runnerParams, addons);
    return 0;
}
