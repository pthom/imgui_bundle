#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui_assets.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nanovg.h"
#include "nvg_imgui/nvg_imgui.h"
#include <math.h>

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

using NvgFramebufferPtr = std::unique_ptr<NvgImgui::NvgFramebuffer>;

struct AppStateNvgHeart
{
    NVGcontext *vg = nullptr;
    std::unique_ptr<NvgImgui::NvgFramebuffer> nvgFramebuffer;
    int fontId = 0;

    void Init()
    {
        vg = NvgImgui::CreateNvgContext_GL(NvgImgui::NVG_ANTIALIAS | NvgImgui::NVG_STENCIL_STROKES);
        int nvgImageFlags = 0; //NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED;
        nvgFramebuffer = std::make_unique<NvgImgui::NvgFramebuffer>(vg, 1000, 600, nvgImageFlags);

        // Load the font. You should do this only once and store the font handle if you're calling this multiple times.
        auto fontPath = HelloImGui::AssetFileFullPath("fonts/Roboto/Roboto-Regular.ttf");
        fontId = nvgCreateFont(vg, "roboto", fontPath.c_str());
        if (fontId == -1) {
            fprintf(stderr, "Could not add font.\n");
            return; // Exit if the font cannot be added.
        }
    }

    void Release()
    {
        nvgFramebuffer.reset();
        NvgImgui::DeleteNvgContext_GL(vg);
    }
};


void demo_nanovg_heart()
{
    static AppStateNvgHeart appState;

    if (appState.vg == nullptr)
    {
        appState.Init();
        HelloImGui::GetRunnerParams()->callbacks.EnqueueBeforeExit([&]() { appState.Release(); });
    }


    NvgImgui::RenderNvgToFrameBuffer(appState.vg, *appState.nvgFramebuffer, [&](float width, float height)
    {
        //DrawHeart(ImmApp::NanoVGContext(), {width / 2.f, height / 2.f}, 200.f, ImGui::GetTime());
        DrawTextWithGradient(appState.vg, {width / 2.f, height / 2.f}, appState.fontId);
    });

    ImGui::Text("Hello, world!");
    ImGui::Image(appState.nvgFramebuffer->TextureId, ImVec2(1000, 600));
}
