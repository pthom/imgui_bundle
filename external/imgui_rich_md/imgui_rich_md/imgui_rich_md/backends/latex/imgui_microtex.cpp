#include "imgui_microtex.h"
#include "internal/graphic_freetype.h"
#include "microtex.h"
#include <functional>
#include <vector>

#include <cstdlib>
#include <map>
#include <mutex>
#include <stdexcept>

namespace ImGuiMicroTeX {

static bool sInitialized = false;
static std::mutex sMutex;
static std::vector<std::function<void()>> sReleaseCallbacks;

// Convert ImU32 (0xAABBGGRR) to MicroTeX color (0xAARRGGBB)
static uint32_t ImU32ToMicroTexColor(ImU32 c) {
    uint8_t a = (c >> IM_COL32_A_SHIFT) & 0xFF;
    uint8_t r = (c >> IM_COL32_R_SHIFT) & 0xFF;
    uint8_t g = (c >> IM_COL32_G_SHIFT) & 0xFF;
    uint8_t b = (c >> IM_COL32_B_SHIFT) & 0xFF;
    return (a << 24) | (r << 16) | (g << 8) | b;
}

// Map our public TexStyle to MicroTeX's internal enum.
static microtex::TexStyle ToMicroTeXStyle(TexStyle s) {
    switch (s) {
        case TexStyle::Display:      return microtex::TexStyle::display;
        case TexStyle::Text:         return microtex::TexStyle::text;
        case TexStyle::Script:       return microtex::TexStyle::script;
        case TexStyle::ScriptScript: return microtex::TexStyle::scriptScript;
    }
    return microtex::TexStyle::text;
}

// ============================================================================
// Init / Release
// ============================================================================

// sMutex must be held
static void _InitWithFontSrc(const microtex::FontSrc& mathFont) {
    microtex::Font_freetype::initFreeType();

    microtex::PlatformFactory::registerFactory(
        "freetype",
        std::make_unique<microtex::PlatformFactory_freetype>()
    );
    microtex::PlatformFactory::activate("freetype");

    microtex::MicroTeX::init(mathFont);

    // Register the *real* MicroTeX + FreeType teardown as an atexit
    // handler on first successful init. We can't run this teardown from
    // Release() because MicroTeX cannot be re-initialized cleanly after
    // MicroTeX::release(): it half-frees its macro tables
    // (NewCommandMacro::_instance is deleted but not null'd, MacroInfo::
    // _commands stays full of dangling pointers, NewCommandMacro::_codes
    // and _replacements never clear) and leaves _config->isInited ==
    // true, so a second MicroTeX::init() silently early-returns into a
    // broken state. Deferring the real teardown to process exit lets the
    // Pyodide playground, Jupyter notebooks, and desktop REPLs call
    // immapp.run() multiple times safely, while still giving leak
    // checkers a clean shutdown path on normal desktop exit. Per C++
    // standard, this atexit callback is guaranteed to run before any
    // static destructor of objects constructed before registration
    // (i.e. before all of MicroTeX's own namespace-scope statics), so
    // we don't hit the cross-TU static destruction order fiasco.
    static bool sAtexitRegistered = false;
    if (!sAtexitRegistered) {
        std::atexit([]() {
            microtex::MicroTeX::release();
            microtex::Font_freetype::releaseFreeType();
        });
        sAtexitRegistered = true;
    }

    sInitialized = true;
}

void Init(const std::string& clmFile, const std::string& fontFile) {
    std::lock_guard<std::mutex> lock(sMutex);
    if (sInitialized) return;
    microtex::FontSrcFile mathFont(clmFile, fontFile);
    _InitWithFontSrc(mathFont);
}

void InitFromMemory(const std::vector<uint8_t>& clmData, const std::vector<uint8_t>& fontData) {
    std::lock_guard<std::mutex> lock(sMutex);
    if (sInitialized) return;
    static const char* kFontName = "memory://math-font.otf";
    microtex::Font_freetype::registerMemoryFont(kFontName, fontData);
    static std::vector<uint8_t> sClmData;  // MicroTeX keeps the pointer: the bytes stay alive
    sClmData = clmData;
    microtex::FontSrcData mathFont(sClmData.size(), sClmData.data(), kFontName);
    _InitWithFontSrc(mathFont);
}

bool IsInitialized() {
    return sInitialized;
}

void Release() {
    std::lock_guard<std::mutex> lock(sMutex);
    if (!sInitialized) return;
    // The hosts drop their cached textures (see AddReleaseCallback): this must happen while the
    // rendering backend is still alive, which is why Release() runs before the app exits.
    //
    // Note: we intentionally do NOT tear down MicroTeX or FreeType here.
    // The real teardown is deferred to a std::atexit() handler installed
    // on first Init() (see Init() for the rationale). This lets pyodide
    // playgrounds, jupyter notebooks, and desktop Python REPLs call
    // immapp.run() multiple times per process without tripping the
    // MicroTeX init-after-release bug. sInitialized stays true on
    // purpose so subsequent Init() calls correctly no-op.
    for (auto& callback : sReleaseCallbacks)
        callback();
}

void AddReleaseCallback(std::function<void()> callback) {
    std::lock_guard<std::mutex> lock(sMutex);
    sReleaseCallbacks.push_back(std::move(callback));
}

// ============================================================================
// Level 1: LaTeX -> RGBA pixel buffer
// ============================================================================

RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color, TexStyle style) {
    std::lock_guard<std::mutex> lock(sMutex);
    if (!sInitialized) {
        throw std::runtime_error("ImGuiMicroTeX::Render called before Init()");
    }

    uint32_t mtColor = ImU32ToMicroTexColor(color);

    auto* mtRender = microtex::MicroTeX::parse(
        latex,
        0,             // unlimited width
        fontSize,
        fontSize / 3.f,
        mtColor,
        true,          // fillWidth (default)
        {true, ToMicroTeXStyle(style)}  // overrideTeXStyle: force the caller's style
    );

    int w = mtRender->getWidth();
    int h = mtRender->getHeight();        // total = ascent + depth (unpadded)
    int depth = mtRender->getDepth();     // descent below baseline (unpadded)
    int ascent = h - depth;               // pixels above baseline (unpadded)

    // Padding around the formula so antialiased edges are not clipped.
    int pad = 2;
    int imgW = w + 2 * pad;
    int imgH = h + 2 * pad;

    Internal::PixelBuffer buf(imgW, imgH);
    microtex::Graphics2D_freetype g2(buf);
    mtRender->draw(g2, pad, pad);

    delete mtRender;

    RenderedFormula result;
    result.Pixels = std::move(buf.pixels);
    result.Width = imgW;
    result.Height = imgH;
    result.Depth = depth;
    // Baseline-from-top in the padded image: top-pad + ascent.
    result.BaselineY = pad + ascent;
    return result;
}

RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color, TexStyle style) {
    return Render(latex, fontSize, ImGui::ColorConvertFloat4ToU32(color), style);
}

} // namespace ImGuiMicroTeX
