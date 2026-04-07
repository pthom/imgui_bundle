// dev_screenshot.h — header-only helper to programmatically capture
// a screenshot of an ImGui Bundle GUI for visual validation.
//
// Drop a temporary .cpp file into bindings/imgui_bundle/demos_cpp/sandbox/
// that includes this header and calls DevScreenshot::RunAndSave(). The
// existing `ibd_add_this_folder_auto_demos` glob in that directory's
// CMakeLists.txt will discover the file on the next `cmake .` reconfigure
// and build it as a target named after the file (without the .cpp suffix).
//
// Example:
//
//     // bindings/imgui_bundle/demos_cpp/sandbox/sandbox_shoot_xxx.cpp
//     #include "dev_screenshot.h"
//     #include "imgui_md_wrapper/imgui_md_wrapper.h"
//
//     int main()
//     {
//         DevScreenshot::Options opts;
//         opts.outputPath = "/tmp/out.png";
//         opts.windowSize = ImVec2(900, 950);
//         opts.withLatex  = true;
//
//         return DevScreenshot::RunAndSave(
//             [](){ ImGuiMd::Render("Inline math: $E = mc^2$"); },
//             opts
//         ) ? 0 : 1;
//     }
//
// Then:
//
//     cmake builds/claude_python_bindings   # rediscover sandbox files
//     cmake --build builds/claude_python_bindings --target sandbox_shoot_xxx
//     ./builds/.../sandbox_shoot_xxx[.app/...]
//
// See ci_scripts/dev_tools/README.md for the full story and the Python
// equivalent (`dev_screenshot.py::take_screenshot`).
#pragma once

#include <cstdio>
#include <cstring>
#include <functional>
#include <string>

#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/hello_imgui_screenshot.h"
#include "immapp/immapp.h"

// stbi_write_png is implemented inside HelloImGui (via stb_impl_hello_imgui.cpp
// + the HELLOIMGUI_STB_IMAGE_WRITE_IMPLEMENTATION compile flag). We just
// forward-declare the C symbol so we don't need stb_image_write.h on our
// include path.
extern "C" int stbi_write_png(
    const char* filename, int w, int h, int comp, const void* data, int stride_in_bytes);

namespace DevScreenshot
{

struct Options
{
    // Where to save the PNG. Parent directories must already exist.
    std::string outputPath = "/tmp/dev_screenshot.png";

    // Number of frames to render before exiting (default 8). Increase
    // if your layout takes longer to settle (e.g. async asset loads).
    int exitAfterFrames = 8;

    // Logical pixel size of the app window. On HiDPI displays the captured
    // framebuffer is larger by the framebuffer scale factor.
    ImVec2 windowSize = ImVec2(900, 950);

    // Window title (cosmetic — only briefly visible during capture).
    std::string windowTitle = "DevScreenshot probe";

    // Disable the auto-saved imgui .ini file. Avoids leaving artifacts on
    // disk and prevents window-state drift across repeated screenshot runs.
    bool iniDisable = true;

    // Standard ImmApp addons. Enable as needed by the demo being captured.
    // withLatex implies withMarkdown.
    bool withMarkdown = false;
    bool withLatex = false;
    bool withImplot = false;
    bool withImplot3d = false;
    bool withNodeEditor = false;
};

// Run guiFn for `opts.exitAfterFrames` frames, exit, save the final
// framebuffer to opts.outputPath as PNG. Returns true on success.
//
// On failure, prints a message to stderr and returns false. Reasons:
//   - the framebuffer was empty (app exited before any frame rendered)
//   - stbi_write_png failed to write the file (bad path / no permissions)
inline bool RunAndSave(std::function<void()> guiFn, const Options& opts = Options())
{
    HelloImGui::SimpleRunnerParams simple;
    simple.windowTitle = opts.windowTitle;
    simple.windowSize = {(int)opts.windowSize.x, (int)opts.windowSize.y};
    simple.iniDisable = opts.iniDisable;
    simple.fpsIdle = 0.0f;  // render as fast as possible — we only need a few frames

    int frameCount = 0;
    simple.guiFunction = [guiFn, &frameCount, &opts]() {
        guiFn();
        ++frameCount;
        if (frameCount >= opts.exitAfterFrames)
            HelloImGui::GetRunnerParams()->appShallExit = true;
    };

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = opts.withMarkdown;
    addons.withLatex = opts.withLatex;     // implies withMarkdown
    addons.withImplot = opts.withImplot;
    addons.withImplot3d = opts.withImplot3d;
    addons.withNodeEditor = opts.withNodeEditor;

    ImmApp::Run(simple, addons);

    HelloImGui::ImageBuffer img = HelloImGui::FinalAppWindowScreenshotRgbBuffer();
    if (img.bufferRgb.empty() || img.width == 0 || img.height == 0)
    {
        std::fprintf(stderr,
            "DevScreenshot::RunAndSave: final framebuffer is empty "
            "(width=%zu height=%zu). Did the app exit before any frame "
            "was rendered? (exitAfterFrames=%d)\n",
            img.width, img.height, opts.exitAfterFrames);
        return false;
    }

    int stride = (int)img.width * 3;
    int rc = stbi_write_png(
        opts.outputPath.c_str(),
        (int)img.width, (int)img.height, 3,
        img.bufferRgb.data(), stride);

    if (rc == 0)
    {
        std::fprintf(stderr,
            "DevScreenshot::RunAndSave: stbi_write_png failed for path '%s'\n",
            opts.outputPath.c_str());
        return false;
    }

    std::fprintf(stdout,
        "DevScreenshot::RunAndSave: saved %zux%zu PNG to %s\n",
        img.width, img.height, opts.outputPath.c_str());
    return true;
}

}  // namespace DevScreenshot
