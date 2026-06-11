// immapp/testing.h — helpers for driving an ImmApp GUI under the
// ImGui Test Engine, and for one-shot screenshot capture.
//
// Two helpers:
//   ImmApp::Testing::Capture(ctx, path, {window, flags})
//       Write a PNG from inside a test function (TestContext*).
//   ImmApp::Testing::CaptureFinalFrame(guiFn, path, opts)
//       Run a GUI for a few frames then save the final framebuffer.
//
// No Run() sugar on the C++ side: writing test-engine boilerplate in
// C++ is already concise (RunnerParams + use_imgui_test_engine = true +
// register_tests + QueueTest + app_shall_exit). Add those 5 lines
// inline in your app; use Capture() for the non-obvious 4-step
// screenshot sequence and CaptureFinalFrame() for the one-shot case.
#pragma once

#include <cstdio>
#include <functional>
#include <string>

#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/hello_imgui_screenshot.h"
#include "immapp/immapp.h"

#ifdef IMGUI_ENABLE_TEST_ENGINE
#include "imgui_test_engine/imgui_te_context.h"
#endif

// stbi_write_png is implemented inside HelloImGui (via stb_impl_hello_imgui.cpp
// + HELLOIMGUI_STB_IMAGE_WRITE_IMPLEMENTATION). Forward-declare the C symbol
// so we don't need stb_image_write.h on the include path.
extern "C" int stbi_write_png(
    const char* filename, int w, int h, int comp, const void* data, int stride_in_bytes);


namespace ImmApp
{
namespace Testing
{

#ifdef IMGUI_ENABLE_TEST_ENGINE

struct CaptureOptions
{
    // If empty, capture the full application framebuffer.
    // Otherwise capture a single window. A bare label (e.g. "Dear ImGui
    // Demo") is interpreted as an absolute root reference (prefixed
    // with "//" automatically).
    std::string window = "";

    // ImGuiCaptureFlags bitfield.
    int flags = 0;
};


// Write a PNG from inside a test function.
// Yields one frame first so pending animation/layout has a chance to
// settle before the capture.
inline void Capture(ImGuiTestContext* ctx, const std::string& path,
                    const CaptureOptions& opts = {})
{
    ctx->Yield();
    ctx->CaptureReset();
    if (!opts.window.empty())
    {
        const std::string ref =
            (opts.window.rfind("//", 0) == 0) ? opts.window : "//" + opts.window;
        ctx->CaptureAddWindow(ref.c_str());
    }
    if (ctx->CaptureArgs != nullptr)
        ImStrncpy(ctx->CaptureArgs->InOutputFile, path.c_str(), IM_ARRAYSIZE(ctx->CaptureArgs->InOutputFile));
    ctx->CaptureScreenshot(opts.flags);
}

#endif  // IMGUI_ENABLE_TEST_ENGINE


struct CaptureFinalFrameOptions
{
    // Number of frames to render before exiting (default 8). Increase
    // if your layout takes longer to settle (e.g. async asset loads).
    int exitAfterFrames = 8;

    // Logical pixel size of the app window. On HiDPI displays the
    // captured framebuffer is larger by the framebuffer scale factor.
    ImVec2 windowSize = ImVec2(900, 950);

    std::string windowTitle = "capture_final_frame";

    // Disable imgui.ini to avoid side effects and window-state drift.
    bool iniDisable = true;

    // Standard ImmApp addons. withLatex implies withMarkdown.
    bool withMarkdown = false;
    bool withLatex = false;
    bool withImplot = false;
    bool withImplot3d = false;
    bool withNodeEditor = false;
};


// Run guiFn for opts.exitAfterFrames frames, exit, save the final
// framebuffer to path as PNG. Returns true on success.
// On failure prints to stderr and returns false (empty framebuffer, or
// stbi_write_png failure).
inline bool CaptureFinalFrame(std::function<void()> guiFn,
                              const std::string& path,
                              const CaptureFinalFrameOptions& opts = {})
{
    HelloImGui::SimpleRunnerParams simple;
    simple.windowTitle = opts.windowTitle;
    simple.windowSize = {(int)opts.windowSize.x, (int)opts.windowSize.y};
    simple.iniDisable = opts.iniDisable;
    simple.fpsIdle = 0.0f;

    int frameCount = 0;
    simple.guiFunction = [guiFn, &frameCount, &opts]() {
        guiFn();
        ++frameCount;
        if (frameCount >= opts.exitAfterFrames)
            HelloImGui::GetRunnerParams()->appShallExit = true;
    };

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = opts.withMarkdown;
    addons.withLatex = opts.withLatex;
    addons.withImplot = opts.withImplot;
    addons.withImplot3d = opts.withImplot3d;
    addons.withNodeEditor = opts.withNodeEditor;

    ImmApp::Run(simple, addons);

    HelloImGui::ImageBuffer img = HelloImGui::FinalAppWindowScreenshotRgbBuffer();
    if (img.bufferRgb.empty() || img.width == 0 || img.height == 0)
    {
        std::fprintf(stderr,
            "ImmApp::Testing::CaptureFinalFrame: empty framebuffer "
            "(exitAfterFrames=%d)\n", opts.exitAfterFrames);
        return false;
    }

    int stride = (int)img.width * 3;
    int rc = stbi_write_png(path.c_str(),
                            (int)img.width, (int)img.height, 3,
                            img.bufferRgb.data(), stride);
    if (rc == 0)
    {
        std::fprintf(stderr,
            "ImmApp::Testing::CaptureFinalFrame: stbi_write_png failed for '%s'\n",
            path.c_str());
        return false;
    }
    return true;
}


}  // namespace Testing
}  // namespace ImmApp
