#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nanovg.h"
#include "nvg_imgui/nvg_imgui.h"
#include <math.h>


void DrawHeart(NVGcontext* vg, ImVec2 center, float size, float t)
{
    float x = center.x, y = center.y;
    float scale = sinf(t * 10) * 0.1f + 1.0f;  // Oscillating scale for the beating effect
    float scaledSize = size * scale;

    nvgSave(vg);

    // Change coord so that we draw in coords between (-1, 1) and (-1, 1)
    nvgTranslate(vg, x, y);
    nvgScale(vg, scaledSize, -scaledSize); // y points up

    nvgBeginPath(vg);
    {
        nvgMoveTo(vg, 0.f, 0.4f);
        nvgBezierTo(vg, 0.f, 0.5f,     0.1f, 1.f,     0.5f, 1.f);
        nvgBezierTo(vg, 0.9f, 1.f,     1.f, 0.7f,     1.f, 0.4f);
        nvgBezierTo(vg, 1.f, 0.2f,     0.75f, -0.2f,  0.5f, -0.4f);
        nvgBezierTo(vg, 0.2f, -0.65f,  0.f, -0.8f,    0.f, -1.f);

        nvgBezierTo(vg, 0.f, -0.8f,    -0.2f, -0.65f,  -0.5f, -0.4f);
        nvgBezierTo(vg, -0.75f, -0.2f, -1.f, 0.2f,     -1.f, 0.4f);
        nvgBezierTo(vg, -1.f, 0.7f,    -0.9f, 1.f,     -0.5f, 1.f);
        nvgBezierTo(vg, -0.1f, 1.f,    0.f, 0.5f,      0.f, 0.4f);
    }

    // Create gradient from top to bottom
    NVGpaint paint = nvgLinearGradient(vg, 0.f, 1.f, 0.f, -1.f, nvgRGBAf(1, 0, 0, 1), nvgRGBAf(0.2, 0, 0, 1));
    nvgFillPaint(vg, paint);
    nvgFill(vg);

    nvgStrokeColor(vg, nvgRGBA(0, 0, 255, 255));
    nvgStrokeWidth(vg, 0.05f);
    nvgStroke(vg);

    nvgRestore(vg);
}


void DrawNanoVgLabel(NVGcontext* vg, float width, float height)
{
    // The font used to write "NanoVG": it should be loaded only once
    static int fontId = -1;
    if (fontId == -1)
    {
        // Load the font
        auto fontPath = HelloImGui::AssetFileFullPath("fonts/Roboto/Roboto-Bold.ttf");
        fontId = nvgCreateFont(vg, "roboto", fontPath.c_str());
        if (fontId == -1) {
            fprintf(stderr, "Could not add font.\n");
            return; // Exit if the font cannot be added.
        }
    }

    nvgBeginPath(vg);
    nvgFontSize(vg, 128.f);
    nvgFontFaceId(vg, fontId);
    nvgTextAlign(vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    nvgSave(vg);
    nvgRotate(vg, -0.1f);
    nvgFillColor(vg, nvgRGBA(255, 100, 100, 255));
    nvgText(vg, 0.5f * width, 0.9f * height, "NanoVG", nullptr);
    nvgRestore(vg);
}


void DrawScene(NVGcontext* vg, float width, float height)
{
    nvgSave(vg);

    // Draw a white background
    nvgBeginPath(vg);
    nvgRect(vg, 0, 0, width, height);
    nvgFillColor(vg, nvgRGBA(255, 255, 255, 255));
    nvgFill(vg);

    // Draw NanoVG
    DrawNanoVgLabel(vg, width, height);

    // Draw a heart
    DrawHeart(vg, {width / 2.f, height / 2.f}, width * 0.2f, ImGui::GetTime());

    nvgRestore(vg);
};


using NvgFramebufferPtr = std::unique_ptr<NvgImgui::NvgFramebuffer>;

struct AppStateNvgHeart
{
    // Our NanoVG context
    NVGcontext *vg = nullptr;

    // A framebuffer, which will be used as a texture for our button
    std::unique_ptr<NvgImgui::NvgFramebuffer> nvgFramebuffer;

    void Init()
    {
        // Instantiate the NanoVG context
        vg = NvgImgui::CreateNvgContext_GL(NvgImgui::NVG_ANTIALIAS | NvgImgui::NVG_STENCIL_STROKES);

        // Create a framebuffer
        int nvgImageFlags = 0; //NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        nvgFramebuffer = std::make_unique<NvgImgui::NvgFramebuffer>(vg, 1000, 600, nvgImageFlags);
    }

    void Release()
    {
        nvgFramebuffer.reset();
        NvgImgui::DeleteNvgContext_GL(vg);
    }
};


int main(int, char**)
{
    AppStateNvgHeart appState;

    HelloImGui::RunnerParams runnerParams;

    runnerParams.callbacks.EnqueuePostInit([&]() { appState.Init(); });
    runnerParams.callbacks.EnqueueBeforeExit([&]() { appState.Release(); });

    // Render our drawing to a custom background:
    //   (we need to disable the default ImGui window, so that the background is visible)
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    // CustomBackground is where we can draw our custom background
    runnerParams.callbacks.CustomBackground = [&](){
        NvgImgui::RenderNvgToBackground(appState.vg, DrawScene);
    };


    auto gui = [&]()
    {
        ImGui::Begin("Hello, NanoVG!");

        ImGui::Text("Click on the image button below to exit");

        // Also, render our drawing to a framebuffer, and use it as a texture for an ImGui button
        // Render to our framebuffer
        NvgImgui::RenderNvgToFrameBuffer(appState.vg, *appState.nvgFramebuffer, DrawScene);
        // Use it as a texture for an ImGui button
        if (ImGui::ImageButton(appState.nvgFramebuffer->TextureId, HelloImGui::EmToVec2(5.f, 3.f)))
            HelloImGui::GetRunnerParams()->appShallExit = true;

        ImGui::End();
    };
    runnerParams.callbacks.ShowGui = gui;
    runnerParams.fpsIdling.enableIdling = false;

    HelloImGui::Run(runnerParams);
}