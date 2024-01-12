#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui_assets.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nanovg.h"
#include "nvg_imgui/nvg_imgui.h"

#include "nanovg_demo/nanovg_demo.h"
#include "hello_imgui/internal/functional_utils.h"

// On peut modifier CustomBackground durant l'execution

void DrawHeart(NVGcontext* vg, ImVec2 center, float size, float t) {
    float scale = sinf(t * 10) * 0.1f + 1.0f;  // Oscillating scale for the beating effect
    float scaledSize = size * scale;
    float x = center.x, y = center.y;

    // Coordinates for the top left and right curves of the heart
    float x0 = x - scaledSize / 2.0f;
    float y0 = y - scaledSize / 2.0f;
    float x1 = x + scaledSize / 2.0f;
    float y1 = y - scaledSize / 2.0f;
    float x2 = x;
    float y2 = y + scaledSize / 2.0f;

    nvgBeginPath(vg);

    // Start from bottom point of the heart
    nvgMoveTo(vg, x2, y2);

    // Draw left curve of the heart
    nvgBezierTo(vg, x2, y - scaledSize / 4.0f, x0, y0 + scaledSize / 4.0f, x0, y0);

    // Draw top left curve
    nvgBezierTo(vg, x0 - scaledSize / 4.0f, y0 - scaledSize / 4.0f, x, y0 - scaledSize / 4.0f, x, y0);

    // Draw top right curve
    nvgBezierTo(vg, x, y0 - scaledSize / 4.0f, x1 + scaledSize / 4.0f, y0 - scaledSize / 4.0f, x1, y0);

    // Draw right curve of the heart
    nvgBezierTo(vg, x1, y0 + scaledSize / 4.0f, x2, y - scaledSize / 4.0f, x2, y2);

    // Create gradient from top to bottom
    NVGpaint paint = nvgLinearGradient(vg, x, y0, x, y2, nvgRGBAf(1, 0, 0, 1), nvgRGBAf(0.8, 0, 0, 1));

    // Fill the heart with gradient
    nvgFillPaint(vg, paint);
    nvgFill(vg);

    nvgClosePath(vg);
}


void DrawTextWithGradient(NVGcontext* vg, ImVec2 position, int fontId)
{
    float fontSize = 128.0f;
    // Set the font size and face.
    nvgFontSize(vg, fontSize); // Set the font size
    nvgFontFaceId(vg, fontId); // Set the font face using the handle returned by nvgCreateFont

    // Set up the gradient
    NVGpaint textGradient = nvgLinearGradient(
        vg,
        position.x, position.y - fontSize / 2.f,
        position.x, position.y + fontSize /  2.f,
        nvgRGB(255, 0, 0), // Start color: red
        nvgRGB(0, 0, 255)  // End color: blue
    );
    //nvgFillPaint(vg, textGradient);

    nvgCircle(vg, position.x, position.y, fontSize / 2.f);

    // Draw the text with a gradient fill
    nvgTextAlign(vg, NVG_ALIGN_CENTER | NVG_ALIGN_MIDDLE);
    //nvgText(vg, textGradient); // Apply the gradient to the fill
    nvgStrokeColor(vg, nvgRGBA(255, 255, 0, 160)); // Stroke color: semi-transparent black
    nvgText(vg, position.x, position.y, "NanoVG", NULL);
    //nvgFill(vg);
    nvgStroke(vg);

    // Draw the text with a stroke
//    nvgStrokeColor(vg, nvgRGBA(0, 0, 0, 160)); // Stroke color: semi-transparent black
//    nvgStrokeWidth(vg, 2.0f); // Stroke width

    // Create gradient from top to bottom
//    NVGpaint paint = nvgLinearGradient(vg, position.x, position.y, position.x + fontSize, position.y + fontSize, nvgRGBAf(1, 0, 0, 1), nvgRGBAf(0.8, 0, 0, 1));
//    nvgFillPaint(vg, paint);

    //nvgText(vg, position.x, position.y, "NanoVG", NULL);

    //nvgFill(vg);

    //nvgStroke(vg); // Apply the stroke
}


void demo_nanovg_heart()
{
    static NvgImgui::NvgFramebufferPtr nvgFramebuffer;
    static NVGcontext *vg = nullptr;

    int fontId = 0;
    if (vg == nullptr)
    {
        vg = NvgImgui::CreateNvgContext(NvgImgui::NVG_ANTIALIAS | NvgImgui::NVG_STENCIL_STROKES);
        int nvgImageFlags = 0; //NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        nvgFramebuffer = NvgImgui::CreateNvgFramebuffer(vg, 1000, 600, nvgImageFlags);

        // Load the font. You should do this only once and store the font handle if you're calling this multiple times.
        auto fontPath = HelloImGui::AssetFileFullPath("fonts/Roboto/Roboto-Regular.ttf");
        fontId = nvgCreateFont(vg, "roboto", fontPath.c_str());
        if (fontId == -1) {
            fprintf(stderr, "Could not add font.\n");
            return; // Exit if the font cannot be added.
        }
    }
    HelloImGui::GetRunnerParams()->callbacks.CallBeforeExit([]() {
        nvgFramebuffer.reset();
        NvgImgui::DeleteNvgContext(vg);
    }
    );

    NvgImgui::RenderNvgToFrameBuffer(vg, nvgFramebuffer, [&](float width, float height)
    {
        //DrawHeart(ImmApp::NanoVGContext(), {width / 2.f, height / 2.f}, 200.f, ImGui::GetTime());
        DrawTextWithGradient(vg, {width / 2.f, height / 2.f}, fontId);
    });

    ImGui::Text("Hello, world!");
    ImGui::Image(nvgFramebuffer->TextureId, ImVec2(1000, 600));
}

//struct MyNvgDemo
//{
//    bool Blowup = false;
//    DemoData nvgDemoData;
//    NVGcontext* vg;
//
//    MyNvgDemo(NVGcontext* _vg)
//        : vg(_vg)
//    {
//        int status = loadDemoData(vg, &nvgDemoData);
//        IM_ASSERT((status == 0) && "Could not load demo data!");
//    }
//
//    ~MyNvgDemo()
//    {
//        freeDemoData(vg, &nvgDemoData);
//    }
//
//    void Render(float width, float height, int mousex, int mousey, float t)
//    {
//        renderDemo(vg, mousex, mousey, width, height, t, Blowup, &nvgDemoData);
//    }
//
//};



//struct AppState
//{
//    std::unique_ptr<MyNvgDemo> myNvgDemo;
//
//    NvgImgui::NvgFramebufferPtr myFramebuffer;
//
//    ImVec4 ClearColor = ImVec4(0.2f, 0.2f, 0.2f, 1.f);
//    bool DisplayInFrameBuffer = false;
//};



//int kkmain(int, char**)
//{
//    ChdirBesideAssetsFolder();
//
//    AppState appState;
//
//    HelloImGui::RunnerParams runnerParams;
//    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
//    runnerParams.appWindowParams.windowGeometry.size = {1200, 900};
//    ImmApp::AddOnsParams addons;
//    addons.withNanoVG = true;
//
//    runnerParams.callbacks.PostInit = [&]()
//    {
//        auto vg = ImmApp::NanoVGContext();
//        appState.myNvgDemo = std::make_unique<MyNvgDemo>(vg);
//        int nvgImageFlags = 0; //NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
//        appState.myFramebuffer = NvgImgui::CreateNvgFramebuffer(vg, 1000, 600, nvgImageFlags);
//    };
//    runnerParams.callbacks.BeforeExit = [&]()
//    {
//        appState.myNvgDemo.reset();
//        appState.myFramebuffer.reset();
//    };
//
//    auto nvgDrawingFunction = [&](float width, float height)
//    {
//        double now = ImGui::GetTime();
//        auto mousePos = ImGui::GetMousePos() - ImGui::GetMainViewport()->Pos;
//        appState.myNvgDemo->Render(width, height, (int)mousePos.x, (int)mousePos.y, (float)now);
//    };
//
//    runnerParams.callbacks.CustomBackground = [&]()
//    {
//        NvgImgui::RenderNvgToBackground(ImmApp::NanoVGContext(), nvgDrawingFunction, appState.ClearColor);
//    };
//
//    runnerParams.callbacks.ShowGui = [&]()
//    {
//        ImGui::Begin("My Window!", NULL, ImGuiWindowFlags_AlwaysAutoResize);
//        ImGui::Checkbox("Display in FrameBuffer", &appState.DisplayInFrameBuffer);
//        ImGui::Checkbox("Blowup", &appState.myNvgDemo->Blowup);
//        ImGui::SetNextItemWidth(HelloImGui::EmSize(15.f));
//        ImGui::ColorEdit4("Clear color", &appState.ClearColor.x);
//
//        if (appState.DisplayInFrameBuffer)
//        {
//            NvgImgui::RenderNvgToFrameBuffer(ImmApp::NanoVGContext(), appState.myFramebuffer, nvgDrawingFunction, appState.ClearColor);
//            ImGui::Image(appState.myFramebuffer->TextureId, ImVec2(1000, 600));
//        }
//
//        ImGui::End();
//    };
//
//    ImmApp::Run(runnerParams, addons);
//    return 0;
//}
