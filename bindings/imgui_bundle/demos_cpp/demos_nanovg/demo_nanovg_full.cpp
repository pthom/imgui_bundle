#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nvg_imgui/nvg_imgui.h"

#include "demo_nanovg_full/demo_nanovg_full_impl.h"
#include <algorithm>


struct MyNvgDemo
{
    bool Blowup = false;
    DemoData nvgDemoData = {};
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

    void Render(float width, float height, int mousex, int mousey, float t)
    {
        renderDemo(vg, mousex, mousey, width, height, t, Blowup, &nvgDemoData);
    }

};



struct AppState
{
    std::unique_ptr<MyNvgDemo> myNvgDemo;
    NVGcontext * vg = nullptr;

    std::unique_ptr<NvgImgui::NvgFramebuffer> myFramebuffer;

    ImVec4 ClearColor = ImVec4(0.2f, 0.2f, 0.2f, 1.f);
#ifdef HELLOIMGUI_HAS_METAL
    bool DisplayInFrameBuffer = true;
#else
    bool DisplayInFrameBuffer = false;
#endif
};



int main(int, char**)
{
    ChdirBesideAssetsFolder();

    AppState appState;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    runnerParams.appWindowParams.windowGeometry.size = {1200, 900};

    runnerParams.callbacks.EnqueuePostInit([&]()
    {
        appState.vg = NvgImgui::CreateNvgContext_HelloImGui(
            NvgImgui::NVG_ANTIALIAS | NvgImgui::NVG_STENCIL_STROKES); // | NvgImgui::NVG_DEBUG);
        appState.myNvgDemo = std::make_unique<MyNvgDemo>(appState.vg);
        int nvgImageFlags = 0; //NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        appState.myFramebuffer = std::make_unique<NvgImgui::NvgFramebuffer>(appState.vg, 1000, 600, nvgImageFlags);
    });
    runnerParams.callbacks.EnqueueBeforeExit([&]()
    {
        appState.myNvgDemo.reset();
        appState.myFramebuffer.reset();
        NvgImgui::DeleteNvgContext_HelloImGui(appState.vg);
    });

    auto nvgDrawingFunction = [&](NVGcontext *vg, float width, float height)
    {
        double now = ImGui::GetTime();
        ImVec2 mousePos(
            ImGui::GetIO().MousePos.x - ImGui::GetMainViewport()->Pos.x,
            ImGui::GetIO().MousePos.y - ImGui::GetMainViewport()->Pos.y
            );
        // The scene is laid out for a width of 1000 pixels: narrower (a phone), it is scaled down
        float scale = (std::min)(1.f, width / 1000.f);
        nvgScale(vg, scale, scale);
        appState.myNvgDemo->Render(
            width / scale, height / scale, (int)(mousePos.x / scale), (int)(mousePos.y / scale), (float)now);
    };

#ifndef HELLOIMGUI_HAS_METAL
    runnerParams.callbacks.CustomBackground = [&]()
    {
        NvgImgui::RenderNvgToBackground(appState.vg, nvgDrawingFunction, appState.ClearColor);
    };
#endif

    runnerParams.callbacks.ShowGui = [&]()
    {
        ImGui::SetNextWindowPos(ImVec2(0, 0), ImGuiCond_Appearing);
        ImGui::Begin("My Window!", NULL, ImGuiWindowFlags_AlwaysAutoResize);

        if (appState.DisplayInFrameBuffer)
        {
            NvgImgui::RenderNvgToFrameBuffer(appState.vg, *appState.myFramebuffer, nvgDrawingFunction, appState.ClearColor);
            // 1000 pixels wide at most (the screen's width on a phone), with the framebuffer's aspect ratio
            float width = (std::min)(1000.f, ImGui::GetMainViewport()->WorkSize.x - HelloImGui::EmSize(2.f));
            ImGui::Image(appState.myFramebuffer->TextureId, ImVec2(width, width * 0.6f));
        }

        ImGui::Button("?##Note");
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("This is the complete NanoVG demo, ported to ImGui Bundle (C++ and Python)\n"
                              "It displays fake widgets, as a way to display NanoVG drawing capabilities.\n"
                              "However, those widgets are not interactive.\n");

        ImGui::Checkbox("Blowup", &appState.myNvgDemo->Blowup);
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("When checked, apply a simple transform to the drawing");

        ImGui::Checkbox("Display in FrameBuffer", &appState.DisplayInFrameBuffer);
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("When checked, the drawing is rendered to a FrameBuffer, and the  displayed as a texture");

        ImGui::SetNextItemWidth(HelloImGui::EmSize(15.f));
        ImGui::ColorEdit4("Clear color", &appState.ClearColor.x);
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("Background color of the drawing");

        ImGui::End();
    };

    runnerParams.fpsIdling.enableIdling = false;

    HelloImGui::Run(runnerParams);
    return 0;
}
